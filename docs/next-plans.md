# Next Development Steps

## Current Progress

**Phase:** Phase 2 (Enrollment Flow & Dashboards)
**Overall:** ~80% complete
**Next Milestone:** Enrollment views and student dashboard

---

## Checklist

### Phase 2A: Enrollment Flow (High Priority)

- [ ] **1. Enrollment views**
  - Objective: Allow students to enroll in courses
  - Files: `enrollments/views.py`, `enrollments/urls.py`
  - Complexity: M
  - Validation: Student can click "Enroll" on course page and see course in their dashboard
  - Notes: Requires login, creates Enrollment record, redirect to course detail

- [ ] **2. Progress tracking views**
  - Objective: Mark lessons as complete and track progress
  - Files: `enrollments/views.py`, update `courses/templates/lesson_detail.html`
  - Complexity: M
  - Validation: Student can mark lesson complete, progress percentage updates
  - Notes: AJAX endpoint preferred, updates LessonProgress model

- [ ] **3. Student dashboard**
  - Objective: View enrolled courses and progress
  - Files: `profiles/views.py`, `profiles/urls.py`, `templates/profiles/student_dashboard.html`
  - Complexity: L
  - Validation: Student sees all enrollments with progress bars
  - Notes: Filter by active enrollments, show completion percentage

- [ ] **4. Unenroll functionality**
  - Objective: Allow students to drop courses
  - Files: `enrollments/views.py`
  - Complexity: S
  - Validation: Student can unenroll, record soft-deleted
  - Notes: Confirm dialog, soft delete enrollment

### Phase 2B: Instructor Features (Medium Priority)

- [ ] **5. Instructor dashboard**
  - Objective: View/manage owned courses
  - Files: `profiles/views.py`, `templates/profiles/instructor_dashboard.html`
  - Complexity: L
  - Validation: Instructor sees courses with enrollment counts
  - Notes: List courses, show student counts, link to course management

- [ ] **6. Course management views**
  - Objective: CRUD for courses beyond admin
  - Files: `courses/views.py`, `courses/forms.py`, templates
  - Complexity: L
  - Validation: Instructor can create/edit/delete courses via UI
  - Notes: FormView for create/edit, only owner can modify

- [ ] **7. Student list view**
  - Objective: Instructors see enrolled students per course
  - Files: `courses/views.py`, templates
  - Complexity: M
  - Validation: Instructor sees list of students with progress
  - Notes: Accessible from instructor dashboard

### Phase 3: Polish (Lower Priority)

- [ ] **8. Core API exports**
  - Objective: Clean imports like `from core import SoftDeleteModel`
  - Files: `core/__init__.py`
  - Complexity: S
  - Validation: `python -c "from core import SoftDeleteModel; print('OK')"`

- [ ] **9. Status enum**
  - Objective: Type-safe status choices (DRAFT, PUBLISHED, etc.)
  - Files: `core/constants.py` (new)
  - Complexity: S
  - Notes: For future course publishing workflow

- [ ] **10. SoftDeleteAdminMixin**
  - Objective: Reusable admin mixin for soft delete actions
  - Files: `core/admin.py`
  - Complexity: M
  - Notes: Actions for soft_delete, restore, hard_delete

- [ ] **11. Comprehensive test coverage**
  - Objective: Test all apps
  - Files: `*/tests.py` or `*/tests/`
  - Complexity: L
  - Notes: Prioritize core and enrollments apps

---

## Completed Items

### Phase 1: Core + Foundation (Completed 2026-02-03)

- [x] **Core app models** - TimestampedModel, SoftDeleteModel with managers
- [x] **Core mixins** - UUIDMixin, SlugMixin in `core/mixins.py`
- [x] **Core managers** - SoftDeleteQuerySet, SoftDeleteManager, AllObjectsManager

### Phase 1: Profiles (Completed 2026-02-03)

- [x] **Create profiles app** - App created with migrations
- [x] **Student model** - OneToOne to CustomUser, inherits SoftDeleteModel
- [x] **Instructor model** - OneToOne to CustomUser, bio field, SoftDeleteModel
- [x] **Profiles admin** - Admin configurations for Student/Instructor

### Phase 1: Courses (Completed 2026-02-03)

- [x] **Course model** - SlugMixin, FK to Instructor, with managers
- [x] **Module model** - FK to Course, ordering, with managers
- [x] **Lesson model** - FK to Module, ordering, content field
- [x] **Course managers** - with_full_counts(), with_lessons_count() annotations
- [x] **Course views** - course_list, course_detail, LessonDetailView
- [x] **Course URLs** - /courses/, /courses/<slug>/, /courses/<slug>/lessons/<id>/
- [x] **Course admin** - Inlines for modules/lessons, search, filters
- [x] **Course templates** - course_list.html, course_detail.html, lesson_detail.html

### Phase 1: Enrollments Models (Completed 2026-02-03)

- [x] **Enrollment model** - FK to Student/Course, unique constraint
- [x] **LessonProgress model** - FK to Enrollment/Lesson, completion tracking
- [x] **Enrollments admin** - Progress display, inline lesson progress

### Phase 1: Home & Auth (Completed 2026-02-03)

- [x] **Home app** - Landing page with hero, about, CTA sections
- [x] **Base template** - Header, nav, footer
- [x] **CustomUser** - Extended AbstractUser with age/phone
- [x] **Signup view** - Registration with custom form
- [x] **Auth admin** - CustomUserAdmin configuration

---

## Architecture Reference

```
┌──────────┐
│   core   │  ← Foundation (no dependencies) ✓
└────┬─────┘
     │
┌────▼─────┐
│ accounts │  ← Auth only (CustomUser) ✓
└────┬─────┘
     │
┌────▼─────┐
│ profiles │  ← Domain roles (Student, Instructor) ✓
└────┬─────┘
     │
┌────▼─────┐
│ courses  │  ← Content hierarchy ✓
└────┬─────┘
     │
┌────▼─────┐
│enrollments│ ← Enrollment & Progress (models ✓, views pending)
└──────────┘
```

---

## Notes

- Always run `black .` before committing
- Follow dependency rules: lower layers never import from higher layers
- All domain models inherit from SoftDeleteModel
- When completing items, move them to "Completed Items" section with date
