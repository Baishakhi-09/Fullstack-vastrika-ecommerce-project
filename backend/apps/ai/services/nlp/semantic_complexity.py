from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from threading import Lock
from typing import Any

import numpy as np
import torch
from django.conf import settings
from sentence_transformers import (
    SentenceTransformer,
)


logger = logging.getLogger(__name__)


@dataclass(
    frozen=True,
    slots=True,
)
class SemanticComplexityResult:
    """
    Structured semantic complexity result.
    """

    complexity_score: float

    total_sentences: int

    average_similarity: float
    similarity_variance: float

    device: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SemanticComplexityService:
    """
    Enterprise semantic complexity service.
    """

    _model = None

    _lock = Lock()

    DEFAULT_MODEL = getattr(
        settings,
        "SENTENCE_TRANSFORMER_MODEL",
        "all-MiniLM-L6-v2",
    )

    @classmethod
    def get_model(
        cls,
    ) -> SentenceTransformer:
        """
        Load transformer model safely.
        """

        with cls._lock:

            if cls._model is None:

                logger.info(
                    "Loading semantic "
                    "transformer model..."
                )

                device = (
                    "cuda"
                    if torch.cuda.is_available()
                    else "cpu"
                )

                cls._model = (
                    SentenceTransformer(
                        cls.DEFAULT_MODEL,
                        device=device,
                    )
                )

                logger.info(
                    "Semantic transformer "
                    "loaded on %s.",
                    device,
                )

        return cls._model

    @classmethod
    def calculate_complexity(
        cls,
        text: str,
    ) -> SemanticComplexityResult:
        """
        Analyze semantic complexity.
        """

        try:
            if not text.strip():

                return SemanticComplexityResult(
                    complexity_score=0.0,
                    total_sentences=0,
                    average_similarity=0.0,
                    similarity_variance=0.0,
                    device="unknown",
                )

            max_length = getattr(
                settings,
                "NLP_MAX_LENGTH",
                100000,
            )

            if len(text) > max_length:
                raise ValueError(
                    "Input exceeds maximum "
                    "semantic processing length."
                )

            sentences = cls.extract_sentences(
                text,
            )

            if len(sentences) < 2:

                return SemanticComplexityResult(
                    complexity_score=0.0,
                    total_sentences=1,
                    average_similarity=1.0,
                    similarity_variance=0.0,
                    device=(
                        "cuda"
                        if torch.cuda.is_available()
                        else "cpu"
                    ),
                )

            model = cls.get_model()

            embeddings = model.encode(
                sentences,
                convert_to_numpy=True,
                batch_size=16,
                show_progress_bar=False,
            )

            similarity_matrix = np.inner(
                embeddings,
                embeddings,
            )

            average_similarity = float(
                np.mean(similarity_matrix)
            )

            similarity_variance = float(
                np.var(similarity_matrix)
            )

            complexity_score = float(
                np.std(similarity_matrix)
            )

            logger.info(
                "Semantic complexity analysis "
                "completed successfully."
            )

            return SemanticComplexityResult(
                complexity_score=round(
                    complexity_score,
                    4,
                ),
                total_sentences=len(
                    sentences
                ),
                average_similarity=round(
                    average_similarity,
                    4,
                ),
                similarity_variance=round(
                    similarity_variance,
                    4,
                ),
                device=(
                    "cuda"
                    if torch.cuda.is_available()
                    else "cpu"
                ),
            )

        except Exception as exc:

            logger.exception(
                "Semantic complexity "
                "analysis failed: %s",
                exc,
            )

            raise

    @staticmethod
    def extract_sentences(
        text: str,
    ) -> list[str]:
        """
        Basic sentence extraction.

        Future upgrade:
        Replace with spaCy tokenizer.
        """

        return [
            sentence.strip()
            for sentence in text.split(".")
            if sentence.strip()
        ]

    @classmethod
    def calculate_batch_complexity(
        cls,
        texts: list[str],
    ) -> list[
        SemanticComplexityResult
    ]:
        """
        Batch semantic analysis.
        """

        try:
            if not texts:
                return []

            return [
                cls.calculate_complexity(
                    text
                )
                for text in texts
            ]

        except Exception as exc:

            logger.exception(
                "Batch semantic analysis "
                "failed: %s",
                exc,
            )

            raise

    @classmethod
    def warmup(cls) -> None:
        """
        Warm up semantic model.

        Useful for:
        - Docker startup
        - Kubernetes readiness
        - Celery workers
        """

        logger.info(
            "Warming up semantic "
            "transformer..."
        )

        cls.get_model()

    @classmethod
    def is_loaded(cls) -> bool:
        """
        Check whether model is loaded.
        """

        return cls._model is not None

    @classmethod
    def unload(cls) -> None:
        """
        Unload semantic model safely.
        """

        with cls._lock:

            if cls._model is not None:

                logger.info(
                    "Unloading semantic "
                    "transformer..."
                )

                cls._model = None

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

    @classmethod
    def current_device(cls) -> str:
        """
        Return active inference device.
        """

        return (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )