# MgmtSays

Full-stack web application that analyzes management disclosures from publicly listed companies.

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **uv** (Python package manager)

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Run the Application

```bash
# Full build and start (production mode)
uv run python start.py

# Development mode with hot reload
uv run python start.py --dev

# Skip frontend build (use existing build)
uv run python start.py --skip-build

# Custom port
uv run python start.py --port 3000
```

The application will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:8000 (when built)

## Development

### Install Dependencies

```bash
# Sync all dependencies (Python)
uv sync

# Install frontend dependencies
cd frontend && npm install
```

### Run Tests

```bash
# Backend tests
uv run pytest

# Frontend tests
cd frontend && npm test

# E2E tests
cd frontend && npm run test:e2e
```

### Lint & Format

```bash
# Python
uv run ruff check backend/src
uv run ruff format backend/src

# Frontend
cd frontend && npm run lint
```

## Project Structure

```
MgmtSays/
├── backend/           # FastAPI backend
│   ├── src/           # Source code
│   ├── tests/         # Tests
│   └── alembic/       # Database migrations
├── frontend/          # React frontend
│   ├── src/           # Source code
│   └── e2e/           # E2E tests
├── docs/              # Documentation
├── start.py           # Startup script
└── pyproject.toml     # Python project config
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, LlamaIndex, DSPy
- **Frontend**: React, TypeScript, Tailwind CSS, Vite
- **Database**: PostgreSQL (production), SQLite (development)
- **Vector Store**: ChromaDB
- **LLM**: OpenAI / Anthropic
