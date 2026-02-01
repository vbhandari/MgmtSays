# MgmtSays - Complete Task Breakdown

## Overview

This document contains the complete task breakdown for implementing the Management Disclosure Intelligence Platform. Each phase is broken into epics, and each epic contains specific tasks with estimates.

**Review this plan carefully before approving execution.**

---

## Phase 1: Foundation & Infrastructure (Week 1-2)

### Epic 1.1: Backend Foundation
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 1.1.1 | Create FastAPI application entry point | Set up `main.py` with app factory, middleware, CORS | 2h |
| 1.1.2 | Implement settings management | Pydantic settings with env validation | 1h |
| 1.1.3 | Set up logging configuration | Structured logging with structlog | 1h |
| 1.1.4 | Create base API router structure | v1 router with health check endpoint | 1h |
| 1.1.5 | Implement exception handlers | Global error handling and custom exceptions | 2h |
| 1.1.6 | Set up dependency injection | FastAPI deps for DB, services | 2h |

### Epic 1.2: Database Setup
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 1.2.1 | Configure SQLAlchemy async session | Database session management | 2h |
| 1.2.2 | Create base model classes | SQLAlchemy base with common fields | 1h |
| 1.2.3 | Set up Alembic migrations | Migration environment and initial migration | 2h |
| 1.2.4 | Create Company model | Company entity with ticker, name, metadata | 1h |
| 1.2.5 | Create Document model | Document entity with file metadata | 1h |
| 1.2.6 | Create Insight/Initiative models | Core NLP output models | 2h |

### Epic 1.3: Frontend Foundation
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 1.3.1 | Initialize Vite + React + TypeScript | Base React app with proper config | 1h |
| 1.3.2 | Set up Tailwind CSS | Tailwind with custom theme from config | 1h |
| 1.3.3 | Create routing structure | React Router with page stubs | 1h |
| 1.3.4 | Set up API client | Axios client with interceptors | 2h |
| 1.3.5 | Configure React Query | TanStack Query setup | 1h |
| 1.3.6 | Create Zustand stores | Base store structure | 1h |
| 1.3.7 | Build common UI components | Button, Card, Input, Loading, Modal | 4h |
| 1.3.8 | Create main layout | Header, Sidebar, MainLayout components | 2h |

### Epic 1.4: Testing Infrastructure
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 1.4.1 | Configure pytest for backend | conftest.py with fixtures | 2h |
| 1.4.2 | Set up test database | In-memory or test container DB | 1h |
| 1.4.3 | Configure Vitest for frontend | Setup file and mock utilities | 1h |
| 1.4.4 | Set up Playwright | E2E test configuration | 1h |
| 1.4.5 | Create test utilities | Factories, helpers, mock data | 2h |

**Phase 1 Total: ~35 hours**

---

## Phase 2: Document Ingestion Pipeline (Week 2-3)

### Epic 2.1: File Upload & Storage
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 2.1.1 | Create file storage abstraction | Base interface for storage backends | 1h |
| 2.1.2 | Implement local file storage | Local filesystem storage | 2h |
| 2.1.3 | Create document upload endpoint | POST /documents with multipart | 2h |
| 2.1.4 | Build document list endpoint | GET /documents with filtering | 1h |
| 2.1.5 | Create document service layer | Business logic for documents | 2h |
| 2.1.6 | Add document repository | Data access for documents | 1h |

### Epic 2.2: Document Parsing
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 2.2.1 | Create parser base interface | Abstract parser class | 1h |
| 2.2.2 | Implement PDF parser | PyMuPDF/unstructured PDF parsing | 3h |
| 2.2.3 | Implement DOCX parser | python-docx parsing | 2h |
| 2.2.4 | Implement PPTX parser | python-pptx parsing | 2h |
| 2.2.5 | Implement TXT parser | Plain text parsing | 1h |
| 2.2.6 | Create parser factory | Factory for selecting parser by type | 1h |
| 2.2.7 | Add metadata extraction | Date, author, doc type detection | 2h |

### Epic 2.3: Text Chunking
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 2.3.1 | Create chunker base interface | Abstract chunker class | 1h |
| 2.3.2 | Implement semantic chunker | LlamaIndex semantic chunking | 2h |
| 2.3.3 | Implement structural chunker | Section-aware chunking | 3h |
| 2.3.4 | Add chunk metadata | Track source location, section | 1h |

### Epic 2.4: Frontend Upload Flow
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 2.4.1 | Build DocumentUpload component | Dropzone with file validation | 3h |
| 2.4.2 | Create upload progress UI | Progress bar, status indicators | 2h |
| 2.4.3 | Build DocumentList component | List view with cards | 2h |
| 2.4.4 | Create DocumentCard component | Individual document display | 1h |
| 2.4.5 | Add document preview | PDF/text preview modal | 3h |

### Epic 2.5: Ingestion Tests
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 2.5.1 | Unit tests for parsers | Test each parser type | 3h |
| 2.5.2 | Unit tests for chunkers | Test chunking strategies | 2h |
| 2.5.3 | Integration tests for upload | API endpoint tests | 2h |
| 2.5.4 | Frontend component tests | Upload and list components | 2h |

**Phase 2 Total: ~47 hours**

---

## Phase 3: LlamaIndex Integration (Week 3-4)

### Epic 3.1: Vector Store Setup
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 3.1.1 | Configure ChromaDB client | Connection and auth setup | 2h |
| 3.1.2 | Create vector store abstraction | Interface for vector stores | 1h |
| 3.1.3 | Implement index manager | Create, update, delete indices | 3h |
| 3.1.4 | Add embedding configuration | OpenAI embeddings setup | 1h |

### Epic 3.2: Document Indexing
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 3.2.1 | Create indexing pipeline | End-to-end ingestion → index | 3h |
| 3.2.2 | Implement metadata storage | Store chunk metadata in vector store | 2h |
| 3.2.3 | Add document-level index management | Per-company/document indices | 2h |
| 3.2.4 | Implement index persistence | Save/load indices | 1h |

### Epic 3.3: Retrieval Implementation
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 3.3.1 | Create retriever base interface | Abstract retriever class | 1h |
| 3.3.2 | Implement semantic retriever | Vector similarity retrieval | 2h |
| 3.3.3 | Implement hybrid retriever | Semantic + keyword retrieval | 3h |
| 3.3.4 | Implement temporal retriever | Time-filtered retrieval | 2h |
| 3.3.5 | Add retrieval with citations | Include source metadata | 2h |

### Epic 3.4: Integration Tests
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 3.4.1 | Test index creation | Verify indexing pipeline | 2h |
| 3.4.2 | Test retrieval accuracy | Validate retrieval quality | 2h |
| 3.4.3 | Test metadata preservation | Verify citations work | 1h |

**Phase 3 Total: ~30 hours**

---

## Phase 4: DSPy Programs (Week 4-5)

### Epic 4.1: DSPy Foundation
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 4.1.1 | Configure DSPy with LLM providers | OpenAI/Anthropic setup | 2h |
| 4.1.2 | Create base program structure | Abstract DSPy program class | 1h |
| 4.1.3 | Define output schemas | Pydantic models for DSPy outputs | 2h |

### Epic 4.2: Extraction Programs
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 4.2.1 | Implement InitiativeExtractor | Extract strategic initiatives | 4h |
| 4.2.2 | Implement ForwardLookingClassifier | Identify forward guidance | 3h |
| 4.2.3 | Implement CategoryClassifier | Categorize initiatives | 2h |
| 4.2.4 | Implement ConfidenceScorer | Score extraction confidence | 2h |

### Epic 4.3: Post-Processing Programs
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 4.3.1 | Implement Deduplicator | Merge similar initiatives | 3h |
| 4.3.2 | Implement TemporalNormalizer | Normalize time references | 2h |
| 4.3.3 | Implement InitiativeLinker | Link across documents | 3h |

### Epic 4.4: Analysis Pipeline
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 4.4.1 | Create analysis pipeline orchestrator | Chain DSPy programs | 3h |
| 4.4.2 | Implement caching layer | Cache LLM calls | 2h |
| 4.4.3 | Add async processing | Background task handling | 2h |

### Epic 4.5: NLP Tests
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 4.5.1 | Unit tests for DSPy programs | Mock LLM tests | 3h |
| 4.5.2 | Create regression test framework | Golden output comparison | 3h |
| 4.5.3 | Create baseline test datasets | Sample docs + expected outputs | 4h |

**Phase 4 Total: ~41 hours**

---

## Phase 5: Analysis API & Services (Week 5-6)

### Epic 5.1: Company Management
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 5.1.1 | Create company endpoints | CRUD for companies | 2h |
| 5.1.2 | Implement company service | Company business logic | 1h |
| 5.1.3 | Add company repository | Company data access | 1h |
| 5.1.4 | Add ticker validation | Validate company tickers | 1h |

### Epic 5.2: Analysis Endpoints
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 5.2.1 | Create analysis trigger endpoint | POST /analysis/run | 2h |
| 5.2.2 | Create analysis status endpoint | GET /analysis/{id}/status | 1h |
| 5.2.3 | Create insights endpoint | GET /companies/{id}/insights | 2h |
| 5.2.4 | Implement analysis service | Orchestrate NLP pipeline | 3h |
| 5.2.5 | Add analysis repository | Store analysis results | 2h |

### Epic 5.3: Timeline Endpoints
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 5.3.1 | Create timeline endpoint | GET /companies/{id}/timeline | 2h |
| 5.3.2 | Implement timeline service | Build timeline from insights | 3h |
| 5.3.3 | Add temporal grouping | Group by quarter/year | 2h |

### Epic 5.4: API Tests
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 5.4.1 | Integration tests for company API | Full CRUD tests | 2h |
| 5.4.2 | Integration tests for analysis API | Analysis flow tests | 3h |
| 5.4.3 | Integration tests for timeline API | Timeline generation tests | 2h |

**Phase 5 Total: ~29 hours**

---

## Phase 6: Frontend Features (Week 6-7)

### Epic 6.1: Company Features
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 6.1.1 | Build CompanySearch component | Ticker search with autocomplete | 3h |
| 6.1.2 | Create CompanyCard component | Company overview display | 1h |
| 6.1.3 | Build CompanyPage | Full company view page | 3h |
| 6.1.4 | Add company hooks | useCompany, useCompanies | 1h |

### Epic 6.2: Insight Display
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 6.2.1 | Build InsightCard component | Single insight display | 2h |
| 6.2.2 | Create InsightList component | Filterable insight list | 2h |
| 6.2.3 | Build InsightDetail modal | Expanded insight view | 2h |
| 6.2.4 | Create CategoryBadge component | Category visualization | 1h |
| 6.2.5 | Build ConfidenceIndicator | Confidence display | 1h |
| 6.2.6 | Add insight filtering | Filter by category, date, confidence | 2h |

### Epic 6.3: Timeline Visualization
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 6.3.1 | Build Timeline component | Main timeline visualization | 6h |
| 6.3.2 | Create TimelineItem component | Individual timeline entries | 2h |
| 6.3.3 | Build TimelineFilter component | Filter controls | 2h |
| 6.3.4 | Add timeline interactions | Expand, collapse, zoom | 3h |
| 6.3.5 | Implement "new vs repeated" styling | Visual differentiation | 2h |

### Epic 6.4: Evidence & Citations
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 6.4.1 | Build EvidenceCard component | Citation display | 2h |
| 6.4.2 | Create SourceQuote component | Quoted text display | 1h |
| 6.4.3 | Build DocumentLink component | Link to source document | 1h |
| 6.4.4 | Add document excerpt preview | Show context in modal | 3h |

### Epic 6.5: Analysis Flow
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 6.5.1 | Build AnalysisPage | Full analysis workflow | 4h |
| 6.5.2 | Create analysis progress UI | Show pipeline progress | 2h |
| 6.5.3 | Add polling for status | Real-time status updates | 1h |

### Epic 6.6: Frontend Tests
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 6.6.1 | Component unit tests | All major components | 4h |
| 6.6.2 | Hook tests | Custom hook tests | 2h |
| 6.6.3 | Integration tests | Store + API tests | 2h |

**Phase 6 Total: ~51 hours**

---

## Phase 7: E2E Testing & Polish (Week 7-8)

### Epic 7.1: E2E Test Suites
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 7.1.1 | Create page object models | POM for all pages | 3h |
| 7.1.2 | Write company search E2E tests | Search and select flow | 2h |
| 7.1.3 | Write document upload E2E tests | Full upload flow | 2h |
| 7.1.4 | Write analysis flow E2E tests | Trigger and view analysis | 3h |
| 7.1.5 | Write timeline interaction E2E tests | Timeline navigation | 2h |

### Epic 7.2: Error Handling & Edge Cases
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 7.2.1 | Add frontend error boundaries | Graceful error handling | 2h |
| 7.2.2 | Implement retry logic | API retry mechanisms | 1h |
| 7.2.3 | Add loading states | Skeleton loaders | 2h |
| 7.2.4 | Handle empty states | No data UI | 1h |

### Epic 7.3: Performance Optimization
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 7.3.1 | Add API response caching | Cache frequent requests | 2h |
| 7.3.2 | Implement pagination | Paginate large lists | 2h |
| 7.3.3 | Optimize bundle size | Code splitting | 2h |
| 7.3.4 | Add lazy loading | Lazy load components | 1h |

### Epic 7.4: Documentation
| ID | Task | Description | Estimate |
|----|------|-------------|----------|
| 7.4.1 | Write API documentation | OpenAPI + examples | 3h |
| 7.4.2 | Write development setup guide | Local dev instructions | 2h |
| 7.4.3 | Write NLP pipeline documentation | DSPy programs docs | 2h |
| 7.4.4 | Create architecture diagrams | System diagrams | 2h |

**Phase 7 Total: ~34 hours**

---

## Summary

| Phase | Description | Estimated Hours |
|-------|-------------|-----------------|
| 1 | Foundation & Infrastructure | 35h |
| 2 | Document Ingestion Pipeline | 47h |
| 3 | LlamaIndex Integration | 30h |
| 4 | DSPy Programs | 41h |
| 5 | Analysis API & Services | 29h |
| 6 | Frontend Features | 51h |
| 7 | E2E Testing & Polish | 34h |
| **Total** | | **~267 hours** |

---

## Recommended Execution Order

For a solo developer or small team, I recommend this execution sequence:

1. **Phase 1** → Get the skeleton running end-to-end
2. **Phase 2** → Can upload and view documents
3. **Phase 3** → Documents are indexed and searchable
4. **Phase 4** → Core NLP extraction working
5. **Phase 5** → Full API complete
6. **Phase 6** → Full UI complete
7. **Phase 7** → Production-ready quality

### Parallel Tracks (if 2+ developers)

- **Track A (Backend)**: Phase 1.1, 1.2, 2.1-2.3, 3.x, 4.x, 5.x
- **Track B (Frontend)**: Phase 1.3, 2.4, 6.x
- **Sync Points**: After Phase 1, After Phase 5

---

## Approval Required

**Please review this task breakdown and confirm:**

1. ✅ Scope is correct
2. ✅ Priorities are aligned
3. ✅ Any phases to skip or defer
4. ✅ Any additional requirements

**Reply with "approved" to begin execution, or provide feedback for adjustments.**
