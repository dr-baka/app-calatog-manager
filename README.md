# App Catalog Manager

[English](README.en.md) | Bahasa Indonesia

App Catalog Manager adalah aplikasi Django untuk mencatat dan memantau katalog aplikasi internal. Aplikasi ini membantu tim melihat daftar aplikasi, kategori, server, admin aplikasi, riwayat update, serta konfigurasi environment server untuk `DEV`, `BETA`, dan `PROD`.

## Fitur Utama

- Login dan logout menggunakan authentication bawaan Django.
- Manajemen aplikasi, kategori, dan server.
- Satu aplikasi dapat memiliki beberapa environment: `DEV`, `BETA`, dan `PROD`.
- Setiap environment dapat memiliki server, URL, local IP, port, status aktif, dan deployment notes sendiri.
- Dashboard dan daftar aplikasi menampilkan environment tertinggi dengan urutan `DEV < BETA < PROD`.
- Detail aplikasi menampilkan seluruh environment yang dimiliki aplikasi.
- Deteksi online/offline aplikasi dari environment tertinggi:
  - cek `url`
  - fallback ke `https://local_ip:port`
  - fallback ke `http://local_ip:port`
- Field catatan/deskripsi mendukung Markdown dan dirender sebagai HTML.
- Manajemen admin aplikasi dan riwayat update.

## Instalasi Lokal

Pastikan Python dan virtual environment sudah tersedia.

```bash
cd app-catalog-manager
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

Jika ingin memakai environment variable, salin contoh file env:

```bash
cp .env.example .env
```

Lalu export variable yang dibutuhkan sebelum menjalankan Django, atau masukkan ke konfigurasi service/deployment Anda.

Opsional, isi data contoh:

```bash
python manage.py seed_data
```

Jalankan server development:

```bash
python manage.py runserver
```

Aplikasi akan tersedia di:

```text
http://127.0.0.1:8000
```

## Instalasi dengan Docker Compose

Jalankan aplikasi dan database PostgreSQL:

```bash
docker compose up --build
```

Container web akan menjalankan migration, seed data, lalu server Django. Aplikasi tersedia di:

```text
http://127.0.0.1:8081
```

## Membuat User Login

Buat superuser Django:

```bash
python manage.py createsuperuser
```

Ikuti prompt untuk mengisi username, email, dan password.

Jika menggunakan Docker Compose:

```bash
docker compose exec web python manage.py createsuperuser
```

Setelah user dibuat, login melalui:

```text
http://127.0.0.1:8000/login/
```

atau jika menggunakan Docker:

```text
http://127.0.0.1:8081/login/
```

## Perintah Berguna

Menjalankan test:

```bash
python manage.py test
```

Membuat migration setelah perubahan model:

```bash
python manage.py makemigrations
python manage.py migrate
```

Masuk ke Django admin:

```text
/${ADMIN_PATH}
```

## Environment Variable

Semua environment variable yang tersedia juga dicontohkan di `.env.example`.

| Variable | Default | Contoh | Fungsi |
| --- | --- | --- | --- |
| `SECRET_KEY` | development key bawaan | `change-me` | Secret key Django. Wajib diganti untuk production. |
| `DEBUG` | `1` | `0` | Mengaktifkan mode debug. Gunakan `0` untuk production. |
| `ALLOWED_HOSTS` | `*` | `localhost,127.0.0.1,catalog.example.com` | Daftar host yang boleh mengakses aplikasi, dipisah koma. |
| `CSRF_TRUSTED_ORIGINS` | kosong | `https://catalog.example.com` | Daftar origin tepercaya untuk CSRF, dipisah koma. |
| `DATABASE_URL` | kosong, memakai SQLite | `postgres://postgres:postgres@db:5432/appcatalog` | Koneksi database. Jika kosong, aplikasi memakai `db.sqlite3`. |
| `LANGUAGE_CODE` | `id` | `en-us` | Bahasa default Django. |
| `TIME_ZONE` | `Asia/Jakarta` | `UTC` | Timezone aplikasi. |
| `STATIC_URL` | `static/` | `/static/` | URL prefix untuk static files. |
| `STATIC_ROOT` | `staticfiles` | `/app/staticfiles` | Lokasi output `collectstatic`. |
| `MEDIA_URL` | `media/` | `/media/` | URL prefix untuk uploaded media. |
| `MEDIA_ROOT` | `media` | `/app/media` | Lokasi penyimpanan uploaded media. |
| `LOGIN_URL` | `login` | `login` | Nama route/URL halaman login. |
| `LOGIN_REDIRECT_URL` | `dashboard` | `dashboard` | Redirect setelah login berhasil. |
| `LOGOUT_REDIRECT_URL` | `login` | `login` | Redirect setelah logout. |
| `ADMIN_PATH` | `admin/` | `secure-admin-9xk/` | Path Django admin. Gunakan nilai non-standar untuk mengurangi risiko scanning. |
| `SECURE_SSL_REDIRECT` | `0` | `1` | Redirect semua request HTTP ke HTTPS. Aktifkan di production HTTPS. |
| `SESSION_COOKIE_SECURE` | `0` | `1` | Membuat session cookie hanya dikirim lewat HTTPS. |
| `CSRF_COOKIE_SECURE` | `0` | `1` | Membuat CSRF cookie hanya dikirim lewat HTTPS. |

Contoh production minimal:

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

## Struktur Data Singkat

- `Application`: data umum aplikasi seperti nama, deskripsi, kategori, framework, database, repository, maintenance notes, dan deployment notes global.
- `ApplicationEnvironment`: konfigurasi deployment per environment aplikasi.
- `Server`: data host/server.
- `Category`: pengelompokan aplikasi.
- `AppAdmin`: kontak/admin aplikasi.
- `UpdateHistory`: riwayat update aplikasi.
