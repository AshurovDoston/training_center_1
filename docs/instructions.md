# Django Production Deployment: Mental Models and Risks

This guide explains what changes when you move Django from development (`runserver`) to production. It focuses on understanding *why* things work the way they do, not just *how* to configure them.

---

## 1. What Changes: Development vs Production

### The Development Server (`runserver`)

When you run `python manage.py runserver`, Django starts a simple, single-threaded server designed for one purpose: **convenience during development**.

What `runserver` does for you:
- Auto-reloads when you change code
- Serves static files directly (CSS, JS, images)
- Shows detailed error pages with tracebacks
- Handles one request at a time

### Why `runserver` Cannot Go to Production

**Mental model**: Think of `runserver` as a bicycle with training wheels. Perfect for learning, but you wouldn't enter a race with it.

| Limitation | Why It Matters |
|------------|----------------|
| Single-threaded | One slow request blocks everyone else |
| No security hardening | Hasn't been audited for production threats |
| Static files | Works, but inefficiently (Django processes each file request) |
| Auto-reload overhead | Constantly watching files wastes resources |
| Error pages | Detailed tracebacks are a security risk |

### The Production Stack

In production, you replace `runserver` with a layered architecture:

```
Browser Request
      ↓
[Reverse Proxy - nginx/Caddy]  ← Handles HTTPS, serves static files
      ↓
[WSGI Server - gunicorn/uWSGI] ← Runs multiple Django workers
      ↓
[Django Application]           ← Your code
```

**Mental model**: A restaurant analogy
- **nginx** = the host who greets guests, handles reservations (HTTPS), and serves drinks (static files)
- **gunicorn** = the kitchen manager who coordinates multiple chefs (workers)
- **Django** = the actual chefs cooking your food (processing requests)

Each layer does what it's best at. Django focuses purely on your application logic.

---

## 2. Critical Settings Explained

### DEBUG

**What it controls:**
- Detailed error pages with full stack traces
- Template debug information
- Some security features are relaxed

**Mental model**: `DEBUG=True` is like leaving your house with all doors open and a sign saying "Here's where I keep my valuables."

**The Risk:**

When `DEBUG=True` and an error occurs, Django shows:
- The full Python traceback
- Local variables at each stack frame
- Your settings (including database credentials)
- The SQL queries that ran

An attacker who triggers an error sees your entire internal structure.

**The Rule:**

```python
# settings.py
DEBUG = False  # ALWAYS in production
```

Your project already loads this from `.env`:
```python
DEBUG = env.bool("DEBUG", default=False)
```

**What happens when DEBUG=False:**
- Errors show a generic "Server Error (500)" page
- No internal details are exposed
- You need proper logging to debug issues

---

### ALLOWED_HOSTS

**What it prevents:** HTTP Host header attacks

**Background**: Every HTTP request includes a `Host` header telling the server which domain was requested. Django uses this header to build absolute URLs (like password reset links).

**Mental model**: `ALLOWED_HOSTS` is the bouncer at your club's door. It checks if the incoming request claims to be for a domain you actually own.

**The Risk:**

Without `ALLOWED_HOSTS`, an attacker can:

1. **Cache poisoning**: Send a request with `Host: evil.com`, causing Django to cache pages with malicious URLs
2. **Password reset poisoning**: Trigger a password reset, but the email contains `https://evil.com/reset/token` instead of your real domain
3. **Phishing setup**: Use your server to generate legitimate-looking links pointing to attacker-controlled sites

**The Rule:**

```python
# settings.py
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

Your project loads this from `.env`:
```python
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
```

Current `.env` value:
```
ALLOWED_HOSTS=localhost,127.0.0.1
```

For production, you'll add your real domain:
```
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

**Common Mistake:**

Never use `ALLOWED_HOSTS = ['*']` in production. This disables the protection entirely.

---

### SECRET_KEY

**What it protects:**
- Session cookies (keeping users logged in)
- CSRF tokens (preventing cross-site request forgery)
- Password reset tokens
- Any signed data (messages framework, signed cookies)

**Mental model**: The `SECRET_KEY` is the master key to your cryptographic castle. Every lock in the castle uses a key derived from this master key.

**The Risk:**

If your `SECRET_KEY` is leaked:

| Attack | How It Works |
|--------|--------------|
| Session forgery | Attacker creates valid session cookies, logging in as any user |
| CSRF bypass | Attacker generates valid CSRF tokens, submitting forms as victims |
| Account takeover | Attacker generates valid password reset links without email access |
| Data tampering | Any signed data can be forged |

**The Rules:**

1. **Never commit SECRET_KEY to version control**
2. **Use a long, random key** (50+ characters)
3. **Different key for each environment** (dev, staging, production)
4. **Rotate if potentially exposed**

Your project correctly loads from `.env`:
```python
SECRET_KEY = env("SECRET_KEY")
```

**Generating a secure key:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Warning**: Your current `.env` contains a key with "insecure" in it. Before going to production, generate a new random key.

---

## 3. Static Files in Production

### The Development Situation

During development with `DEBUG=True`:
- Django's `runserver` serves static files automatically
- Files come directly from `STATICFILES_DIRS` (your `static/` folder)
- No optimization, no caching headers
- This "just works" for convenience

### Why This Doesn't Work in Production

**Mental model**: Imagine a chef personally delivering each glass of water to tables. It works when there's one customer, but it's absurdly inefficient at scale.

In production:
- `DEBUG=False` disables Django's static file serving
- Django should focus on dynamic content, not file serving
- Static files need proper caching headers, compression, CDN integration

### The Production Pattern: Collect and Serve Elsewhere

**Step 1: Collect**

```bash
python manage.py collectstatic
```

This command:
- Gathers all static files from `STATICFILES_DIRS` (`static/`)
- Gathers all static files from each app's `static/` folder
- Copies everything to `STATIC_ROOT` (`staticfiles/`)

Your current configuration:
```python
STATIC_URL = "static/"           # URL prefix for static files
STATIC_ROOT = BASE_DIR / "staticfiles"  # Where collectstatic puts files
STATICFILES_DIRS = [BASE_DIR / "static"]  # Where your source files live
```

**Step 2: Serve via something else**

Options (from simplest to most robust):

| Method | Best For | Trade-offs |
|--------|----------|------------|
| WhiteNoise | Simple deployments | Easy setup, runs in Django process |
| nginx | Traditional servers | Fast, requires server config |
| CDN (CloudFront, Cloudflare) | High traffic | Fastest, adds complexity |

**Mental model**:
- `STATICFILES_DIRS` = your workshop where you create files
- `collectstatic` = a moving truck
- `STATIC_ROOT` = the warehouse where files are served from

### The Static File Flow

```
Development:
Browser → Django runserver → static/css/base.css

Production:
Browser → nginx (or WhiteNoise) → staticfiles/css/base.css
                                      ↑
                         (populated by collectstatic)
```

### Your Project's Current State

You have:
- `static/css/` with 4 CSS files (base.css, auth.css, courses.css, forms.css)
- `STATIC_ROOT` configured to `staticfiles/`
- The `staticfiles/` directory doesn't exist yet (created when you run `collectstatic`)

Before production, you'll need to:
1. Run `python manage.py collectstatic`
2. Configure nginx or add WhiteNoise to serve from `staticfiles/`

---

## Quick Reference: Production Checklist

| Setting | Development | Production |
|---------|-------------|------------|
| `DEBUG` | `True` | `False` |
| `SECRET_KEY` | Can be simple | Must be secret and random |
| `ALLOWED_HOSTS` | `['localhost']` | Your actual domain(s) |
| Static files | Served by runserver | Served by nginx/WhiteNoise/CDN |
| Server | `runserver` | gunicorn + nginx |

---

## 4. Gunicorn: Your Production WSGI Server

### What Gunicorn Is

**Gunicorn** (Green Unicorn) is a Python WSGI HTTP server that manages multiple worker processes to handle concurrent requests.

**Mental model**: If Django is a chef, gunicorn is the kitchen that provides multiple cooking stations. Instead of one chef handling everything sequentially, you now have multiple chefs (workers) cooking in parallel.

### Why Django Needs Gunicorn

| Problem with runserver | Gunicorn's Solution |
|------------------------|---------------------|
| Single process | Spawns multiple worker processes |
| Blocking requests | Each worker handles requests independently |
| No process management | Automatically restarts crashed workers |
| No graceful reload | Can reload code without dropping connections |

**Key insight**: Django doesn't manage processes or handle concurrent connections. That's not its job. Gunicorn's entire purpose is process management.

### How Gunicorn Connects to Django

Your project has a WSGI entry point at `django_project/wsgi.py`. This file exposes an `application` object that follows the WSGI specification.

**The interaction flow**:

```
1. Gunicorn starts and imports django_project.wsgi
2. Gunicorn spawns N worker processes
3. Each worker loads the Django application
4. Request arrives → Gunicorn routes to available worker
5. Worker calls application(environ, start_response)
6. Django processes request → returns response
7. Worker sends response back through Gunicorn
```

---

### Installation

```bash
pip install gunicorn
```

Add to your `requirements.txt`:
```
gunicorn==23.0.0
```

---

### Basic Usage

**Minimal command** (for your project):

```bash
gunicorn django_project.wsgi:application
```

This starts gunicorn with:
- 1 worker (default)
- Bound to `127.0.0.1:8000`
- Sync worker class

**With common options**:

```bash
gunicorn django_project.wsgi:application \
    --workers 3 \
    --bind 0.0.0.0:8000 \
    --timeout 30
```

---

### Configuration Options Explained

#### Workers (`--workers` or `-w`)

How many worker processes to spawn.

```bash
gunicorn django_project.wsgi:application --workers 3
```

**Rule of thumb**: `(2 × CPU cores) + 1`

| CPU Cores | Recommended Workers |
|-----------|---------------------|
| 1 | 3 |
| 2 | 5 |
| 4 | 9 |

**Why this formula?** One worker handles a request while others wait for I/O (database, network). The +1 ensures there's always a worker ready.

**Warning**: More workers = more memory. Each worker loads the entire Django application. Monitor your memory usage.

#### Bind Address (`--bind` or `-b`)

Where gunicorn listens for connections.

```bash
# Local only (default) - use when nginx is on same machine
gunicorn django_project.wsgi:application --bind 127.0.0.1:8000

# All interfaces - use when nginx is on different machine/container
gunicorn django_project.wsgi:application --bind 0.0.0.0:8000

# Unix socket - faster when nginx is on same machine
gunicorn django_project.wsgi:application --bind unix:/run/gunicorn.sock
```

#### Timeout (`--timeout`)

Seconds before a worker is killed for taking too long.

```bash
gunicorn django_project.wsgi:application --timeout 30
```

Default is 30 seconds. Increase for:
- File uploads
- Long-running API calls
- Report generation

**Warning**: If requests legitimately take >30s, increase this. But first ask: should this be a background task instead?

#### Access Logging (`--access-logfile`)

```bash
# Log to file
gunicorn django_project.wsgi:application --access-logfile /var/log/gunicorn/access.log

# Log to stdout (good for Docker/systemd)
gunicorn django_project.wsgi:application --access-logfile -
```

#### Error Logging (`--error-logfile`)

```bash
gunicorn django_project.wsgi:application --error-logfile /var/log/gunicorn/error.log
```

#### Daemon Mode (`--daemon`)

Run in background (not recommended - use systemd instead):

```bash
gunicorn django_project.wsgi:application --daemon
```

---

### Configuration File (Recommended)

Instead of long command lines, create `gunicorn.conf.py` in your project root:

```python
# gunicorn.conf.py

# Server socket
bind = "127.0.0.1:8000"

# Workers
workers = 3
worker_class = "sync"
timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "training_center"

# Server mechanics
daemon = False
pidfile = None
```

Then run:

```bash
gunicorn django_project.wsgi:application --config gunicorn.conf.py
```

---

### Testing Gunicorn Locally

**Step 1**: Ensure DEBUG=False in your `.env`:
```
DEBUG=False
```

**Step 2**: Collect static files (they won't work yet, but do this anyway):
```bash
python manage.py collectstatic
```

**Step 3**: Run gunicorn:
```bash
gunicorn django_project.wsgi:application --bind 127.0.0.1:8000
```

**Step 4**: Visit `http://127.0.0.1:8000`

**Expected behavior**:
- Pages load (without CSS - that's expected, we'll fix this next)
- No auto-reload when you change code
- Errors show generic 500 page, not Django debug page

---

### Common Beginner Mistakes

#### 1. Running with DEBUG=True

Gunicorn doesn't auto-reload like runserver. With DEBUG=True you get security risks but none of the convenience.

#### 2. Expecting static files to work

Gunicorn only runs Python. It won't serve your CSS/JS:

```
Browser: "GET /static/css/base.css"
Gunicorn: "I only speak Python. 404."
```

This is why we need WhiteNoise (next section).

#### 3. Wrong worker count

Too few = wasted capacity. Too many = memory exhaustion and thrashing.

#### 4. Binding to localhost when nginx is remote

```bash
gunicorn app.wsgi:application  # Binds to 127.0.0.1 only
```

If nginx is in a different container, it can't reach gunicorn. Use `--bind 0.0.0.0:8000`.

#### 5. No process manager

If you run gunicorn directly via SSH and disconnect, gunicorn dies. Use systemd, supervisor, or Docker to keep it running.

#### 6. Forgetting about timeouts

Default 30-second timeout kills long requests mid-process.

---

### Quick Reference: Gunicorn Commands

```bash
# Start (development testing)
gunicorn django_project.wsgi:application

# Start (production-like)
gunicorn django_project.wsgi:application \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --access-logfile - \
    --error-logfile -

# Start with config file
gunicorn django_project.wsgi:application --config gunicorn.conf.py

# Graceful reload (after code changes)
kill -HUP $(cat /var/run/gunicorn.pid)

# Graceful shutdown
kill -TERM $(cat /var/run/gunicorn.pid)
```

---

## 5. WhiteNoise: Static Files Without nginx

### The Problem

You've tested gunicorn and your site loads... but without CSS. The page looks broken.

```
Browser: "GET /static/css/base.css"
Gunicorn: "I only run Python code. 404."
```

**The traditional solution** is nginx sitting in front of gunicorn, serving static files directly. But this adds complexity: another service to configure, monitor, and maintain.

**WhiteNoise** is a simpler alternative for many deployments.

---

### What WhiteNoise Is

WhiteNoise is a Python package that serves static files directly from your WSGI application. It wraps around Django, intercepts requests for static files, and serves them efficiently.

**Mental model**: WhiteNoise is like hiring a dedicated assistant who stands at the kitchen door. When someone asks for water (static files), the assistant handles it directly instead of bothering the chefs (Django views).

```
Without WhiteNoise:
Browser → Gunicorn → Django → "404, I don't serve files"

With WhiteNoise:
Browser → Gunicorn → WhiteNoise → serves file directly
                  ↓ (if not static)
               Django → processes request
```

---

### When to Use WhiteNoise

| Use WhiteNoise | Use nginx Instead |
|----------------|-------------------|
| Simple deployments | High-traffic sites (>1000 req/sec) |
| Heroku, Railway, Render | You already have nginx |
| Containers without reverse proxy | Need advanced caching rules |
| Getting started with production | CDN handles static files |

**WhiteNoise is production-ready**. Companies serve millions of requests with it. For most Django projects, it's the right choice.

---

### Installation

```bash
pip install whitenoise
```

Add to `requirements.txt`:
```
whitenoise==6.7.0
```

---

### Configuration

#### Step 1: Add Middleware

In `django_project/settings.py`, add WhiteNoise to `MIDDLEWARE` immediately after `SecurityMiddleware`:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Add this line
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # ... rest of middleware
]
```

**Why after SecurityMiddleware?** Security middleware handles HTTPS redirects and security headers. Those should run first. WhiteNoise should intercept static requests before Django wastes time on them.

#### Step 2: Configure Static Settings

Your project already has the required settings:

```python
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
```

#### Step 3: Enable Compression and Caching (Recommended)

Add this to `settings.py`:

```python
# WhiteNoise configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

This enables:
- **Compression**: Serves gzipped files to browsers that support it
- **Cache-busting**: Adds hashes to filenames (`base.css` → `base.a1b2c3d4.css`)
- **Forever caching**: Files get `Cache-Control: max-age=31536000` (1 year)

**Mental model**: Cache-busting means when you change `base.css`, it becomes `base.xyz789.css`. Browsers see a "new" file and fetch it. Old cached versions are ignored because they have different names.

---

### Collect Static Files

After configuring WhiteNoise, collect your static files:

```bash
python manage.py collectstatic
```

This:
1. Copies files from `static/` to `staticfiles/`
2. Compresses them (gzip versions)
3. Generates hashed filenames
4. Creates a manifest mapping original → hashed names

You'll see output like:
```
128 static files copied to '/path/to/staticfiles'.
```

---

### Testing WhiteNoise

**Step 1**: Ensure your `.env` has:
```
DEBUG=False
```

**Step 2**: Run collectstatic:
```bash
python manage.py collectstatic --noinput
```

**Step 3**: Start gunicorn:
```bash
gunicorn django_project.wsgi:application --bind 127.0.0.1:8000
```

**Step 4**: Visit `http://127.0.0.1:8000`

**Expected behavior**:
- Pages load WITH CSS styling
- Check browser DevTools → Network tab
- Static files return 200 status
- Response headers show `Content-Encoding: gzip` (if browser supports it)

---

### How WhiteNoise Serves Files

1. **At startup**: WhiteNoise scans `STATIC_ROOT` and builds an in-memory file index
2. **On request**: Checks if URL matches a static file
3. **If match**: Serves file directly with proper headers
4. **If no match**: Passes request to Django

**Important**: WhiteNoise only serves files that exist in `STATIC_ROOT`. If you add new static files, you must run `collectstatic` again.

---

### Understanding the Manifest

When using `CompressedManifestStaticFilesStorage`, Django creates `staticfiles/staticfiles.json`:

```json
{
  "paths": {
    "css/base.css": "css/base.a1b2c3d4e5f6.css",
    "css/auth.css": "css/auth.f7g8h9i0j1k2.css"
  }
}
```

In templates, `{% static 'css/base.css' %}` becomes `/static/css/base.a1b2c3d4e5f6.css`.

**Why this matters**: You can set aggressive caching (1 year) because if the file changes, it gets a new hash, and browsers fetch the new version.

---

### Configuration Options

#### Basic (No Compression)

```python
# Just serve files, no compression or hashing
# Good for development-like production testing
STATICFILES_STORAGE = "whitenoise.storage.StaticFilesStorage"
```

#### Compressed + Manifest (Recommended)

```python
# Compression + cache-busting hashes
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

#### Django 4.2+ Alternative Syntax

```python
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

---

### Common Beginner Mistakes

#### 1. Forgetting to run collectstatic

WhiteNoise serves from `STATIC_ROOT`, not `STATICFILES_DIRS`. Without `collectstatic`, there's nothing to serve.

```bash
# Must run this after any static file changes
python manage.py collectstatic
```

#### 2. Wrong middleware order

WhiteNoise must be **after** SecurityMiddleware:

```python
# WRONG
MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Too early!
    "django.middleware.security.SecurityMiddleware",
    ...
]

# CORRECT
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Right here
    ...
]
```

#### 3. Expecting it to work with DEBUG=True

With `DEBUG=True`, Django's `runserver` serves static files directly. WhiteNoise only activates when `DEBUG=False`.

#### 4. Not adding staticfiles/ to .gitignore

The `staticfiles/` directory is generated by `collectstatic`. Don't commit it:

```gitignore
# .gitignore
staticfiles/
```

Run `collectstatic` as part of your deployment process instead.

#### 5. Missing the storage backend setting

Without `STATICFILES_STORAGE`, WhiteNoise works but without compression or cache-busting. Add the setting for full benefits.

---

### Production Deployment Flow

Every time you deploy:

```bash
# 1. Pull new code
git pull

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Collect static files (WhiteNoise needs this!)
python manage.py collectstatic --noinput

# 5. Restart gunicorn
systemctl restart gunicorn  # or however you restart
```

The `--noinput` flag skips the "are you sure?" prompt, essential for automated deployments.

---

### Quick Reference: WhiteNoise Setup

```python
# settings.py

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # <-- Add here
    # ... rest of middleware
]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Enable compression + cache-busting
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

```bash
# Commands
pip install whitenoise
python manage.py collectstatic --noinput
gunicorn django_project.wsgi:application
```

---

## 6. HTTPS: Encrypting Traffic

### Why HTTPS Matters

HTTPS isn't just about encryption. It provides three guarantees:

| Guarantee | What It Means |
|-----------|---------------|
| **Confidentiality** | Traffic can't be read by eavesdroppers |
| **Integrity** | Traffic can't be modified in transit |
| **Authentication** | You're actually talking to the real server |

**Without HTTPS:**
- Passwords sent over HTTP are visible to anyone on the network
- Session cookies can be stolen (session hijacking)
- Attackers can inject malicious content into responses
- Browsers show "Not Secure" warnings, destroying user trust

**Mental model**: HTTP is a postcard—anyone handling it can read it. HTTPS is a sealed envelope that only the recipient can open.

---

### Where HTTPS Happens

HTTPS is **not handled by Django or gunicorn**. It's handled by:

1. **A reverse proxy** (nginx, Caddy) in front of gunicorn
2. **A load balancer** (AWS ALB, Cloudflare) in front of your server
3. **A PaaS platform** (Heroku, Render, Railway) that handles it for you

```
Traditional Setup:
Browser ←──HTTPS──→ nginx ←──HTTP──→ gunicorn ←──→ Django
                     ↑
              TLS termination
              happens here

PaaS Setup:
Browser ←──HTTPS──→ Platform Load Balancer ←──HTTP──→ gunicorn ←──→ Django
                           ↑
                    TLS termination
```

**Key insight**: Gunicorn and Django communicate over plain HTTP internally. That's fine because they're on the same machine or private network. The encrypted connection is between the user's browser and your edge (nginx/load balancer).

---

### Django's HTTPS Settings

Even though Django doesn't handle TLS directly, it has settings that depend on HTTPS being present.

#### SECURE_SSL_REDIRECT

Redirects all HTTP requests to HTTPS:

```python
# settings.py
SECURE_SSL_REDIRECT = True
```

When a user visits `http://yourdomain.com`, Django responds with a redirect to `https://yourdomain.com`.

**When to use**: Always in production, unless your load balancer already handles redirects.

**When to skip**: If nginx or your PaaS already redirects HTTP→HTTPS before reaching Django.

#### SECURE_PROXY_SSL_HEADER

Tells Django how to detect HTTPS when behind a proxy:

```python
# settings.py
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

**Why this is needed**: When nginx terminates TLS, Django sees plain HTTP. But nginx adds a header `X-Forwarded-Proto: https` to tell Django "the original request was HTTPS."

Without this setting, Django thinks every request is HTTP and may:
- Generate `http://` URLs in emails
- Refuse to set secure cookies
- Infinite redirect loops with `SECURE_SSL_REDIRECT`

**Security warning**: Only set this if you trust your proxy. If an attacker can send requests directly to gunicorn (bypassing nginx), they could forge this header.

#### SESSION_COOKIE_SECURE

Only send session cookies over HTTPS:

```python
# settings.py
SESSION_COOKIE_SECURE = True
```

**What it does**: Adds the `Secure` flag to session cookies. Browsers won't send the cookie over HTTP connections.

**Risk if missing**: An attacker who tricks a user into visiting `http://yourdomain.com` (even briefly) can steal the session cookie.

#### CSRF_COOKIE_SECURE

Same as above, but for CSRF tokens:

```python
# settings.py
CSRF_COOKIE_SECURE = True
```

---

### Getting TLS Certificates

You need a certificate to enable HTTPS. Options:

#### Let's Encrypt (Free, Recommended)

Let's Encrypt provides free TLS certificates. Use **Certbot** to obtain and auto-renew them:

```bash
# Install certbot (Ubuntu/Debian)
sudo apt install certbot python3-certbot-nginx

# Get certificate and configure nginx automatically
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

Certbot:
1. Proves you control the domain
2. Downloads certificates
3. Configures nginx to use them
4. Sets up automatic renewal (certificates expire every 90 days)

#### PaaS Platforms

Most platforms handle certificates automatically:
- **Heroku**: Automatic with custom domains
- **Render**: Automatic with custom domains
- **Railway**: Automatic
- **AWS**: Use ACM (Amazon Certificate Manager) with ALB

You don't need to configure anything—just point your domain to the platform.

#### Paid Certificates

For extended validation (EV) or organization validation (OV) certificates, use providers like:
- DigiCert
- Sectigo
- GlobalSign

These show your organization name in the browser but offer no additional security over Let's Encrypt.

---

### nginx HTTPS Configuration

A basic nginx configuration with HTTPS:

```nginx
# /etc/nginx/sites-available/yourdomain.com

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # Certificates (managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    # Proxy to gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;  # Important for Django
    }

    # Static files (if not using WhiteNoise)
    location /static/ {
        alias /path/to/staticfiles/;
    }
}
```

**Key headers for Django**:
- `X-Forwarded-Proto`: Tells Django whether the original request was HTTP or HTTPS
- `X-Forwarded-For`: Original client IP (for logging, rate limiting)
- `Host`: The domain name requested

---

### Complete Django HTTPS Settings

Add these to `settings.py` for production:

```python
# Only apply in production (when DEBUG is False)
if not DEBUG:
    # HTTPS/SSL
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Secure cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

Or using environment variables (more flexible):

```python
# settings.py
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if not DEBUG else None
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)
```

```bash
# .env (production)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

### Testing HTTPS Locally

For local development, you typically don't need HTTPS. But if you must test:

#### Option 1: django-sslserver (Development Only)

```bash
pip install django-sslserver
```

```python
# settings.py
INSTALLED_APPS = [
    ...
    'sslserver',
]
```

```bash
python manage.py runsslserver
```

#### Option 2: mkcert (Local Trusted Certificates)

```bash
# Install mkcert
brew install mkcert  # macOS
mkcert -install      # Create local CA

# Create certificate for localhost
mkcert localhost 127.0.0.1
```

Use the generated certificates with nginx locally.

#### Option 3: ngrok (Tunnel with HTTPS)

```bash
ngrok http 8000
```

Provides a temporary HTTPS URL that tunnels to your local server.

---

### Common Beginner Mistakes

#### 1. Infinite redirect loops

```
Browser → nginx (HTTPS) → Django → "Redirect to HTTPS" → nginx → Django → ...
```

**Cause**: `SECURE_SSL_REDIRECT=True` but `SECURE_PROXY_SSL_HEADER` not set. Django doesn't know the request was already HTTPS.

**Fix**: Set `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`

#### 2. Mixed content warnings

Your page loads over HTTPS but includes HTTP resources:

```html
<img src="http://example.com/image.jpg">  <!-- Blocked! -->
```

**Fix**: Use protocol-relative URLs or always use HTTPS:

```html
<img src="https://example.com/image.jpg">
<img src="//example.com/image.jpg">  <!-- Uses same protocol as page -->
```

For Django static/media files, ensure `STATIC_URL` and `MEDIA_URL` don't hardcode `http://`.

#### 3. Forgetting to redirect HTTP to HTTPS

Users who type `yourdomain.com` get HTTP by default. Without a redirect, they stay on insecure HTTP.

**Fix**: Either nginx redirects (recommended) or Django's `SECURE_SSL_REDIRECT`.

#### 4. Setting SECURE_PROXY_SSL_HEADER when not behind a proxy

If attackers can reach gunicorn directly, they can forge the `X-Forwarded-Proto` header and trick Django into thinking requests are HTTPS when they're not.

**Fix**: Only set this when behind a trusted proxy. Ensure gunicorn only accepts connections from the proxy (bind to localhost or unix socket).

#### 5. Not testing with DEBUG=False

HTTPS settings often only apply when `DEBUG=False`. Test your production configuration locally:

```bash
DEBUG=False python manage.py runserver
```

---

### HTTPS Verification Checklist

After deploying with HTTPS:

1. **Visit your site** - Browser should show padlock icon
2. **Try HTTP** - Should redirect to HTTPS
3. **Check certificate** - Click padlock → verify domain and expiry
4. **Test cookies** - In DevTools, check cookies have `Secure` flag
5. **SSL Labs test** - Visit https://www.ssllabs.com/ssltest/ and enter your domain

SSL Labs grades your configuration (aim for A or A+).

---

### Quick Reference: HTTPS Settings

```python
# settings.py (production)

# Redirect HTTP to HTTPS
SECURE_SSL_REDIRECT = True

# Trust proxy header for HTTPS detection
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Secure cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

```bash
# Certbot commands
sudo certbot --nginx -d yourdomain.com    # Get certificate
sudo certbot renew --dry-run               # Test renewal
sudo certbot renew                         # Actually renew
```

---

## What's Next

Remaining production setup steps:
1. ~~Install a production WSGI server (gunicorn)~~ Done!
2. ~~Configure static file serving (WhiteNoise)~~ Done!
3. ~~Set up HTTPS~~ Done!
4. Configure logging (since you won't see DEBUG error pages)
5. Add security headers (HSTS, etc.)
