# MVP Architecture Guide

This document defines what to build NOW versus what exists but waits. It reduces cognitive load through clear rules, not by deleting code.

---

## Correction Statement

The infrastructure built so far (TimestampedModel, SoftDeleteModel, managers, mixins) is sound. The issue was not over-engineering—it was documenting a future system before building the present one.

This document draws a clear line: **use these things, ignore those things, ship features**.

---

## What Simplification Means Here

Simplification does **NOT** mean:
- Deleting code
- Removing abstractions
- Collapsing apps
- Restructuring the architecture

Simplification **DOES** mean:
- Defining clear usage rules
- Reducing scope per app
- Freezing features until post-MVP
- Knowing what to ignore

---

## Core App — MVP Rules

### Stable and Allowed for MVP

| Abstraction | Use Case | Status |
|-------------|----------|--------|
| `TimestampedModel` | Base for all models | Use everywhere |
| `SoftDeleteModel` | Base for domain models | Use for all domain entities |
| `SlugMixin` | SEO-friendly URLs | Use for Course model |

### Exists but Hands-Off During MVP

| Abstraction | Why It Waits |
|-------------|--------------|
| `UUIDMixin` | Needed when exposing external APIs (not yet) |
| Custom admin mixins | Basic `ModelAdmin` is sufficient for now |
| `core/validators.py` | Don't create until a validator is needed |
| `core/exceptions.py` | Don't create until custom exceptions are needed |
| `core/constants.py` | Don't create until enums are needed |

**Rule: Do not ADD to core during MVP. Only USE what's stable.**

---

## Per-App MVP Scope

### accounts/

**What exists:** CustomUser with `age`, `phone` fields

**MVP scope:**
- Login, signup, logout
- That's it

**NOT adding:**
- Permissions system
- Groups
- Social authentication
- Email verification

**Rule:** Don't touch unless authentication is broken.

---

### profiles/

**What exists:** Nothing yet (planned)

**MVP scope:**
- `Student` model (OneToOne to CustomUser)
- `Instructor` model (OneToOne to CustomUser)
- Minimal fields only

**Fields for Student:**
```python
user = OneToOneField(CustomUser)
# Inherits: created_at, updated_at, is_deleted, deleted_at
```

**Fields for Instructor:**
```python
user = OneToOneField(CustomUser)
bio = TextField(blank=True)
# Inherits: created_at, updated_at, is_deleted, deleted_at
```

**NOT adding:**
- Expertise tags
- Profile completion percentage
- Progress statistics
- Achievements

**Rule:** Two models, minimal fields, done.

---

### courses/

**What exists:** Nothing yet (planned)

**MVP scope:**
- `Course` model (uses SlugMixin)
- `Module` model (belongs to Course)
- `Lesson` model (belongs to Module)

**Keep it simple:**
- One lesson type (no VideoLesson, TextLesson variants)
- Flat hierarchy (Course → Module → Lesson)
- No polymorphism

**Fields for Course:**
```python
title = CharField(max_length=200)
description = TextField(blank=True)
instructor = ForeignKey(Instructor)
# From SlugMixin: slug
# Inherits: created_at, updated_at, is_deleted, deleted_at
```

**Fields for Module:**
```python
course = ForeignKey(Course)
title = CharField(max_length=200)
order = PositiveIntegerField(default=0)
```

**Fields for Lesson:**
```python
module = ForeignKey(Module)
title = CharField(max_length=200)
content = TextField()
order = PositiveIntegerField(default=0)
```

**NOT adding:**
- Categories
- Difficulty levels
- Pricing
- Status workflow (draft/published)
- Prerequisites

**Rule:** One lesson type, simple hierarchy.

---

### enrollments/

**What exists:** Nothing yet (planned)

**MVP scope:**
- `Enrollment` model (Student + Course)
- Basic progress tracking (boolean per lesson)

**Fields for Enrollment:**
```python
student = ForeignKey(Student)
course = ForeignKey(Course)
enrolled_at = DateTimeField(auto_now_add=True)
```

**Fields for LessonProgress:**
```python
enrollment = ForeignKey(Enrollment)
lesson = ForeignKey(Lesson)
is_completed = BooleanField(default=False)
completed_at = DateTimeField(null=True, blank=True)
```

**NOT adding:**
- Certificates
- Completion percentage calculations
- Analytics
- Quiz scores

**Rule:** Connect user to course, track done/not-done per lesson.

---

## Why Current Setup Feels Heavy

**Honest assessment:**
- Too many planned features documented before any exist
- Infrastructure decisions made before knowing actual needs
- Mental overhead from remembering "what's planned vs what's built"
- Documentation describes a future system, not the current one

**How MVP rules reduce this:**
- Clear line: "Use these. Ignore those."
- No ambiguity about what to build next
- Django Admin + shell = sufficient testing for MVP
- No test infrastructure for unused abstractions

---

## Testing Strategy for MVP

### What to Test

- Features that users touch (models, views, admin)
- Via **Django Admin**: Create, edit, delete records
- Via **Django shell**: Query relationships, verify constraints

### What NOT to Test Yet

- Core abstractions in isolation (already stable)
- Mixins in isolation (test through real models)
- Managers in isolation (test via model queries)

### Validation Commands

```bash
# After creating models
python manage.py makemigrations
python manage.py migrate

# Verify in shell
python manage.py shell
>>> from profiles.models import Student, Instructor
>>> from courses.models import Course, Module, Lesson
>>> from enrollments.models import Enrollment
```

---

## MVP Development Rules

1. **No new mixins during MVP** — use SlugMixin where needed, nothing else
2. **No new apps during MVP** — everything fits in the 5 defined apps
3. **No new core utilities during MVP** — if it doesn't ship value, postpone
4. **Inherit from SoftDeleteModel** — it's the standard base, use it
5. **Use Django Admin as UI** — no custom views until admin is insufficient
6. **Test via shell and admin** — no pytest setup until features are stable
7. **If in doubt, defer** — ship features, not infrastructure

---

## What "Done" Looks Like for MVP

- [ ] Can create an Instructor via admin
- [ ] Can create a Course with Modules and Lessons via admin
- [ ] Can create a Student via admin
- [ ] Can enroll a Student in a Course via admin
- [ ] Can mark lessons as complete via shell
- [ ] Course has a working slug URL

**This is the finish line. Everything else is post-MVP.**

---

## App Dependency Rules (Unchanged)

```
enrollments/  →  courses/, profiles/
courses/      →  profiles/, core/
profiles/     →  accounts/, core/
accounts/     →  core/
core/         →  (nothing)
```

Lower layers never import from higher layers.
