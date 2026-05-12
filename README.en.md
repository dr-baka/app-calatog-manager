# App Catalog Manager

English | [Bahasa Indonesia](README.md)

App Catalog Manager is a Django application for documenting and monitoring an internal application catalog. It helps teams manage applications, categories, servers, application admins, update history, and environment-specific server configurations for `DEV`, `BETA`, and `PROD`.

## Main Features

- Login and logout using Django's built-in authentication.
- Manage applications, categories, and servers.
- One application can have multiple environments: `DEV`, `BETA`, and `PROD`.
- Each environment can have its own server, URL, local IP, port, active status, and deployment notes.
- Dashboard and application list show the highest available environment using the order `DEV < BETA < PROD`.
- Application detail page shows all environments owned by the application.
- Online/offline detection from the highest environment:
  - check `url`
  - fallback to `https://local_ip:port`
  - fallback to `http://local_ip:port`
- Notes and description fields support Markdown and render as HTML.
- Manage application admins and update history.

## Local Installation

Make sure Python and virtual environment support are available.

```bash
cd app-catalog-manager
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

To use environment variables, copy the example env file:

```bash
cp .env.example .env
```

Then export the required variables before running Django, or add them to your service/deployment configuration.

Optional, seed sample data:

```bash
python manage.py seed_data
```

Run the development server:

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000
```

## Installation with Docker Compose

Start the application and PostgreSQL database:

```bash
docker compose up --build
```

The web container will run migrations, seed data, then start the Django server. The application will be available at:

```text
http://127.0.0.1:8081
```

## Creating a Login User

Create a Django superuser:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter username, email, and password.

If using Docker Compose:

```bash
docker compose exec web python manage.py createsuperuser
```

After creating the user, log in through:

```text
http://127.0.0.1:8000/login/
```

or, if using Docker:

```text
http://127.0.0.1:8081/login/
```

## Useful Commands

Run tests:

```bash
python manage.py test
```

Create and apply migrations after model changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

Open Django admin:

```text
/${ADMIN_PATH}
```

## Environment Variables

All available environment variables are also shown in `.env.example`.

| Variable | Default | Example | Purpose |
| --- | --- | --- | --- |
| `SECRET_KEY` | bundled development key | `change-me` | Django secret key. Must be changed for production. |
| `DEBUG` | `1` | `0` | Enables debug mode. Use `0` for production. |
| `ALLOWED_HOSTS` | `*` | `localhost,127.0.0.1,catalog.example.com` | Comma-separated hosts allowed to access the app. |
| `CSRF_TRUSTED_ORIGINS` | empty | `https://catalog.example.com` | Comma-separated trusted origins for CSRF. |
| `DATABASE_URL` | empty, uses SQLite | `postgres://postgres:postgres@db:5432/appcatalog` | Database connection. If empty, the app uses `db.sqlite3`. |
| `LANGUAGE_CODE` | `id` | `en-us` | Django default language. |
| `TIME_ZONE` | `Asia/Jakarta` | `UTC` | Application timezone. |
| `STATIC_URL` | `static/` | `/static/` | URL prefix for static files. |
| `STATIC_ROOT` | `staticfiles` | `/app/staticfiles` | Output location for `collectstatic`. |
| `MEDIA_URL` | `media/` | `/media/` | URL prefix for uploaded media. |
| `MEDIA_ROOT` | `media` | `/app/media` | Storage location for uploaded media. |
| `LOGIN_URL` | `login` | `login` | Login page route/URL name. |
| `LOGIN_REDIRECT_URL` | `dashboard` | `dashboard` | Redirect target after successful login. |
| `LOGOUT_REDIRECT_URL` | `login` | `login` | Redirect target after logout. |
| `ADMIN_PATH` | `admin/` | `secure-admin-9xk/` | Django admin path. Use a non-standard value to reduce scanning risk. |
| `SECURE_SSL_REDIRECT` | `0` | `1` | Redirect all HTTP requests to HTTPS. Enable for HTTPS production. |
| `SESSION_COOKIE_SECURE` | `0` | `1` | Send session cookies only over HTTPS. |
| `CSRF_COOKIE_SECURE` | `0` | `1` | Send CSRF cookies only over HTTPS. |

Minimal production example:

```env
SECRET_KEY=replace-with-strong-secret
DEBUG=0
ALLOWED_HOSTS=catalog.example.com
CSRF_TRUSTED_ORIGINS=https://catalog.example.com
DATABASE_URL=postgres://user:password@db:5432/appcatalog
ADMIN_PATH=secure-admin-9xk/
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
```

## Data Structure Overview

- `Application`: general application data such as name, description, category, framework, database, repository, maintenance notes, and global deployment notes.
- `ApplicationEnvironment`: deployment configuration per application environment.
- `Server`: host/server data.
- `Category`: application grouping.
- `AppAdmin`: application admin/contact data.
- `UpdateHistory`: application update history.
