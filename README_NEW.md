# MgmtSays - Management Disclosure Intelligence Platform

[![CI](https://github.com/yourusername/mgmtsays/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/mgmtsays/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Extract strategic insights from what management says** — Transform earnings calls, annual reports, and investor presentations into actionable intelligence.

## 🎯 What is MgmtSays?

MgmtSays is an NLP-powered platform that analyzes management disclosures from publicly traded companies to extract and synthesize strategic insights. It answers the question: *"What is management actually saying about the company's future?"*

### Key Features

- 📄 **Document Ingestion** — Upload PDFs, earnings transcripts, investor decks
- 🧠 **AI-Powered Extraction** — Identify strategic initiatives, guidance, M&A signals
- 📊 **Timeline View** — Track how management messaging evolves over time
- 🔗 **Full Citations** — Every insight links back to source documents

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- OpenAI API key (or Anthropic)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/mgmtsays.git
cd mgmtsays

# Copy environment file and add your API keys
cp .env.example .env

# Start all services
make dev
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs

### Alternative: Manual Setup

```bash
# Backend
cd backend
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8080

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  React + TS     │────▶│  FastAPI        │────▶│  PostgreSQL     │
│  Frontend       │     │  Backend        │     │  Database       │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │                         │
                    │  NLP Pipeline           │
                    │  ├── LlamaIndex         │
                    │  ├── DSPy Programs      │
                    │  └── ChromaDB           │
                    │                         │
                    └─────────────────────────┘
```

## 📁 Project Structure

```
MgmtSays/
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── api/            # REST API endpoints
│   │   ├── services/       # Business logic
│   │   ├── nlp/            # LlamaIndex + DSPy pipelines
│   │   ├── models/         # Domain & database models
│   │   └── repositories/   # Data access layer
│   └── tests/
│
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Route pages
│   │   ├── hooks/          # Custom React hooks
│   │   └── stores/         # Zustand state management
│   └── tests/
│
├── docs/                   # Documentation
├── docker/                 # Docker configurations
└── scripts/                # Development scripts
```

## 🧪 Testing

```bash
# Run all tests
make test

# Backend only
make test-backend

# Frontend only
make test-frontend

# E2E tests
make test-e2e

# With coverage
make test-cov
```

## 🛠️ Development

```bash
# Linting
make lint

# Format code
make format

# Type checking
make typecheck

# Database migrations
make db-migrate
```

## 📚 Documentation

- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [PRD & Vision](docs/IDEA.md)
- [API Documentation](http://localhost:8080/docs) (when running)
- [Contributing Guide](docs/CONTRIBUTING.md)

## 🗺️ Roadmap

### Phase 1: MVP ✨
- [ ] Single-company document ingestion
- [ ] Strategic initiative extraction
- [ ] Timeline visualization
- [ ] Citation tracking

### Phase 2: Enhanced Analysis
- [ ] Multi-period trend analysis
- [ ] Confidence scoring
- [ ] User accounts

### Phase 3: Scale
- [ ] Cross-company comparison
- [ ] Alerts on new disclosures
- [ ] Public API

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with ❤️ using [LlamaIndex](https://www.llamaindex.ai/) and [DSPy](https://dspy-docs.vercel.app/)
