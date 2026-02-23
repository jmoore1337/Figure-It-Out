# Figure It Out

**Integrity-first AI tutor + teacher analytics** — Chromebook-friendly monorepo MVP.

Students get a Socratic AI tutor that guides, not gives answers. Teachers see real-time analytics on where students are stuck.

---

## Quick Start (local dev)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Compose)
- [pnpm](https://pnpm.io/installation) (`npm install -g pnpm`)
- Python 3.12+ (for running backend locally without Docker)

### 1. Clone & configure

```bash
git clone https://github.com/jmoore1337/Figure-It-Out.git
cd Figure-It-Out
cp .env.example .env
```

Edit `.env` if needed (defaults work for local dev with SQLite).

### 2. Start everything

```bash
make dev
```

This runs `docker compose up` — starts Postgres, backend (port 8000), and frontend (port 3000).

Or run just the database and start services manually (faster for development):

**Terminal 1 — Database:**
```bash
docker compose up db
```

**Terminal 2 — Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 3 — Frontend:**
```bash
cd frontend
pnpm install
pnpm dev
```

### 3. Migrate & seed demo data

```bash
make migrate   # runs Alembic migrations (auto-run on startup too)
make seed      # creates demo teacher + class + problems
```

After seeding:
- **Teacher login:** `teacher@demo.com` / `admin123`
- **Student join code:** `DEMO01`

### 4. Open the app

| URL | Description |
|---|---|
| http://localhost:3000 | Main app (student or teacher) |
| http://localhost:8000/docs | FastAPI interactive API docs |
| http://localhost:8000/redoc | Alternative API docs |

---

## Architecture

```
Figure-It-Out/
├── frontend/          # Next.js 14 (App Router), TypeScript, Tailwind, shadcn/ui
├── backend/           # FastAPI, Python 3.12, SQLAlchemy 2.0, Alembic
├── docker-compose.yml # Postgres + backend + frontend
├── .env.example       # Environment variable template
├── Makefile           # dev / migrate / seed / test shortcuts
└── README.md
```

### Backend structure

```
backend/
  app/
    main.py            # FastAPI app + CORS + auto-create tables on startup
    config.py          # Pydantic settings (reads .env)
    database.py        # Async SQLAlchemy engine + session
    models/            # SQLAlchemy ORM models
    schemas/           # Pydantic v2 request/response schemas
    routers/           # auth · classes · student · tutor · analytics
    llm/
      provider.py      # LLMProvider ABC + factory (OpenAI or Mock)
      mock_provider.py # Deterministic hint-ladder (works without API key)
      openai_provider.py
    prompts/
      tutor_system.py  # Socratic system prompt with policy injection
    services/
      leakage.py       # Post-generation answer-leakage detector + rewriter
      analytics.py     # Keyword/bigram clustering for question analysis
  alembic/             # Async migrations scaffold
  seed.py              # Demo data seeder
  tests/               # pytest — policy enforcement + leakage checker
```

### Frontend pages

| Route | Description |
|---|---|
| `/` | Landing — choose student or teacher |
| `/student/join` | Enter class code (no login required) |
| `/student/class/[classCode]` | Assignment list |
| `/student/class/.../problem/[problemId]` | **Chat tutor UI** |
| `/teacher/login` | Teacher JWT login |
| `/teacher/dashboard` | Class list + create, copyable join codes |
| `/teacher/class/[classId]` | Assignment list + create |
| `/teacher/class/.../assignment/[assignmentId]` | Analytics dashboard |

---

## Features

### Student (Chromebook-first)
- **No login required** — anonymous ID stored in `localStorage`
- Join class with a 6-character code
- Chat with a Socratic AI tutor (never gives direct answers)
- Keyboard-friendly: `Enter` sends, `Shift+Enter` for newline
- Works in Chrome browser on Chromebooks

### Tutor (hint ladder)
- Progressive hints: levels 0–5 (configurable ceiling per assignment)
- Per-assignment policy: `NO_ANSWER` | `ALLOW_AFTER_MASTERY` | `ALLOW`
- `attempt_required`: tutor asks student to try before escalating
- **Leakage prevention**: post-generation regex checker rewrites final-answer responses, logs `policy_violation_prevented=true`

### Teacher
- Create classes (auto-generated join codes)
- Create assignments with policy JSON
- Analytics dashboard:
  - Sessions count, active students
  - Average hint level used
  - Top intent types (hint request, answer request, check, concept)
  - Top question keywords (bigram frequency clustering)
  - Most common stuck step
  - Policy violations prevented count

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./figureout.db` | Database connection (use `postgresql+asyncpg://...` for Postgres) |
| `TEACHER_ADMIN_PASSWORD` | `admin123` | Single admin password for teacher login |
| `SECRET_KEY` | *(dev default)* | JWT signing secret — **change in production** |
| `OPENAI_API_KEY` | *(empty)* | If set, uses OpenAI; otherwise uses MockProvider |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `ENVIRONMENT` | `development` | Set to `production` for prod |

---

## LLM Providers

The app works **without any API keys** using `MockProvider` — a deterministic hint-ladder tutor great for development and demos.

Set `OPENAI_API_KEY` in `.env` to switch to `OpenAIProvider` automatically.

To add another provider, implement `LLMProvider` in `backend/app/llm/provider.py`.

---

## Running Tests

```bash
make test
# or
cd backend && python -m pytest tests/ -v
```

Tests cover:
- Policy enforcement (NO_ANSWER mode, hint ceiling)
- Leakage checker (detects final answers, no false positives)
- LLM response parsing (valid JSON, markdown-wrapped JSON, plain text fallback)

---

## API Reference

Full interactive docs at http://localhost:8000/docs when running locally.

### Key endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/teacher/login` | Get JWT token |
| `GET` | `/auth/me` | Current teacher info |
| `POST` | `/classes` | Create a class (teacher) |
| `GET` | `/classes` | List teacher's classes |
| `POST` | `/classes/{id}/assignments` | Create assignment |
| `POST` | `/student/join` | Student joins a class |
| `GET` | `/student/classes/{code}/assignments` | List assignments for student |
| `POST` | `/tutor/next` | Get next tutor response |
| `GET` | `/analytics/classes/{id}/assignments/{id}` | Assignment analytics |

### Tutor response format

```json
{
  "student_message": "What do you think the first step should be?",
  "check_question": "What do you know about this problem?",
  "next_action": "hint",
  "telemetry": {
    "intent": "ask_for_hint",
    "skill_tags": ["linear-equations"],
    "stuck_step": 1,
    "hint_level_served": 1,
    "misconception_code": null,
    "policy_violation_prevented": false
  }
}
```

---

## Assignment Policy

```json
{
  "answer_mode": "NO_ANSWER",
  "hint_ceiling": 3,
  "attempt_required": true,
  "show_similar_example": false
}
```

| Field | Options | Description |
|---|---|---|
| `answer_mode` | `NO_ANSWER` / `ALLOW_AFTER_MASTERY` / `ALLOW` | When (if ever) the final answer can be shown |
| `hint_ceiling` | 0–5 | Maximum hint level served |
| `attempt_required` | bool | Student must attempt a step before next hint |
| `show_similar_example` | bool | Allow showing a worked similar example |
