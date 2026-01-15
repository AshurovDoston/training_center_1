# Next Development Steps

## Current Progress

**Phase:** Phase 1 (Core + Profiles)
**Core App:** 40% complete
**Next Milestone:** Complete core app, then create profiles app

---

## Checklist

### Core App Completion

- [ ] **1. Add public API exports to core/__init__.py**
  - Objective: Enable clean imports like `from core import SoftDeleteModel`
  - Files: `core/__init__.py`
  - Complexity: S
  - Validation: `python -c "from core import SoftDeleteModel, TimestampedModel; print('OK')"`
  - Notes: Export all public classes from models.py and managers.py

- [ ] **2. Add Status enum to core/constants.py**
  - Objective: Type-safe status choices for all models
  - Files: `core/constants.py` (new)
  - Complexity: S
  - Validation: `python -c "from core.constants import Status; print(Status.DRAFT)"`
  - Notes: DRAFT, PENDING_REVIEW, PUBLISHED, ARCHIVED

- [ ] **3. Add UUIDMixin and SlugMixin to core/mixins.py**
  - Objective: Reusable mixins for external IDs and SEO URLs
  - Files: `core/mixins.py` (new)
  - Complexity: M
  - Validation: Create test model inheriting mixins, verify fields exist
  - Notes: UUIDMixin adds `uuid` field, SlugMixin adds `slug` with auto-generation

- [ ] **4. Add SoftDeleteAdminMixin to core/admin.py**
  - Objective: Admin interface that respects soft delete
  - Files: `core/admin.py`
  - Complexity: M
  - Validation: Register a test model, verify soft delete in admin
  - Notes: Custom actions for soft_delete, restore, hard_delete

- [ ] **5. Add core app tests**
  - Objective: Test coverage for base models and managers
  - Files: `core/tests/test_models.py`, `core/tests/test_managers.py`
  - Complexity: M
  - Validation: `python manage.py test core`
  - Notes: Test soft delete, restore, hard_delete, managers filtering

### Profiles App (Phase 1)

- [ ] **6. Create profiles app**
  - Objective: Domain roles for Student and Instructor
  - Files: `profiles/` (new app)
  - Complexity: L
  - Validation: `python manage.py makemigrations profiles && python manage.py migrate`
  - Notes: Student and Instructor models with OneToOne to User

- [ ] **7. Add Student model**
  - Objective: Learner role with enrollment-related fields
  - Files: `profiles/models.py`
  - Complexity: M
  - Validation: Create student via shell, verify relationship to user
  - Notes: Inherits from SoftDeleteModel, OneToOne to CustomUser

- [ ] **8. Add Instructor model**
  - Objective: Teacher role with course-related fields
  - Files: `profiles/models.py`
  - Complexity: M
  - Validation: Create instructor via shell, verify relationship to user
  - Notes: bio, expertise, hire_date fields

- [ ] **9. Add profiles admin**
  - Objective: Admin interface for Student/Instructor
  - Files: `profiles/admin.py`
  - Complexity: S
  - Validation: Access admin, verify CRUD operations
  - Notes: Use SoftDeleteAdminMixin

- [ ] **10. Add profiles tests**
  - Objective: Test coverage for profile models
  - Files: `profiles/tests.py`
  - Complexity: M
  - Validation: `python manage.py test profiles`
  - Notes: Test creation, soft delete, relationship to user

---

## Completed Items

(Items will be moved here when done)

---

## Notes

- Always run `black .` before committing
- Follow dependency rules: profiles can import from core and accounts only
- All domain models should inherit from SoftDeleteModel
- When completing items, move them to "Completed Items" section with date
