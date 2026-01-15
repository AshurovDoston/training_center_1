# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django 6.0 training center web application (Python 3.13) for an online learning platform.

## Commands

```bash
source .venv/bin/activate         # Activate virtual environment
python manage.py runserver        # Run development server
python manage.py makemigrations   # Create migrations
python manage.py migrate          # Apply migrations
python manage.py test             # Run all tests
python manage.py test home.tests  # Run single test file
black .                           # Format code
```

## Architecture

### App Dependency Graph

```
┌──────────┐
│   core   │  ← Foundation (no dependencies)
└────┬─────┘
     │
┌────▼─────┐
│ accounts │  ← Auth only (CustomUser)
└────┬─────┘
     │
┌────▼─────┐
│ profiles │  ← Domain roles (Student, Instructor) [PLANNED]
└────┬─────┘
     │
┌────▼─────┐
│ courses  │  ← Content hierarchy [PLANNED]
└────┬─────┘
     │
┌────┴────┐
│enrollments, scheduling, messaging│  [PLANNED]
└─────────┘
```

**Rule:** Lower layers NEVER import from higher layers.

### Core App (`core/`)

Foundation layer providing abstract base models for all domain models:

- **TimestampedModel**: Abstract base with `created_at` (indexed), `updated_at`
- **SoftDeleteModel**: Extends TimestampedModel with soft delete (`is_deleted`, `deleted_at`)
  - `objects` manager excludes deleted records by default
  - `all_objects` manager includes all records
  - `.delete()` soft deletes, `.hard_delete()` permanently removes
  - Bulk operations via QuerySet: `.soft_delete()`, `.hard_delete()`, `.restore()`

### Accounts App (`accounts/`)

Authentication only. `CustomUser` extends `AbstractUser` with `age` and `phone` fields.

**Key principle:** Auth model stays minimal. Domain roles (Student, Instructor) will be separate models with OneToOne relationships to User.

### Configuration

- Environment variables via `django-environ` from `.env`
- PostgreSQL database (requires `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)
- Custom user model: `AUTH_USER_MODEL = "accounts.CustomUser"`
- Templates at project root: `templates/`

## Domain Modeling Patterns

1. **Profile Pattern**: User ← OneToOne → Student/Instructor (same person can have multiple roles)
2. **Soft Delete**: All domain models inherit from `SoftDeleteModel`
3. **Strict Dependencies**: Apps only import from lower layers in the dependency graph
