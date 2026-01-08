# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django 6.0 training center web application using Python 3.13.

## Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run development server
python manage.py runserver

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Run tests
python manage.py test

# Run a single test file
python manage.py test home.tests

# Format code with black
black .
```

## Architecture

- **django_project/**: Main Django project configuration (settings, root URLs, WSGI/ASGI)
- **home/**: Homepage app with basic views
- **accounts/**: User authentication app (uses Django's built-in auth URLs at `/accounts/`)
- **templates/**: Global templates directory with `home.html` and `registration/` for auth templates

## Configuration

- Environment variables loaded via `django-environ` from `.env` file
- `DEBUG` and `ALLOWED_HOSTS` configured via environment
- SQLite database (`db.sqlite3`)
- Templates directory at project root level
