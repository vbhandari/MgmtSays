"""DSPy base module with common configuration."""

import logging
from functools import lru_cache

import dspy

from src.config.settings import get_settings


logger = logging.getLogger(__name__)


@lru_cache()
def get_dspy_lm():
    """Get configured DSPy language model."""
    settings = get_settings()

    if settings.llm_provider == "openai":
        lm = dspy.LM(
            model=f"openai/{settings.openai_model}",
            api_key=settings.openai_api_key,
            temperature=settings.llm_temperature,
        )
    elif settings.llm_provider == "anthropic":
        lm = dspy.LM(
            model=f"anthropic/{settings.anthropic_model}",
            api_key=settings.anthropic_api_key,
            temperature=settings.llm_temperature,
        )
    elif settings.llm_provider == "azure":
        lm = dspy.LM(
            model=f"azure/{settings.azure_deployment}",
            api_key=settings.azure_api_key,
            api_base=settings.azure_endpoint,
            api_version=settings.azure_api_version,
            temperature=settings.llm_temperature,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

    return lm


def configure_dspy():
    """Configure DSPy with the language model."""
    lm = get_dspy_lm()
    dspy.configure(lm=lm)
    logger.info("DSPy configured successfully")
