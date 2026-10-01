# Registration App

## 1. Project Overview

A simple web app where users register their **name, place and phone number**.
It supports full CRUD (Create, Read, Update, Delete). Data is stored in MySQL.

## 2. Architecture

```text
Browser
   |
   | Registration Form (HTML/CSS/JS, fetch())
   v
Flask REST API
   |
   | CRUD (SQLAlchemy + PyMySQL)
   v
MySQL
```

```text
registration-app/
├── app.py                        # Flask app, /health, error handlers
├── requirements.txt
├── .env.example
├── config/database.py            # DB connection settings (from env vars)
├── models/registration.py        # Registration table model
├── routes/registration_routes.py # REST API endpoints
├── templates/index.html          # Page
└── static/{css/style.css, js/app.js}
```

## 3. Prerequisites

- Python 3.9+
- MySQL 8.x (running locally)
- pip

## 4. MySQL Setup

Log in as a MySQL admin (this is only for setup, the app never uses root):

```bash
mysql -u root -p
```

Then run:

```sql
-- 1. Create the database
CREATE DATABASE IF NOT EXISTS registration_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. Create the table
USE registration_db;

CREATE TABLE IF NOT EXISTS registrations (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  place      VARCHAR(100) NOT NULL,
  phone      VARCHAR(20)  NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 3. Create an application-specific user (change the password!)
CREATE USER IF NOT EXISTS 'registration_user'@'localhost'
  IDENTIFIED BY 'change_me';

-- 4. Grant only the permissions the app needs
GRANT SELECT, INSERT, UPDATE, DELETE
  ON registration_db.registrations
  TO 'registration_user'@'localhost';

FLUSH PRIVILEGES;
```

## 5. Python Setup

```bash
cd registration-app
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 6. Environment Variables

```bash
cp .env.example .env              # Windows: copy .env.example .env
```

Edit `.env` and set your real password:

| Variable      | Example             |
| ------------- | ------------------- |
| DB_HOST       | localhost           |
| DB_PORT       | 3306                |
| DB_NAME       | registration_db     |
| DB_USER       | registration_user   |
| DB_PASSWORD   | change_me           |

`.env` is listed in `.gitignore` and must never be committed.

## 7. Start the Application

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.
Health check: http://127.0.0.1:5000/health

## 8. API Endpoints

| Method | Endpoint                   | Description        | Success |
| ------ | -------------------------- | ------------------ | ------- |
| GET    | /health                    | Health check       | 200     |
| POST   | /api/registrations         | Create             | 201     |
| GET    | /api/registrations         | Get all            | 200     |
| GET    | /api/registrations/<id>    | Get one            | 200     |
| PUT    | /api/registrations/<id>    | Update             | 200     |
| DELETE | /api/registrations/<id>    | Delete             | 200     |

Errors return JSON like `{"error": "name is required"}` with status
400 (bad request / invalid ID), 404 (not found) or 500 (server / database error).

## 9. Example API Requests

```bash
# Create
curl -X POST http://127.0.0.1:5000/api/registrations \
  -H "Content-Type: application/json" \
  -d '{"name": "Harish", "place": "Hyderabad", "phone": "9876543210"}'

# Get all
curl http://127.0.0.1:5000/api/registrations

# Get by ID
curl http://127.0.0.1:5000/api/registrations/1

# Update
curl -X PUT http://127.0.0.1:5000/api/registrations/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Harish Gundimeda", "place": "Hyderabad", "phone": "9876543210"}'

# Delete
curl -X DELETE http://127.0.0.1:5000/api/registrations/1

# Health
curl http://127.0.0.1:5000/health
```
