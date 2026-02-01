"""Background job processor for document processing and analysis."""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Awaitable
from datetime import datetime

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    """Job representation."""
    id: str
    type: str
    status: JobStatus
    data: dict[str, Any]
    progress: int = 0
    error_message: str | None = None
    created_at: datetime = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class JobQueue:
    """Simple in-memory job queue for background processing."""
    
    def __init__(self):
        self._jobs: dict[str, Job] = {}
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._handlers: dict[str, Callable[[Job], Awaitable[None]]] = {}
        self._running = False
        self._workers: list[asyncio.Task] = []
    
    def register_handler(
        self,
        job_type: str,
        handler: Callable[[Job], Awaitable[None]],
    ):
        """Register a handler for a job type."""
        self._handlers[job_type] = handler
    
    async def enqueue(
        self,
        job_id: str,
        job_type: str,
        data: dict[str, Any],
    ) -> Job:
        """Add a job to the queue."""
        job = Job(
            id=job_id,
            type=job_type,
            status=JobStatus.PENDING,
            data=data,
        )
        self._jobs[job_id] = job
        await self._queue.put(job_id)
        logger.info(f"Job {job_id} ({job_type}) enqueued")
        return job
    
    def get_job(self, job_id: str) -> Job | None:
        """Get a job by ID."""
        return self._jobs.get(job_id)
    
    def update_progress(self, job_id: str, progress: int):
        """Update job progress."""
        if job := self._jobs.get(job_id):
            job.progress = min(100, max(0, progress))
    
    async def start(self, num_workers: int = 2):
        """Start job processing workers."""
        self._running = True
        for i in range(num_workers):
            task = asyncio.create_task(self._worker(i))
            self._workers.append(task)
        logger.info(f"Started {num_workers} job workers")
    
    async def stop(self):
        """Stop all workers."""
        self._running = False
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("Job workers stopped")
    
    async def _worker(self, worker_id: int):
        """Worker process that handles jobs."""
        logger.info(f"Worker {worker_id} started")
        
        while self._running:
            try:
                # Wait for a job with timeout
                try:
                    job_id = await asyncio.wait_for(
                        self._queue.get(),
                        timeout=1.0,
                    )
                except asyncio.TimeoutError:
                    continue
                
                job = self._jobs.get(job_id)
                if not job:
                    continue
                
                # Get handler
                handler = self._handlers.get(job.type)
                if not handler:
                    logger.error(f"No handler for job type: {job.type}")
                    job.status = JobStatus.FAILED
                    job.error_message = f"No handler for job type: {job.type}"
                    continue
                
                # Process job
                logger.info(f"Worker {worker_id} processing job {job_id}")
                job.status = JobStatus.PROCESSING
                job.started_at = datetime.utcnow()
                
                try:
                    await handler(job)
                    job.status = JobStatus.COMPLETED
                    job.progress = 100
                    logger.info(f"Job {job_id} completed successfully")
                except Exception as e:
                    logger.error(f"Job {job_id} failed: {e}")
                    job.status = JobStatus.FAILED
                    job.error_message = str(e)
                finally:
                    job.completed_at = datetime.utcnow()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")


# Global job queue instance
job_queue = JobQueue()


async def process_document_job(job: Job):
    """Process a document upload job."""
    from src.core.database import async_session_maker
    from src.repositories.document_repository import DocumentRepository
    from src.nlp.ingestion.parser import DocumentParser
    from src.nlp.chunking.semantic import SemanticChunker
    from src.nlp.indexing.vector_store import VectorStoreManager
    from src.storage.local_storage import LocalStorage
    from src.core.config import get_settings
    
    settings = get_settings()
    document_id = job.data["document_id"]
    company_id = job.data["company_id"]
    file_path = job.data["file_path"]
    
    async with async_session_maker() as db:
        doc_repo = DocumentRepository(db)
        
        try:
            # Update status
            await doc_repo.update_processing_status(document_id, "processing")
            job_queue.update_progress(job.id, 10)
            
            # Parse document
            storage = LocalStorage(settings.upload_dir)
            file_content = await storage.load(file_path)
            
            parser = DocumentParser()
            parsed = parser.parse(file_content, file_path)
            job_queue.update_progress(job.id, 30)
            
            # Chunk document
            chunker = SemanticChunker()
            chunks = await chunker.chunk(
                parsed.content,
                metadata={
                    "document_id": document_id,
                    "company_id": company_id,
                    "document_type": parsed.document_type,
                    "sections": [s.title for s in parsed.sections],
                },
            )
            job_queue.update_progress(job.id, 60)
            
            # Index chunks
            vector_store = VectorStoreManager(
                host=settings.chroma_host,
                port=settings.chroma_port,
            )
            
            collection_name = f"company_{company_id}"
            await vector_store.add_chunks(collection_name, chunks)
            job_queue.update_progress(job.id, 90)
            
            # Update document status
            await doc_repo.update_processing_status(
                document_id,
                "completed",
                chunk_count=len(chunks),
            )
            job_queue.update_progress(job.id, 100)
            
            logger.info(f"Document {document_id} processed: {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            await doc_repo.update_processing_status(
                document_id,
                "failed",
                error_message=str(e),
            )
            raise


async def run_analysis_job(job: Job):
    """Run analysis job for extracting initiatives."""
    from src.core.database import async_session_maker
    from src.repositories.analysis_repository import AnalysisRepository
    from src.repositories.document_repository import DocumentRepository
    from src.nlp.retrieval.hybrid import HybridRetriever
    from src.nlp.indexing.vector_store import VectorStoreManager
    from src.nlp.dspy_programs.base import configure_dspy
    from src.nlp.dspy_programs.initiative_extractor import InitiativeExtractor
    from src.nlp.dspy_programs.deduplicator import InitiativeDeduplicator
    from src.core.config import get_settings
    
    settings = get_settings()
    analysis_id = job.data["analysis_id"]
    company_id = job.data["company_id"]
    document_ids = job.data.get("document_ids")
    
    # Configure DSPy
    configure_dspy(
        settings.llm_provider,
        settings.openai_api_key or settings.anthropic_api_key,
    )
    
    async with async_session_maker() as db:
        analysis_repo = AnalysisRepository(db)
        doc_repo = DocumentRepository(db)
        
        try:
            # Update status
            await analysis_repo.update_status(analysis_id, "processing")
            job_queue.update_progress(job.id, 10)
            
            # Get documents
            documents = await doc_repo.get_by_company(company_id)
            if document_ids:
                documents = [d for d in documents if d.id in document_ids]
            
            # Initialize retriever
            vector_store = VectorStoreManager(
                host=settings.chroma_host,
                port=settings.chroma_port,
            )
            
            collection_name = f"company_{company_id}"
            retriever = HybridRetriever(
                vector_store=vector_store,
                collection_name=collection_name,
            )
            
            # Extract initiatives from each document
            extractor = InitiativeExtractor()
            all_initiatives = []
            
            for i, doc in enumerate(documents):
                # Retrieve content for this document
                chunks = await retriever.retrieve(
                    query="strategic initiatives goals plans investments expansion",
                    top_k=50,
                    filter_metadata={"document_id": doc.id},
                )
                
                if chunks:
                    context = "\n\n".join([c.text for c in chunks])
                    initiatives = extractor.extract(context, doc.title)
                    all_initiatives.extend(initiatives)
                
                progress = 10 + int((i + 1) / len(documents) * 60)
                job_queue.update_progress(job.id, progress)
            
            # Deduplicate initiatives
            deduplicator = InitiativeDeduplicator()
            deduplicated = deduplicator.deduplicate(all_initiatives)
            job_queue.update_progress(job.id, 85)
            
            # Store initiatives
            for initiative in deduplicated:
                await analysis_repo.create_initiative(
                    company_id=company_id,
                    analysis_id=analysis_id,
                    initiative=initiative,
                )
            
            # Update analysis status
            await analysis_repo.update_status(
                analysis_id,
                "completed",
                initiative_count=len(deduplicated),
            )
            job_queue.update_progress(job.id, 100)
            
            logger.info(f"Analysis {analysis_id} completed: {len(deduplicated)} initiatives")
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            await analysis_repo.update_status(
                analysis_id,
                "failed",
                error_message=str(e),
            )
            raise


def register_job_handlers():
    """Register all job handlers."""
    job_queue.register_handler("process_document", process_document_job)
    job_queue.register_handler("run_analysis", run_analysis_job)
