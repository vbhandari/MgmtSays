"""DSPy-based question answerer with citations."""

import logging
from typing import Any

import dspy

from src.nlp.dspy_programs.base import configure_dspy


logger = logging.getLogger(__name__)


class QuestionAnswerSignature(dspy.Signature):
    """Answer questions about company disclosures with citations."""
    
    question: str = dspy.InputField(
        desc="Question about the company's strategy, initiatives, or disclosures"
    )
    context: str = dspy.InputField(
        desc="Relevant text chunks from company disclosures"
    )
    company_name: str = dspy.InputField(
        desc="Name of the company"
    )
    
    answer: str = dspy.OutputField(
        desc="Comprehensive answer to the question"
    )
    citations: list[str] = dspy.OutputField(
        desc="List of direct quotes from the context that support the answer"
    )
    confidence: float = dspy.OutputField(
        desc="Confidence in the answer 0-1"
    )
    related_topics: list[str] = dspy.OutputField(
        desc="Related topics the user might want to explore"
    )


class QuestionAnswerer(dspy.Module):
    """
    Answers questions about company disclosures with proper citations.
    
    Features:
    - Grounded answers based on retrieved context
    - Direct quotes as citations
    - Confidence scoring
    - Related topic suggestions
    """

    def __init__(self):
        super().__init__()
        configure_dspy()
        
        self.answerer = dspy.ChainOfThought(QuestionAnswerSignature)

    def forward(
        self,
        question: str,
        context: str | list[str],
        company_name: str,
    ) -> dict[str, Any]:
        """
        Answer a question based on retrieved context.
        
        Args:
            question: User's question
            context: Retrieved text chunks (str or list of str)
            company_name: Company name for context
            
        Returns:
            Answer dict with citations
        """
        # Combine context if list
        if isinstance(context, list):
            context_str = "\n\n---\n\n".join(context)
        else:
            context_str = context

        result = self.answerer(
            question=question,
            context=context_str,
            company_name=company_name,
        )

        return {
            "answer": result.answer,
            "citations": result.citations,
            "confidence": self._normalize_confidence(result.confidence),
            "related_topics": result.related_topics,
        }

    def _normalize_confidence(self, confidence: float) -> float:
        """Normalize confidence to 0-1 range."""
        try:
            conf = float(confidence)
            return max(0.0, min(1.0, conf))
        except (ValueError, TypeError):
            return 0.5

    async def answer_with_retrieval(
        self,
        question: str,
        retrieval_results: list[dict],
        company_name: str,
    ) -> dict[str, Any]:
        """
        Answer a question using retrieval results.
        
        Args:
            question: User's question
            retrieval_results: Results from HybridRetriever
            company_name: Company name
            
        Returns:
            Answer with citations mapped to source documents
        """
        # Build context from retrieval results
        context_parts = []
        source_map = {}  # Map quotes to source documents

        for i, result in enumerate(retrieval_results):
            text = result.get("text", "")
            doc_id = result.get("document_id")
            chunk_id = result.get("chunk_id")
            metadata = result.get("metadata", {})

            context_parts.append(f"[Source {i+1}]\n{text}")
            source_map[f"Source {i+1}"] = {
                "document_id": doc_id,
                "chunk_id": chunk_id,
                "metadata": metadata,
            }

        context_str = "\n\n".join(context_parts)

        # Get answer
        answer_result = self.forward(
            question=question,
            context=context_str,
            company_name=company_name,
        )

        # Enrich citations with source information
        enriched_citations = []
        for citation in answer_result["citations"]:
            citation_info = {
                "quote": citation,
                "sources": [],
            }
            
            # Find which sources this quote might come from
            for source_key, source_info in source_map.items():
                if citation in context_str:
                    # Try to map to specific source
                    for part in context_parts:
                        if citation in part:
                            source_num = part.split("]")[0].replace("[", "")
                            if source_num in source_map:
                                citation_info["sources"].append(source_map[source_num])
                                break

            enriched_citations.append(citation_info)

        return {
            "answer": answer_result["answer"],
            "citations": enriched_citations,
            "confidence": answer_result["confidence"],
            "related_topics": answer_result["related_topics"],
            "sources_used": list(source_map.values()),
        }


class MultiHopQuestionAnswerer(dspy.Module):
    """
    Handles complex questions requiring multiple retrieval steps.
    
    Decomposes complex questions, retrieves for each sub-question,
    and synthesizes a comprehensive answer.
    """

    def __init__(self, base_answerer: QuestionAnswerer | None = None):
        super().__init__()
        configure_dspy()
        
        self.base_answerer = base_answerer or QuestionAnswerer()
        self.decomposer = dspy.ChainOfThought(
            "question -> sub_questions: list[str]"
        )

    def forward(
        self,
        question: str,
        retriever_fn,  # Callable to retrieve context
        company_name: str,
    ) -> dict[str, Any]:
        """
        Answer complex multi-hop question.
        
        Args:
            question: Complex question
            retriever_fn: Function to retrieve context for a query
            company_name: Company name
            
        Returns:
            Comprehensive answer
        """
        # Decompose question
        decomposition = self.decomposer(question=question)
        sub_questions = decomposition.sub_questions

        # Collect all context
        all_context = []
        sub_answers = []

        for sub_q in sub_questions:
            # Retrieve context for sub-question
            context = retriever_fn(sub_q)
            all_context.extend(context)

            # Get sub-answer
            sub_answer = self.base_answerer.forward(
                question=sub_q,
                context=context,
                company_name=company_name,
            )
            sub_answers.append({
                "sub_question": sub_q,
                **sub_answer,
            })

        # Synthesize final answer
        final_answer = self.base_answerer.forward(
            question=question,
            context=all_context,
            company_name=company_name,
        )

        return {
            **final_answer,
            "sub_questions": sub_answers,
            "decomposed": True,
        }
