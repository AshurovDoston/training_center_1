# Domain Modeling: Online Learning Platform

## Overview

This document explains the domain modeling approach for separating User, Student, and Instructor concepts cleanly.

---

## Current State

- `CustomUser` exists with `age` and `phone` fields (extends `AbstractUser`)
- Located in `accounts/models.py`

---

## Core Principle: Separate Identity from Role

| Concept | Question it Answers | Type |
|---------|---------------------|------|
| User | "Who are you?" | Authentication/Identity |
| Student | "What can you do?" | Domain Role |
| Instructor | "What can you do?" | Domain Role |

---

## Recommended Approach: Profile Pattern (OneToOne)

```
CustomUser (accounts app - auth only)
    ↑ OneToOne
    ├── Student (learner role + business logic)
    └── Instructor (teacher role + business logic)
```

### Model Responsibilities

**CustomUser (accounts app)**
- Purpose: Authentication and identity ONLY
- Contains: username, email, password, is_active, is_staff, age, phone
- Does NOT contain: courses, enrollments, teaching assignments

**Student (new model)**
- Purpose: Represents the "learner" role
- Contains: enrollment date, learning preferences, progress tracking
- Relationship: OneToOne → User
- Business logic: `can_enroll()`, `get_enrolled_courses()`, `calculate_progress()`

**Instructor (new model)**
- Purpose: Represents the "teacher" role
- Contains: bio, expertise, hire date, teaching credentials
- Relationship: OneToOne → User
- Business logic: `get_courses_teaching()`, `can_grade()`, `get_students()`

---

## Why NOT Alternatives

| Approach | Problem |
|----------|---------|
| Role field on User | User can only have one role, mixes auth with domain |
| `is_student`/`is_instructor` flags | Puts domain concepts in auth model |
| Multi-table inheritance | Can't be both Student AND Instructor |
| Proxy models | Can't add different fields per role |

---

## Why Profile Pattern Works

1. **Same person can be both Student AND Instructor**
2. **User model stays clean and stable** - no changes needed for new roles
3. **Each role evolves independently** - Student fields don't affect Instructor
4. **Business logic lives in domain models** - not in auth
5. **Adding new roles = adding new models** - not modifying User

---

## Usage Pattern

```python
# Clean: Domain model handles domain logic
if hasattr(user, 'student') and user.student.can_enroll(course):
    ...

# NOT: User model handles everything (anti-pattern)
if user.is_student and user.check_enrollment_eligibility(course):
    ...
```

---

## Future Models (when implementing)

Once Student and Instructor exist:
- `Course` belongs to an `Instructor` (ForeignKey)
- `Enrollment` connects `Student` to `Course` (ManyToMany through model)
- Business logic stays in domain models, not User

---

## Summary Table

| Model | Responsibility | Contains | Does NOT Contain |
|-------|---------------|----------|------------------|
| CustomUser | Identity & Auth | credentials, contact | domain roles |
| Student | Learner Role | enrollment data, progress | teaching logic |
| Instructor | Teacher Role | credentials, bio | learning logic |
