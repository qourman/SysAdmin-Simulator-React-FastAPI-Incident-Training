# SysAdmin Simulator

React + FastAPI training game where you play a junior systems administrator handling on-call incidents through a guided terminal experience. Built by **Aymane Qouraiche** to showcase frontend craft, backend validation, and realistic infrastructure scenarios.

## Features

- 🎯 **Mission-driven gameplay** – tackle curated scenarios like restoring network routes or stabilising failing services.
- 🖥️ **In-browser terminal** – XTerm.js powers an interactive shell for entering commands with instant feedback.
- 🧠 **Backend validation** – FastAPI tracks progress, scores attempts, and returns contextual hints.
- 📊 **HUD and timers** – real-time score, mistakes, and countdown help simulate on-call pressure.
- 🚢 **Deployment ready** – Dockerfiles and compose setup for one-command local or cloud deployment.

## Tech Stack

- Frontend: React 19 + TypeScript + Vite, @xterm/xterm
- Backend: FastAPI (Python 3.11), Pydantic v2, Mission engine in-memory store
- Tooling: npm, uvicorn, Docker, docker-compose

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.11+
- npm and pip in your PATH

### 1. Configure environment

```bash
cp frontend/.env.example frontend/.env
cp backend/.env.example backend/.env
```

Adjust the values if you expose the API elsewhere.

### 2. Install dependencies

```bash
# Frontend
echo "Installing UI deps" && cd frontend && npm install && cd ..

# Backend
echo "Installing API deps" && cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt
```

> On Windows PowerShell replace the activation command with `.venv\Scripts\Activate.ps1`.

### 3. Run locally

```bash
# Terminal 1 – Backend
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 2 – Frontend
cd frontend
npm run dev
```

Visit `http://localhost:5173` and try a mission. The frontend expects the API at `http://localhost:8000/api` by default.

## Docker Workflow

Build and launch both services:

```bash
docker compose up --build
```

- Frontend served at http://localhost:5173
- Backend available at http://localhost:8000 (API routes under `/api`)

To rebuild after code changes:

```bash
docker compose up --build --force-recreate
```

## Project Structure

```
frontend/   # React + Vite app with XTerm terminal
backend/    # FastAPI mission engine and validation logic
```

## Testing & Linting

- Frontend: `npm run lint`
- Backend: add FastAPI/Pytest suites under `backend/tests` (not included yet). Consider writing tests for mission evaluation rules.

## Deployment Notes

- Update `frontend/Dockerfile` build arg `VITE_API_URL` if your API lives behind a different hostname.
- Configure HTTPS/ingress at your hosting provider; the containers expose 80 (frontend) and 8000 (backend).
- For stateful missions, swap the in-memory session store with Redis or a database and update `MissionStore` accordingly.

## Attribution

Crafted by **Aymane Qouraiche** to demonstrate full-stack system administration simulation.
