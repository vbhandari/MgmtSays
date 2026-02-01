# MgmtSays - Project Structure & Architecture Plan

## Overview

This document outlines the complete project structure for the Management Disclosure Intelligence Platform, following modern best practices for separation of concerns, testability, and maintainability.

---

## Root Directory Structure

```
MgmtSays/
├── .github/                     # GitHub workflows & templates
│   ├── workflows/
│   │   ├── ci.yml               # Continuous integration
│   │   ├── cd.yml               # Continuous deployment
│   │   └── codeql.yml           # Security scanning
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS
│
├── backend/                     # Python FastAPI backend
├── frontend/                    # React TypeScript frontend
├── docs/                        # Project documentation
├── scripts/                     # Development & deployment scripts
├── docker/                      # Docker configurations
├── .env.example                 # Environment variables template
├── docker-compose.yml           # Local development orchestration
├── docker-compose.prod.yml      # Production orchestration
├── Makefile                     # Common commands
├── LICENSE
└── README.md
```

---

## Backend Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py          # Pydantic settings management
│   │   └── logging.py           # Logging configuration
│   │
│   ├── api/                     # API layer (controllers)
│   │   ├── __init__.py
│   │   ├── deps.py              # Dependency injection
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── cors.py
│   │   │   ├── auth.py
│   │   │   └── rate_limit.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py        # Main v1 router
│   │       ├── companies.py     # Company endpoints
│   │       ├── documents.py     # Document upload/management
│   │       ├── analysis.py      # Analysis/insights endpoints
│   │       ├── timeline.py      # Timeline endpoints
│   │       └── health.py        # Health check endpoints
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── company_service.py
│   │   ├── document_service.py
│   │   ├── analysis_service.py
│   │   └── timeline_service.py
│   │
│   ├── nlp/                     # NLP/LLM layer
│   │   ├── __init__.py
│   │   ├── ingestion/           # Document ingestion
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Base ingestion interface
│   │   │   ├── pdf_parser.py
│   │   │   ├── docx_parser.py
│   │   │   ├── pptx_parser.py
│   │   │   ├── txt_parser.py
│   │   │   └── factory.py       # Parser factory
│   │   │
│   │   ├── chunking/            # Text chunking strategies
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── semantic_chunker.py
│   │   │   └── structural_chunker.py
│   │   │
│   │   ├── indexing/            # LlamaIndex integration
│   │   │   ├── __init__.py
│   │   │   ├── index_manager.py
│   │   │   ├── vector_store.py
│   │   │   └── metadata.py
│   │   │
│   │   ├── retrieval/           # Retrieval strategies
│   │   │   ├── __init__.py
│   │   │   ├── hybrid_retriever.py
│   │   │   ├── semantic_retriever.py
│   │   │   └── temporal_retriever.py
│   │   │
│   │   ├── dspy_programs/       # DSPy reasoning programs
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── initiative_extractor.py
│   │   │   ├── forward_looking_classifier.py
│   │   │   ├── deduplicator.py
│   │   │   ├── temporal_normalizer.py
│   │   │   └── confidence_scorer.py
│   │   │
│   │   ├── pipelines/           # Orchestration pipelines
│   │   │   ├── __init__.py
│   │   │   ├── ingestion_pipeline.py
│   │   │   ├── analysis_pipeline.py
│   │   │   └── pipeline_factory.py
│   │   │
│   │   └── llm/                 # LLM provider abstraction
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── openai_provider.py
│   │       ├── anthropic_provider.py
│   │       └── factory.py
│   │
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── domain/              # Domain entities
│   │   │   ├── __init__.py
│   │   │   ├── company.py
│   │   │   ├── document.py
│   │   │   ├── insight.py
│   │   │   ├── initiative.py
│   │   │   └── evidence.py
│   │   │
│   │   ├── schemas/             # Pydantic schemas (API)
│   │   │   ├── __init__.py
│   │   │   ├── requests/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── company.py
│   │   │   │   ├── document.py
│   │   │   │   └── analysis.py
│   │   │   └── responses/
│   │   │       ├── __init__.py
│   │   │       ├── company.py
│   │   │       ├── document.py
│   │   │       ├── insight.py
│   │   │       └── timeline.py
│   │   │
│   │   └── db/                  # Database models (SQLAlchemy)
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── company.py
│   │       ├── document.py
│   │       └── analysis.py
│   │
│   ├── repositories/            # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── company_repository.py
│   │   ├── document_repository.py
│   │   └── analysis_repository.py
│   │
│   ├── db/                      # Database infrastructure
│   │   ├── __init__.py
│   │   ├── session.py
│   │   └── migrations/          # Alembic migrations
│   │       ├── env.py
│   │       ├── script.py.mako
│   │       └── versions/
│   │
│   ├── storage/                 # File storage abstraction
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local_storage.py
│   │   └── s3_storage.py
│   │
│   └── utils/                   # Shared utilities
│       ├── __init__.py
│       ├── exceptions.py
│       ├── validators.py
│       └── helpers.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   │
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── test_company_service.py
│   │   │   ├── test_document_service.py
│   │   │   └── test_analysis_service.py
│   │   ├── nlp/
│   │   │   ├── __init__.py
│   │   │   ├── ingestion/
│   │   │   │   ├── test_pdf_parser.py
│   │   │   │   ├── test_docx_parser.py
│   │   │   │   └── test_pptx_parser.py
│   │   │   ├── chunking/
│   │   │   │   └── test_chunkers.py
│   │   │   ├── dspy_programs/
│   │   │   │   ├── test_initiative_extractor.py
│   │   │   │   └── test_deduplicator.py
│   │   │   └── retrieval/
│   │   │       └── test_retrievers.py
│   │   ├── repositories/
│   │   │   └── test_repositories.py
│   │   └── utils/
│   │       └── test_helpers.py
│   │
│   ├── integration/             # Integration tests
│   │   ├── __init__.py
│   │   ├── test_api_companies.py
│   │   ├── test_api_documents.py
│   │   ├── test_api_analysis.py
│   │   ├── test_nlp_pipeline.py
│   │   └── test_database.py
│   │
│   ├── regression/              # Regression tests
│   │   ├── __init__.py
│   │   ├── test_extraction_quality.py
│   │   ├── test_citation_accuracy.py
│   │   └── baselines/           # Golden outputs for comparison
│   │       └── README.md
│   │
│   └── fixtures/                # Test data
│       ├── documents/
│       │   ├── sample_annual_report.pdf
│       │   ├── sample_transcript.txt
│       │   └── sample_presentation.pptx
│       └── expected_outputs/
│           └── sample_insights.json
│
├── alembic.ini
├── pyproject.toml               # Poetry/pip configuration
├── requirements.txt             # Pinned dependencies
├── requirements-dev.txt         # Dev dependencies
├── pytest.ini
├── ruff.toml                    # Ruff linter config
└── Dockerfile
```

---

## Frontend Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   ├── index.html
│   └── assets/
│       └── images/
│
├── src/
│   ├── main.tsx                 # App entry point
│   ├── App.tsx                  # Root component
│   ├── vite-env.d.ts
│   │
│   ├── api/                     # API client layer
│   │   ├── index.ts
│   │   ├── client.ts            # Axios/fetch configuration
│   │   ├── companies.ts
│   │   ├── documents.ts
│   │   ├── analysis.ts
│   │   └── types.ts             # API response types
│   │
│   ├── components/              # React components
│   │   ├── common/              # Shared/reusable components
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.test.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Card/
│   │   │   ├── Input/
│   │   │   ├── Modal/
│   │   │   ├── Loading/
│   │   │   └── ErrorBoundary/
│   │   │
│   │   ├── layout/              # Layout components
│   │   │   ├── Header/
│   │   │   ├── Sidebar/
│   │   │   ├── Footer/
│   │   │   └── MainLayout/
│   │   │
│   │   ├── company/             # Company-related components
│   │   │   ├── CompanySearch/
│   │   │   ├── CompanyCard/
│   │   │   └── CompanyHeader/
│   │   │
│   │   ├── document/            # Document components
│   │   │   ├── DocumentUpload/
│   │   │   ├── DocumentList/
│   │   │   ├── DocumentPreview/
│   │   │   └── DocumentCard/
│   │   │
│   │   ├── insights/            # Insight display components
│   │   │   ├── InsightCard/
│   │   │   ├── InsightList/
│   │   │   ├── InsightDetail/
│   │   │   ├── CategoryBadge/
│   │   │   └── ConfidenceIndicator/
│   │   │
│   │   ├── timeline/            # Timeline components
│   │   │   ├── Timeline/
│   │   │   ├── TimelineItem/
│   │   │   ├── TimelineFilter/
│   │   │   └── TimelineControls/
│   │   │
│   │   └── evidence/            # Citation/evidence components
│   │       ├── EvidenceCard/
│   │       ├── SourceQuote/
│   │       └── DocumentLink/
│   │
│   ├── pages/                   # Page components (routes)
│   │   ├── HomePage/
│   │   │   ├── HomePage.tsx
│   │   │   └── index.ts
│   │   ├── CompanyPage/
│   │   ├── AnalysisPage/
│   │   ├── TimelinePage/
│   │   └── NotFoundPage/
│   │
│   ├── hooks/                   # Custom React hooks
│   │   ├── useCompany.ts
│   │   ├── useDocuments.ts
│   │   ├── useAnalysis.ts
│   │   ├── useTimeline.ts
│   │   └── useDebounce.ts
│   │
│   ├── stores/                  # State management (Zustand/Redux)
│   │   ├── index.ts
│   │   ├── companyStore.ts
│   │   ├── documentStore.ts
│   │   └── analysisStore.ts
│   │
│   ├── types/                   # TypeScript type definitions
│   │   ├── index.ts
│   │   ├── company.ts
│   │   ├── document.ts
│   │   ├── insight.ts
│   │   └── timeline.ts
│   │
│   ├── utils/                   # Utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── dateUtils.ts
│   │   └── constants.ts
│   │
│   ├── styles/                  # Global styles
│   │   ├── index.css
│   │   ├── tailwind.css
│   │   └── typography.css
│   │
│   └── router/                  # Routing configuration
│       └── index.tsx
│
├── tests/
│   ├── setup.ts                 # Test setup
│   │
│   ├── unit/                    # Component unit tests
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── insights/
│   │   │   └── timeline/
│   │   ├── hooks/
│   │   │   └── useAnalysis.test.ts
│   │   └── utils/
│   │       └── formatters.test.ts
│   │
│   ├── integration/             # Integration tests
│   │   ├── api/
│   │   │   └── client.test.ts
│   │   └── stores/
│   │       └── companyStore.test.ts
│   │
│   └── e2e/                     # End-to-end tests (Playwright)
│       ├── playwright.config.ts
│       ├── fixtures/
│       │   └── test-data.ts
│       ├── pages/               # Page object models
│       │   ├── BasePage.ts
│       │   ├── HomePage.ts
│       │   ├── CompanyPage.ts
│       │   └── AnalysisPage.ts
│       └── specs/
│           ├── company-search.spec.ts
│           ├── document-upload.spec.ts
│           ├── analysis-flow.spec.ts
│           └── timeline-interaction.spec.ts
│
├── .storybook/                  # Storybook configuration
│   ├── main.ts
│   └── preview.ts
│
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── eslint.config.js
├── prettier.config.js
└── Dockerfile
```

---

## Documentation Structure

```
docs/
├── IDEA.md                      # Original PRD
├── PROJECT_STRUCTURE.md         # This document
├── CONTRIBUTING.md              # Contribution guidelines
├── CHANGELOG.md                 # Version history
│
├── architecture/
│   ├── README.md
│   ├── system-overview.md       # High-level architecture
│   ├── nlp-pipeline.md          # NLP processing details
│   ├── data-flow.md             # Data flow diagrams
│   └── diagrams/
│       ├── system-architecture.png
│       ├── nlp-pipeline.png
│       └── er-diagram.png
│
├── api/
│   ├── README.md
│   ├── openapi.yaml             # OpenAPI specification
│   └── examples/
│       ├── company-endpoints.md
│       ├── document-endpoints.md
│       └── analysis-endpoints.md
│
├── development/
│   ├── README.md
│   ├── setup-guide.md           # Local development setup
│   ├── coding-standards.md      # Code style guide
│   ├── testing-guide.md         # Testing practices
│   └── debugging.md             # Common debugging tips
│
├── deployment/
│   ├── README.md
│   ├── docker-guide.md
│   ├── kubernetes.md
│   └── environment-variables.md
│
└── nlp/
    ├── README.md
    ├── dspy-programs.md         # DSPy program documentation
    ├── llamaindex-setup.md      # LlamaIndex configuration
    ├── prompts.md               # Prompt templates
    └── evaluation.md            # NLP evaluation criteria
```

---

## Scripts Directory

```
scripts/
├── setup/
│   ├── install-deps.sh          # Install all dependencies
│   ├── setup-db.sh              # Database initialization
│   └── setup-env.sh             # Environment setup
│
├── dev/
│   ├── run-backend.sh
│   ├── run-frontend.sh
│   └── run-all.sh
│
├── test/
│   ├── run-unit-tests.sh
│   ├── run-integration-tests.sh
│   ├── run-e2e-tests.sh
│   ├── run-regression-tests.sh
│   └── run-all-tests.sh
│
├── db/
│   ├── migrate.sh
│   ├── seed.sh
│   └── reset.sh
│
└── ci/
    ├── lint.sh
    ├── format.sh
    └── build.sh
```

---

## Docker Structure

```
docker/
├── backend/
│   ├── Dockerfile
│   └── Dockerfile.dev
│
├── frontend/
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   └── nginx.conf
│
├── db/
│   └── init.sql
│
└── vector-db/
    └── Dockerfile
```

---

## Testing Strategy

### Backend Testing

| Test Type | Location | Tools | Purpose |
|-----------|----------|-------|---------|
| Unit | `backend/tests/unit/` | Pytest, pytest-mock | Test individual functions/classes in isolation |
| Integration | `backend/tests/integration/` | Pytest, httpx | Test API endpoints with real database |
| Regression | `backend/tests/regression/` | Pytest, custom | Verify NLP extraction quality against baselines |

### Frontend Testing

| Test Type | Location | Tools | Purpose |
|-----------|----------|-------|---------|
| Unit | `frontend/tests/unit/` | Vitest, React Testing Library | Test components and hooks |
| Integration | `frontend/tests/integration/` | Vitest, MSW | Test API integration and state management |
| E2E | `frontend/tests/e2e/` | Playwright | Full user flow testing |

### NLP-Specific Testing

```
backend/tests/regression/
├── test_extraction_quality.py   # Compare extracted insights to golden data
├── test_citation_accuracy.py    # Verify citations point to correct sources
├── test_deduplication.py        # Ensure similar insights are properly grouped
├── test_temporal_ordering.py    # Verify timeline accuracy
└── baselines/
    ├── README.md
    ├── company_a/
    │   ├── input_documents/
    │   └── expected_insights.json
    └── company_b/
        ├── input_documents/
        └── expected_insights.json
```

---

## Key Design Patterns

### Backend Patterns

1. **Repository Pattern** - Abstract data access from business logic
2. **Service Layer** - Encapsulate business logic
3. **Factory Pattern** - Create document parsers and LLM providers
4. **Pipeline Pattern** - Chain NLP processing steps
5. **Dependency Injection** - FastAPI's `Depends()` for loose coupling

### Frontend Patterns

1. **Component Composition** - Small, reusable components
2. **Custom Hooks** - Encapsulate stateful logic
3. **Store Pattern** - Centralized state with Zustand
4. **Page Object Model** - E2E test organization

---

## Configuration Files Summary

### Root Level
- `docker-compose.yml` - Local development stack
- `Makefile` - Common commands shortcut
- `.env.example` - Environment variable template

### Backend
- `pyproject.toml` - Python project configuration
- `ruff.toml` - Linter configuration
- `pytest.ini` - Test configuration
- `alembic.ini` - Database migration configuration

### Frontend
- `package.json` - Node dependencies
- `vite.config.ts` - Build configuration
- `tsconfig.json` - TypeScript configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `eslint.config.js` - Linter configuration
- `playwright.config.ts` - E2E test configuration

---

## Next Steps

1. **Phase 1: Foundation**
   - [ ] Initialize backend with FastAPI scaffold
   - [ ] Initialize frontend with Vite + React + TypeScript
   - [ ] Set up Docker Compose for local development
   - [ ] Configure CI/CD pipelines

2. **Phase 2: Core Backend**
   - [ ] Implement document ingestion pipeline
   - [ ] Set up LlamaIndex indexing
   - [ ] Create basic DSPy programs
   - [ ] Build REST API endpoints

3. **Phase 3: Core Frontend**
   - [ ] Build component library
   - [ ] Implement document upload flow
   - [ ] Create timeline visualization
   - [ ] Build insight display components

4. **Phase 4: Integration & Testing**
   - [ ] End-to-end pipeline integration
   - [ ] Comprehensive test coverage
   - [ ] Performance optimization
   - [ ] Documentation completion
