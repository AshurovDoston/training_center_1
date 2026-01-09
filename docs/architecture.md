# Django Project Architecture: Large-Scale Learning Platform

## App Structure

```
training_center/
├── accounts/          # Authentication & Identity (EXISTS)
├── profiles/          # Student & Instructor roles (NEW)
├── courses/           # Course content hierarchy (NEW)
├── enrollments/       # Student-Course relationships (NEW)
├── scheduling/        # Live sessions & calendar (NEW)
├── messaging/         # Group chats & notifications (NEW)
├── core/              # Shared utilities & base classes (NEW)
└── home/              # Public pages (EXISTS)
```

---

## App Responsibilities

### 1. `accounts` (EXISTS - Keep Minimal)

**Responsibility:** Authentication and identity ONLY

**Contains:**
- `CustomUser` model (username, email, password, age, phone)
- Login/logout/signup views
- Password reset functionality

**Does NOT contain:**
- Student or Instructor logic
- Course-related permissions
- Any domain business logic

**Why separate?** The auth model is special in Django (`AUTH_USER_MODEL`). Changing it requires careful migrations. Keep it stable.

---

### 2. `profiles` (NEW)

**Responsibility:** Domain roles and user profiles

**Models:**
- `Student` (OneToOne → User) - learner role
- `Instructor` (OneToOne → User) - teacher role

**Contains:**
- Role-specific fields (bio, expertise, enrollment_date)
- Role-specific methods (can_enroll, can_teach)
- Profile completion logic

**Why separate from accounts?**
- A user can be BOTH Student and Instructor
- Domain logic belongs here, not in auth
- Roles can evolve without touching auth system

**Dependencies:** Can import from `accounts` (to reference User)

---

### 3. `courses` (NEW)

**Responsibility:** Course content hierarchy and structure

**Models:**
```
Course
├── Module (ForeignKey → Course)
│   └── Lesson (ForeignKey → Module)
│       ├── VideoLesson
│       ├── TextLesson
│       └── QuizLesson
└── Category (ManyToMany)
```

**Contains:**
- Course metadata (title, description, price, difficulty)
- Content organization (modules, lessons, ordering)
- Lesson types (video, text, quiz, assignment)
- Course status (draft, published, archived)

**Does NOT contain:**
- Enrollment logic (that's `enrollments` app)
- Scheduling logic (that's `scheduling` app)
- Student progress (that's `enrollments` app)

**Why separate?**
- Course structure is independent of who's enrolled
- Content can be managed without enrollment concerns
- Clear boundary: "What content exists" vs "Who has access"

**Dependencies:** Can import from `profiles` (Instructor as course owner)

---

### 4. `enrollments` (NEW)

**Responsibility:** Student-Course relationships and progress

**Models:**
- `Enrollment` (Student + Course + metadata)
- `LessonProgress` (tracks completion per lesson)
- `Certificate` (issued upon completion)

**Contains:**
- Enrollment status (active, completed, dropped)
- Progress tracking per lesson/module
- Completion percentage calculation
- Certificate generation

**Why separate from courses?**
- Enrollment is a relationship, not content
- Progress is student-specific, not course-specific
- Can add payment integration here without touching content

**Dependencies:**
- Imports from `profiles` (Student)
- Imports from `courses` (Course, Lesson)

---

### 5. `scheduling` (NEW)

**Responsibility:** Live sessions and calendar events

**Models:**
- `LiveSession` (linked to Course, scheduled time)
- `SessionAttendance` (Student + Session)
- `RecurringSchedule` (for weekly classes)

**Contains:**
- Session scheduling (date, time, duration)
- Zoom/Meet integration hooks
- Attendance tracking
- Reminders and notifications triggers

**Why separate?**
- Scheduling is time-based, courses are content-based
- Not all courses have live sessions
- Calendar logic is complex enough to isolate

**Dependencies:**
- Imports from `profiles` (Instructor, Student)
- Imports from `courses` (Course)
- Imports from `enrollments` (to check enrollment status)

---

### 6. `messaging` (NEW)

**Responsibility:** Communication between users

**Models:**
- `ChatGroup` (linked to Course or custom)
- `Message` (sender, group, content, timestamp)
- `Notification` (user, type, read status)

**Contains:**
- Group chat per course
- Direct messaging (optional)
- Notification system
- WebSocket consumers (for real-time)

**Why separate?**
- Messaging is cross-cutting (spans all domains)
- Real-time infrastructure is complex
- Can swap WebSocket implementation independently

**Dependencies:**
- Imports from `accounts` (User for sender/recipient)
- Imports from `courses` (Course for group context)
- Imports from `enrollments` (to verify membership)

---

### 7. `core` (NEW)

**Responsibility:** Shared utilities and base classes

**Contains:**
- Abstract base models (TimestampedModel, SoftDeleteModel)
- Common mixins (SlugMixin, OrderableMixin)
- Utility functions (file uploads, validators)
- Custom exceptions
- Constants and enums

**Does NOT contain:**
- Domain models
- Views or URLs
- Business logic

**Why exists?**
- Avoids circular imports between apps
- DRY for common patterns
- Every app can safely import from `core`

**Dependencies:** None (this is the foundation)

---

## Dependency Graph

```
                    ┌──────────┐
                    │   core   │  ← Foundation (no dependencies)
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │ accounts │  ← Auth only
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │ profiles │  ← Domain roles
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │ courses  │  ← Content
                    └────┬─────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │enrollments│   │scheduling │   │ messaging │
    └──────────┘   └───────────┘   └───────────┘
```

**Rules:**
1. `core` → imports nothing (base layer)
2. `accounts` → imports only `core`
3. `profiles` → imports `core`, `accounts`
4. `courses` → imports `core`, `profiles`
5. `enrollments` → imports `core`, `profiles`, `courses`
6. `scheduling` → imports `core`, `profiles`, `courses`, `enrollments`
7. `messaging` → imports `core`, `accounts`, `courses`, `enrollments`

**NEVER allow:**
- `accounts` importing from `profiles` (circular)
- `courses` importing from `enrollments` (circular)
- Lower layers importing from higher layers

---

## Common Architectural Mistakes to Avoid

### 1. Fat User Model
**Mistake:** Adding `is_student`, `courses_enrolled`, `courses_teaching` to User
**Why bad:** User model becomes a god object; every change requires auth migration
**Solution:** Use profile pattern (Student, Instructor as separate models)

### 2. Circular Dependencies
**Mistake:** Course imports from Enrollment, Enrollment imports from Course
**Why bad:** Import errors, tangled code, hard to test
**Solution:** Strict dependency direction; use signals or callbacks for reverse flow

### 3. Business Logic in Views
**Mistake:** Enrollment logic in `views.py` instead of model/service
**Why bad:** Can't reuse, hard to test, duplicated across views
**Solution:** Model methods or service layer (`enrollments/services.py`)

### 4. God Apps
**Mistake:** Single `courses` app with Course, Enrollment, Progress, Schedule, Chat
**Why bad:** 2000+ line models.py, unclear boundaries, merge conflicts
**Solution:** Split by domain concern (content vs relationships vs time vs communication)

### 5. Premature Abstraction
**Mistake:** Creating `BaseContent`, `ContentType`, `GenericRelation` for everything
**Why bad:** Complexity without benefit; hard to query; poor performance
**Solution:** Start concrete, abstract only when you have 3+ similar patterns

### 6. Missing Indexes
**Mistake:** No database indexes on frequently queried fields
**Why bad:** Slow queries as data grows (especially on ForeignKey lookups)
**Solution:** Add `db_index=True` on fields used in filters/ordering

### 7. Ignoring Soft Delete
**Mistake:** Using `Model.objects.delete()` for everything
**Why bad:** Lose audit trail; break foreign keys; can't recover
**Solution:** `SoftDeleteModel` in `core` with `is_deleted` flag

### 8. Synchronous Everything
**Mistake:** Sending emails, processing videos in request/response cycle
**Why bad:** Slow responses; timeouts; poor UX
**Solution:** Use Celery for async tasks (especially in `messaging`, `scheduling`)

---

## Implementation Order

1. **Phase 1:** `core` → `profiles` (foundation + roles)
2. **Phase 2:** `courses` (content hierarchy)
3. **Phase 3:** `enrollments` (student-course relationships)
4. **Phase 4:** `scheduling` (live sessions)
5. **Phase 5:** `messaging` (group chats)
