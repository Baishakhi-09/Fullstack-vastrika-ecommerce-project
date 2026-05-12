from __future__ import annotations

import logging
from collections.abc import Iterable
from threading import Lock

import spacy
from django.conf import settings
from spacy.language import Language
from spacy.tokens import Doc

from apps.ai.services.nlp.model_registry import (
    SPACY_MODELS,
)


logger = logging.getLogger(__name__)


class NLPPipeline:
    """
    Enterprise NLP pipeline service.
    """

    _pipelines: dict[str, Language] = {}

    _lock = Lock()

    DEFAULT_MODEL_ALIAS = "english"

    @classmethod
    def get_pipeline(
        cls,
        model_alias: str | None = None,
    ) -> Language:
        """
        Load and return spaCy pipeline safely.
        """

        model_alias = (
            model_alias
            or cls.DEFAULT_MODEL_ALIAS
        )

        if model_alias not in SPACY_MODELS:
            raise ValueError(
                f"Unsupported NLP model alias: "
                f"{model_alias}"
            )

        with cls._lock:

            if model_alias not in cls._pipelines:

                logger.info(
                    "Loading spaCy NLP model: %s",
                    model_alias,
                )

                spacy.prefer_gpu()

                model_name = SPACY_MODELS[
                    model_alias
                ]

                cls._pipelines[
                    model_alias
                ] = spacy.load(
                    model_name,
                    disable=[
                        "textcat",
                    ],
                )

                logger.info(
                    "spaCy NLP model loaded: %s",
                    model_name,
                )

        return cls._pipelines[
            model_alias
        ]

    @classmethod
    def process(
        cls,
        text: str,
        model_alias: str | None = None,
    ) -> Doc:
        """
        Process single text document.
        """

        try:
            if not text.strip():
                raise ValueError(
                    "Input text is empty."
                )

            max_length = getattr(
                settings,
                "NLP_MAX_LENGTH",
                100000,
            )

            if len(text) > max_length:
                raise ValueError(
                    "Input exceeds maximum NLP "
                    "processing length."
                )

            pipeline = cls.get_pipeline(
                model_alias=model_alias,
            )

            return pipeline(text)

        except Exception as exc:
            logger.exception(
                "spaCy processing failed: %s",
                exc,
            )

            raise

    @classmethod
    def process_batch(
        cls,
        texts: list[str],
        model_alias: str | None = None,
    ) -> Iterable[Doc]:
        """
        Process batch documents efficiently.
        """

        try:
            if not texts:
                raise ValueError(
                    "Input text batch is empty."
                )

            pipeline = cls.get_pipeline(
                model_alias=model_alias,
            )

            return pipeline.pipe(texts)

        except Exception as exc:
            logger.exception(
                "spaCy batch processing failed: %s",
                exc,
            )

            raise

    @classmethod
    def warmup(
        cls,
        model_alias: str | None = None,
    ) -> None:
        """
        Warm up NLP pipeline.

        Useful for:
        - Docker startup
        - Kubernetes readiness
        - Celery workers
        """

        logger.info(
            "Warming up NLP pipeline..."
        )

        cls.get_pipeline(
            model_alias=model_alias,
        )

    @classmethod
    def is_loaded(
        cls,
        model_alias: str | None = None,
    ) -> bool:
        """
        Check whether pipeline is loaded.
        """

        model_alias = (
            model_alias
            or cls.DEFAULT_MODEL_ALIAS
        )

        return (
            model_alias
            in cls._pipelines
        )

    @classmethod
    def unload_pipeline(
        cls,
        model_alias: str | None = None,
    ) -> None:
        """
        Unload NLP pipeline from memory.
        """

        model_alias = (
            model_alias
            or cls.DEFAULT_MODEL_ALIAS
        )

        with cls._lock:

            if model_alias in cls._pipelines:

                logger.info(
                    "Unloading NLP model: %s",
                    model_alias,
                )

                del cls._pipelines[
                    model_alias
                ]

    @classmethod
    def available_models(
        cls,
    ) -> dict[str, str]:
        """
        Return available model registry.
        """

        return SPACY_MODELS.copy()