# Herihaja Rabenaivo — Engineering Portfolio

Portfolio website using FastAPI and Docker Compose.

## Overview

- Static frontend (HTML/CSS/JavaScript)
- FastAPI backend
- Docker Compose infrastructure
- NGINX reverse proxy

---

## Live site

https://herihaja.gleeze.com

---

# System Architecture

## Frontend

- Static HTML/CSS/JavaScript frontend
- Multilingual interface
- NGINX-served static assets

## Backend

- FastAPI REST API
- SQLAlchemy ORM with PostgreSQL
- Pydantic validation layer
- JWT-protected admin endpoints
- SMTP notification service
- Background email processing

## Infrastructure

- Docker Compose deployment
- NGINX reverse proxy
- HTTPS with Certbot
- Environment-based configuration

## Operational Concerns

- Origin validation
- IP-based rate limiting
- Visit analytics & monitoring
- Structured production logging

---

# Repository Structure

```text
portfolio/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── js/
│   ├── assets/
│   │   ├── images/
│   │   ├── diagrams/
│   │   └── screenshots/
│   ├── projects/
│   └── fr/
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── ...
│
├── nginx/
│   └── default.conf
│
├── docker-compose.yml
│
└── README.md
```

---

# Running Locally

## Requirements

- Docker
- Docker Compose

## Start Services

```bash
docker compose up --build
```

Create a local `.env` file from the example before starting services:

```bash
cp .env.example .env
```

## Running Tests

Because the backend runs in Docker Compose, run tests from the backend container.

Start a shell inside the backend service:

```bash
docker compose run --rm backend bash
```

Then install the dev dependencies and execute pytest:

```bash
python3 -m pip install -r requirements-dev.txt
pytest -q
```

Or run the full sequence in one command without an interactive shell:

```bash
docker compose run --rm backend bash -lc "python3 -m pip install -r requirements-dev.txt && pytest -q"
```

Update `.env` with your SMTP credentials, database password, and admin secrets.

Frontend:

```text
http://localhost
```

Backend API:

```text
http://localhost/api/
```

Health endpoint:

```text
http://localhost/api/health
```

---

# Example API Endpoints

## Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

---

## Version

```http
GET /api/version
```

Response:

```json
{
  "service": "portfolio-backend",
  "version": "1.0.0"
}
```

---

## Contact Endpoint

```http
POST /api/contact
```

Request body:

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "subject": "Project inquiry",
  "message": "I would like to talk about a backend project."
}
```

This endpoint is used by the frontend contact form and includes a custom header for request validation.

## Admin Endpoints

### Admin login

```http
POST /api/admin/login
```

Request body:

```json
{
  "username": "admin",
  "password": "your_admin_password"
}
```

Response:

```json
{
  "token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

### List stored messages

```http
GET /api/admin/messages
```

Headers:

- `Authorization: Bearer <JWT_TOKEN>`

This endpoint returns the stored contact submissions in the backend database.

---

# Selected Projects

## Trading Automation Platform

Trading system processing market data streams, signals, and automated workflows with monitoring.

- market data streams
- signal processing
- WebSocket integrations
- monitoring workflows
- asynchronous services

## payFlow

- Celery + Redis workflows
- financial transaction pipelines
- asynchronous processing architecture

GitHub:

- https://github.com/herihaja/payflow

---

# Future Improvements

Planned enhancements include:

- architecture diagrams
- project deep-dives
- automated deployment workflows
- add more endpoints

---

# Contact

## Email

[heriinfo@gmail.com](mailto:heriinfo@gmail.com)

## LinkedIn

https://linkedin.com/in/herihaja

## GitHub

https://github.com/herihaja

---

# License

This project is licensed under the MIT License.
