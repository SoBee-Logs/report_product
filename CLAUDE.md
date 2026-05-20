# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SoBee** is a mobile-first (375px) financial consumption report and product recommendation app. It is composed of three independent subsystems:

```
sobee-log/          # React + Vite frontend
sobee_fastapi/      # Python FastAPI (AI/ML: VLM receipt/image analysis, AI diary generation, avatar, recommendations)
sobee_springboot/   # Java Spring Boot (auth, CRUD, business logic)
```

## Architecture

### Service Communication

```
sobee-log (Vite dev :5173)
    ↓ REST
sobee_springboot (:8081)   ← User auth (JWT), DB, groups, feed, payments
    ↓ REST
sobee_fastapi (:8000)      ← VLM Analysis (Gemini), Diary Generation (LLM), Avatar, Recommendations
```

FastAPI has **no auth**; Spring Boot handles all authentication and calls FastAPI internally.

### Frontend (`sobee-log`)
- React 19 + Vite, Tailwind CSS v4, React Router v7
- Routes are declared as a config array in `src/App.jsx` (`routeConfig`). Each route specifies which layout components to render (`showAppBar`, `showBottomNav`).
- Fixed width of 375px for mobile web.
- Cross-team navigation (to other deployed services) uses `window.location.href`, not React Router.
- API base URL comes from `.env.local` (not committed).
- Mock data lives in `src/data/mockDiaries.js`.

### FastAPI (`sobee_fastapi`)
- Routers: `/api/vlm` (for Gemini 2.5 Flash image extraction), `/api/diary` (for LLM diary generation), `/api/avatar`, `/api/recommend`, `/api/lifecycle`
- Each feature follows the pattern: `app/api/<feature>.py` → `app/services/<feature>_service.py`
- Core AI Engine: Uses `google-genai` (Gemini 2.5 Flash) for image parsing and text generation.
- Pydantic schemas in `app/models/schemas.py`
- Settings (GEMINI_API_KEY, OpenAI key, MySQL URL) via `app/core/config.py` (`pydantic-settings`, `.env`)
- ML model (KNN lifecycle predictor) in `ml/lifecycle_model.py`

### Spring Boot (`sobee_springboot`)
- Java 21, Spring Boot 3.5, JPA + MySQL, JWT auth
- Domain-driven structure under `src/main/java/com/sobee/sobee/domain/`
- DB: MySQL on `localhost:3306/sobee`
- Server port: 8081
- Security is permissive in dev mode (all requests permitted, CSRF disabled).

## Commands

### Frontend
```bash
cd sobee-log
npm install
npm run dev        # dev server at :5173
npm run build      # production build
npm run lint       # ESLint
npm run preview    # preview production build
```

### FastAPI
```bash
cd sobee_fastapi
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# Swagger UI: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

#### Docker
```bash
docker build -t sobee-fastapi .
docker run -p 8000:8000 sobee-fastapi
```

### Spring Boot
```bash
cd sobee_springboot
./gradlew bootRun          # start server at :8081
./gradlew test             # run tests
gradlew.bat bootRun        # Windows
```

## Git Conventions

PR commit types: `feat`, `fix`, `style`, `refactor`, `docs`, `chore`

PRs must:
- Pass local testing before opening
- Not modify other teams' files without coordination
- Not include `.env` or credentials

## Environment Variables

### FastAPI (`.env` in `sobee_fastapi/`)
- `GEMINI_API_KEY` — Crucial for VLM and Diary generation
- `OPENAI_API_KEY`
- `MYSQL_URL`

### Frontend (`.env.local` in `sobee-log/`)
- API base URLs per environment

## Key Reference Docs
- `sobee_fastapi/reference.md` — FastAPI architecture and local setup walkthrough
- `sobee-log/notice.md` — Frontend routing conventions, multi-team navigation rules, API call patterns
