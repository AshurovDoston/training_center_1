# Implementation Plan: Django `core` App

## Overview

Create a foundational `core` app for the learning platform that provides abstract base models, custom managers, mixins, and utilities. This app has **ZERO dependencies** on other apps and serves as the architectural foundation.

---

## File Structure

```
core/
├── __init__.py           # Public API exports
├── apps.py               # App configuration
├── models.py             # Abstract base models
├── managers.py           # Custom managers and querysets
├── mixins.py             # Reusable model mixins
├── admin.py              # Admin mixins for soft-deleted models
├── validators.py         # Custom field validators
├── utils.py              # Utility functions
├── constants.py          # Enums and constants
├── exceptions.py         # Custom exception classes
├── migrations/
│   └── __init__.py
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_managers.py
    └── test_mixins.py
```

---

## Core Components

### 1. TimestampedModel (Abstract Base)

**Purpose:** Automatic timestamp tracking for all models.

**Fields:**
- `created_at` - DateTimeField with `auto_now_add=True`, `db_index=True`
- `updated_at` - DateTimeField with `auto_now=True`

**Key Concepts:**
- `auto_now_add=True`: Sets timestamp ONLY on creation
- `auto_now=True`: Updates timestamp on EVERY save()
- `abstract=True`: No database table created; fields inherited by children

**Why abstract over multi-table inheritance:**
- Multi-table inheritance creates JOINs on every query
- Abstract models copy fields directly into child tables
- Critical for performance at scale

---

### 2. SoftDeleteModel (Abstract Base)

**Purpose:** Prevent permanent data loss by marking records as deleted instead of removing them.

**Inherits from:** TimestampedModel

**Fields:**
- `is_deleted` - BooleanField, default=False, `db_index=True`
- `deleted_at` - DateTimeField, null=True

**Methods:**
- `delete()` - Overridden to perform soft delete
- `hard_delete()` - Explicitly named method for permanent deletion
- `restore()` - Restore soft-deleted records

**Managers:**
- `objects` - SoftDeleteManager (excludes deleted records)
- `all_objects` - Default Manager (includes all records)

**Why soft delete:**
1. Data recovery (undo accidental deletions)
2. Audit trail (when was it deleted?)
3. Referential integrity (foreign keys remain valid)
4. Analytics (count deleted records)
5. Legal compliance (GDPR audit requirements)

---

### 3. SoftDeleteManager & SoftDeleteQuerySet

**SoftDeleteQuerySet methods:**
- `active()` - Filter to non-deleted records
- `deleted()` - Filter to deleted records only
- `soft_delete()` - Bulk soft delete
- `hard_delete()` - Bulk permanent delete
- `restore()` - Bulk restore
- `delete()` - Overridden to call soft_delete()

**SoftDeleteManager:**
- `get_queryset()` - Returns queryset filtered to `is_deleted=False`
- `with_deleted()` - Returns queryset including deleted
- `deleted_only()` - Returns only deleted records

---

### 4. Mixins

**UUIDMixin:**
- Adds `uuid` field for external-safe identification
- Prevents URL enumeration attacks
- Globally unique IDs for distributed systems

**SlugMixin:**
- Adds `slug` field for SEO-friendly URLs
- `generate_unique_slug()` helper method
- Auto-generates unique slugs from title

**OrderableMixin:**
- Adds `order` field for manual sorting
- `move_to()` method for reordering
- Default ordering by `order` field

**MetadataMixin:**
- Adds `meta_title` and `meta_description` for SEO
- Helper methods for fallback values

---

### 5. Admin Mixins

**SoftDeleteAdminMixin:**
- Shows is_deleted status in list view
- Custom actions: soft_delete, restore, hard_delete
- Removes default "Delete selected" action
- Uses `all_objects` to show deleted records

**TimestampedAdminMixin:**
- Makes timestamp fields read-only

**FullAuditAdminMixin:**
- Combines both mixins

---

### 6. Constants & Enums

Using `models.TextChoices` for type-safe enums:
- `Status` (DRAFT, PENDING_REVIEW, PUBLISHED, ARCHIVED) - Generic, reusable

**Note:** Domain-specific enums (DifficultyLevel, EnrollmentStatus, LessonType) will be defined in their respective apps (courses, enrollments) to maintain proper separation of concerns.

File size limits and pagination constants.

---

### 7. Validators

- `PhoneNumberValidator` - International phone format
- `NoHTMLValidator` - Reject HTML content (XSS prevention)
- `FileSizeValidator` - Maximum file size validation

---

### 8. Utilities

- `get_upload_path()` - UUID-prefixed, date-organized file paths
- `truncate_string()` - Smart string truncation at word boundaries
- `generate_random_string()` - Random alphanumeric strings

---

### 9. Custom Exceptions

Base `CoreException` with context dictionary, plus domain-specific:
- `NotFoundError`, `PermissionDeniedError`, `ValidationError`
- `EnrollmentError`, `CourseError`, `PaymentError`, `RateLimitError`

---

## Usage Example

```python
# courses/models.py
from django.db import models
from core import (
    SoftDeleteModel,
    UUIDMixin,
    SlugMixin,
    Status,
    DifficultyLevel,
)


class Course(UUIDMixin, SlugMixin, SoftDeleteModel):
    """
    INHERITS:
    - uuid: From UUIDMixin
    - slug: From SlugMixin
    - is_deleted, deleted_at: From SoftDeleteModel
    - created_at, updated_at: From TimestampedModel
    """

    title = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug('title')
        super().save(*args, **kwargs)
```

---

## Dependency Rule

```
┌──────────┐
│   core   │  <-- Foundation (no dependencies)
└────┬─────┘
     │
┌────▼─────┐
│ accounts │  <-- Imports only core
└────┬─────┘
     │
┌────▼─────┐
│ profiles │  <-- Imports core, accounts
└────┬─────┘
     │
   ... (higher layers)
```

**NEVER allow lower layers to import from higher layers.**

---

## Files to Modify

1. **Create:** `core/` directory with all files listed above
2. **Modify:** `django_project/settings.py` - Add `"core.apps.CoreConfig"` to INSTALLED_APPS (FIRST in the list, after Django apps)

---

## Verification

1. Run `python manage.py makemigrations core` (should create empty migration)
2. Run `python manage.py migrate`
3. Run `python manage.py test core` (all tests should pass)
4. Verify imports work: `python -c "from core import SoftDeleteModel, Status; print('OK')"`

---

## Technical Debt Prevention

1. **Single source of truth** - All common behavior in one place
2. **Consistent behavior** - Same soft delete across all models
3. **No circular imports** - Strict dependency direction enforced
4. **Index strategy built-in** - Performance baked into base models
5. **Explicit hard_delete()** - Prevents accidental data loss
6. **Type-safe enums** - IDE catches typos immediately
