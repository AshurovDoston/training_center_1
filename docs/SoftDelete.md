# Implementation Plan: SoftDeleteManager & SoftDeleteQuerySet

## Overview

Implement custom Manager and QuerySet classes that make soft delete transparent to the application. The default manager will automatically exclude deleted records, while providing escape hatches for accessing all data.

---

## Files to Modify

1. **`core/managers.py`** - Create new file with SoftDeleteQuerySet and SoftDeleteManager
2. **`core/models.py`** - Update SoftDeleteModel to use the new managers

---

## Django ORM Internals: Deep Dive

### The Manager-QuerySet Relationship

```
┌─────────────────────────────────────────────────────────────────┐
│                        Model Class                               │
│  class Course(models.Model):                                    │
│      objects = Manager()  ← Entry point for all queries         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Manager                                  │
│  - Attached to Model class (not instances)                      │
│  - Creates and returns QuerySets                                │
│  - get_queryset() is the factory method                         │
│  - Can filter what records are "visible" by default             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        QuerySet                                  │
│  - Represents a database query (lazy, not executed yet)         │
│  - Chainable: .filter().exclude().order_by() returns QuerySet   │
│  - Iterable: triggers SQL execution when you loop/list()        │
│  - Has bulk operations: delete(), update()                      │
└─────────────────────────────────────────────────────────────────┘
```

### Why Are Manager and QuerySet Separated?

**1. Single Responsibility Principle:**
```python
# Manager's job: Be the entry point, configure default behavior
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

# QuerySet's job: Build queries, provide chainable operations
class SoftDeleteQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)
    def soft_delete(self):
        return self.update(is_deleted=True, deleted_at=timezone.now())
```

**2. Chainability Problem:**

Without a custom QuerySet, you lose custom methods after chaining:
```python
# BROKEN: Custom method on Manager only
class BadManager(models.Manager):
    def active(self):
        return self.filter(is_deleted=False)

Course.objects.active()                    # Works
Course.objects.filter(status="draft").active()  # AttributeError! filter() returns QuerySet, not Manager
```

With custom QuerySet + `as_manager()` or `from_queryset()`:
```python
# WORKS: Custom method on QuerySet
class GoodQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

Course.objects.active()                    # Works
Course.objects.filter(status="draft").active()  # Works! Returns QuerySet with active()
```

**3. Reusability:**
- QuerySet methods can be reused across different Managers
- Multiple Managers can use the same QuerySet with different `get_queryset()` filters

### How `get_queryset()` Works

```python
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        # This is called EVERY time you access Model.objects
        # It's the "factory" that creates the initial QuerySet
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)
```

**Step-by-step execution:**

```python
Course.objects.filter(status="draft")
```

1. `Course.objects` → Returns the Manager instance
2. `.filter(status="draft")` → Manager doesn't have `filter()`, so Python calls `__getattr__`
3. `Manager.__getattr__("filter")` → Calls `self.get_queryset().filter`
4. `get_queryset()` → Creates `SoftDeleteQuerySet(...).filter(is_deleted=False)`
5. `.filter(status="draft")` → Chains onto the QuerySet

**The magic is in `Manager.__getattr__`:**
```python
# Simplified Django source (django/db/models/manager.py)
class Manager:
    def __getattr__(self, name):
        # Any method not on Manager gets delegated to QuerySet
        return getattr(self.get_queryset(), name)
```

This is why `Course.objects.filter()` works even though `filter()` is a QuerySet method, not a Manager method.

---

## Implementation

### `core/managers.py`

```python
from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """
    Custom QuerySet that provides soft delete operations.

    All methods return QuerySet instances, enabling method chaining:
    Course.objects.filter(status="draft").active().order_by("-created_at")
    """

    def active(self):
        """
        Filter to non-deleted records only.

        Useful when you have a QuerySet that might include deleted records
        (e.g., from all_objects) and want to filter them out.
        """
        return self.filter(is_deleted=False)

    def deleted(self):
        """
        Filter to deleted records only.

        Useful for admin interfaces showing "trash" or for cleanup tasks.
        """
        return self.filter(is_deleted=True)

    def soft_delete(self):
        """
        Bulk soft delete all records in the QuerySet.

        Returns the number of records updated.
        This is what gets called when you do QuerySet.delete().
        """
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """
        Permanently delete all records in the QuerySet.

        Explicitly named to prevent accidents. Calls Django's original delete().
        Returns tuple: (total_deleted, {model_label: count})
        """
        return super().delete()

    def restore(self):
        """
        Bulk restore all soft-deleted records in the QuerySet.

        Returns the number of records updated.
        """
        return self.update(is_deleted=False, deleted_at=None)

    def delete(self):
        """
        Override delete() to perform soft delete instead.

        This ensures bulk operations like:
            Course.objects.filter(status="draft").delete()
        perform soft delete, not hard delete.
        """
        return self.soft_delete()


class SoftDeleteManager(models.Manager):
    """
    Default manager that excludes soft-deleted records.

    This manager is assigned to `objects`, making soft delete transparent:
    Course.objects.all() returns only non-deleted courses.
    """

    def get_queryset(self):
        """
        Return a QuerySet that excludes deleted records.

        This is the "factory method" called every time you access
        Course.objects. By filtering here, all subsequent operations
        automatically exclude deleted records.
        """
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def with_deleted(self):
        """
        Return a QuerySet including deleted records.

        Useful when you need to access everything:
        Course.objects.with_deleted().filter(created_at__year=2024)
        """
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        """
        Return a QuerySet with only deleted records.

        Useful for admin "trash" views:
        Course.objects.deleted_only()
        """
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=True)


class AllObjectsManager(models.Manager):
    """
    Manager that includes all records (deleted and non-deleted).

    Assigned to `all_objects` for explicit access to everything.
    """

    def get_queryset(self):
        """
        Return an unfiltered QuerySet.

        No is_deleted filter applied - returns everything.
        """
        return SoftDeleteQuerySet(self.model, using=self._db)
```

---

## Line-by-Line Explanation

### SoftDeleteQuerySet

**Class Definition:**
```python
class SoftDeleteQuerySet(models.QuerySet):
```
- Inherits from `models.QuerySet` to get all standard QuerySet behavior
- Our custom methods become chainable with standard methods

**`active()` Method:**
```python
def active(self):
    return self.filter(is_deleted=False)
```
- Returns `self.filter(...)` which returns a new QuerySet
- This enables chaining: `.active().order_by("-created_at")`
- `self` is already a QuerySet, so we're filtering the current query

**`soft_delete()` Method:**
```python
def soft_delete(self):
    return self.update(is_deleted=True, deleted_at=timezone.now())
```
- `update()` is a bulk operation - generates single SQL UPDATE statement
- No Python-side iteration, no model `save()` calls
- **Critical**: `auto_now` fields like `updated_at` are NOT updated by `update()`
- Returns integer count of updated rows

**Why `update()` doesn't trigger `auto_now`:**
```python
# update() generates raw SQL:
UPDATE courses SET is_deleted=TRUE, deleted_at='2024-...' WHERE ...

# It bypasses Model.save(), which is where auto_now logic lives
# If you need updated_at, add it explicitly:
self.update(is_deleted=True, deleted_at=timezone.now(), updated_at=timezone.now())
```

**`hard_delete()` Method:**
```python
def hard_delete(self):
    return super().delete()
```
- `super().delete()` calls `QuerySet.delete()` from Django's base class
- This is the REAL delete that removes rows from the database
- Returns `(total_count, {"app.Model": count})` tuple

**`delete()` Override:**
```python
def delete(self):
    return self.soft_delete()
```
- Intercepts ALL bulk delete operations
- Now `Course.objects.filter(...).delete()` soft deletes
- **This is why we needed a custom QuerySet** - Manager can't intercept this

---

### SoftDeleteManager

**`get_queryset()` Method:**
```python
def get_queryset(self):
    return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)
```

**Breaking this down:**

1. **`SoftDeleteQuerySet(self.model, using=self._db)`**
   - `self.model`: The model class this manager is attached to (e.g., `Course`)
   - `using=self._db`: Which database to use (supports multi-database setups)
   - Creates an empty QuerySet bound to our model

2. **`.filter(is_deleted=False)`**
   - Immediately filters out deleted records
   - This filter is applied BEFORE any user filters
   - Result: `Course.objects.all()` already excludes deleted records

**Why filter in `get_queryset()` instead of each method?**
```python
# BAD: Repetitive, error-prone
class BadManager(models.Manager):
    def all(self):
        return super().all().filter(is_deleted=False)
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs).filter(is_deleted=False)
    # Must override EVERY method...

# GOOD: Single point of filtering
class GoodManager(models.Manager):
    def get_queryset(self):
        return QuerySet(...).filter(is_deleted=False)
    # All methods automatically use filtered QuerySet
```

**`with_deleted()` Method:**
```python
def with_deleted(self):
    return SoftDeleteQuerySet(self.model, using=self._db)
```
- Returns QuerySet WITHOUT the `is_deleted=False` filter
- Escape hatch when you need to see everything
- Note: Creates fresh QuerySet, doesn't modify `get_queryset()` result

---

### AllObjectsManager

```python
class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)
```
- No filter applied - returns everything
- Assigned to `all_objects` attribute on model
- Provides second entry point with different default behavior

---

## How Bulk Delete Behaves

### Before Our Custom QuerySet:
```python
Course.objects.filter(status="draft").delete()
# Generated SQL: DELETE FROM courses WHERE status='draft'
# Records are GONE FOREVER
```

### After Our Custom QuerySet:
```python
Course.objects.filter(status="draft").delete()
# Generated SQL: UPDATE courses SET is_deleted=TRUE, deleted_at='...' WHERE status='draft' AND is_deleted=FALSE
# Records are marked deleted, still in database
```

### The Call Chain:
```
Course.objects.filter(status="draft").delete()
       │              │                   │
       │              │                   └─ Calls SoftDeleteQuerySet.delete()
       │              │                      which calls self.soft_delete()
       │              │                      which calls self.update(...)
       │              │
       │              └─ Returns SoftDeleteQuerySet (from Manager.get_queryset())
       │                 with is_deleted=False filter already applied
       │
       └─ SoftDeleteManager instance
```

### For True Deletion:
```python
Course.objects.filter(status="draft").hard_delete()
# Generated SQL: DELETE FROM courses WHERE status='draft' AND is_deleted=FALSE
# Actually removes rows
```

---

## Updated SoftDeleteModel

```python
# In core/models.py

from core.managers import SoftDeleteManager, AllObjectsManager

class SoftDeleteModel(TimestampedModel):
    # ... existing fields ...

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True
```

**Manager Ordering Matters:**
```python
objects = SoftDeleteManager()      # First = default manager
all_objects = AllObjectsManager()  # Second = accessible but not default
```

Django uses the first defined manager as the "default" manager, which is used by:
- Admin interface
- Related object lookups (`course.lessons.all()`)
- Serialization (dumpdata/loaddata)

---

## Verification Steps

1. **Verify QuerySet methods are chainable:**
   ```bash
   python -c "
   from core.managers import SoftDeleteQuerySet
   print('active' in dir(SoftDeleteQuerySet))
   print('soft_delete' in dir(SoftDeleteQuerySet))
   "
   ```

2. **Verify Manager has correct get_queryset:**
   ```bash
   python -c "
   from core.managers import SoftDeleteManager
   print(SoftDeleteManager().get_queryset)
   "
   ```

3. **Verify delete() is overridden on QuerySet:**
   ```bash
   python -c "
   from core.managers import SoftDeleteQuerySet
   import inspect
   print('delete' in SoftDeleteQuerySet.__dict__)  # True = overridden
   "
   ```
