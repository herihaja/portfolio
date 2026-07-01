# Herihaja Rabenaivo — Engineering Portfolio

Portfolio website using FastAPI and Docker Compose.

## Overview

- Static frontend (HTML/CSS/JavaScript)
- FastAPI backend
- Docker Compose infrastructure
- NGINX reverse proxy

---

## Live site

https://herihaja.ddns.net

---

# Tech Stack

## Frontend

- HTML5
- CSS3
- Vanilla JavaScript

## Backend

- FastAPI
- Pydantic
- Uvicorn

## Infrastructure

- Docker Compose
- NGINX

## Engineering Focus

- REST API endpoints
- FastAPI backend

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
GET /version
```

Response:

```json
{
  "service": "portfolio-backend",
  "version": "1.0.0"
}
```

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
