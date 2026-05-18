from __future__ import annotations

import logging
from dataclasses import (
    asdict,
    dataclass,
)
from threading import Lock
from typing import Any

from django.conf import settings

from transformers import pipeline
from transformers.pipelines import (
    Pipeline,
)


logger = logging.getLogger(__name__)


# DTOs
@dataclass(
    frozen=True,
    slots=True,
)
class ReadabilityPrediction:
    label: str

    score: float


@dataclass(
    frozen=True,
    slots=True,
)
class ReadabilityResult:
    text_length: int

    truncated: bool

    predictions: list[
        ReadabilityPrediction
    ]

    model_name: str

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize result safely.
        """

        return asdict(self)


# =========================================================
# READABILITY CLASSIFIER
# =========================================================
class AIReadabilityClassifier:
    _classifier: Pipeline | None = None

    _lock = Lock()

    DEFAULT_MODEL = getattr(
        settings,
        "READABILITY_MODEL",
        (
            "distilbert-base-uncased-"
            "finetuned-sst-2-english"
        ),
    )

    MAX_INPUT_LENGTH = getattr(
        settings,
        "READABILITY_MAX_INPUT_LENGTH",
        512,
    )

    @classmethod
    def get_classifier(
        cls,
    ) -> Pipeline:
        with cls._lock:

            if cls._classifier is None:

                logger.info(
                    (
                        "Loading readability "
                        "classifier model: %s"
                    ),
                    cls.DEFAULT_MODEL,
                )

                cls._classifier = pipeline(
                    task="text-classification",
                    model=cls.DEFAULT_MODEL,
                    truncation=True,
                )

                logger.info(
                    (
                        "Readability classifier "
                        "loaded successfully."
                    )
                )

        return cls._classifier

    @classmethod
    def classify(
        cls,
        text: str,
    ) -> ReadabilityResult:
        try:
            if not text.strip():
                raise ValueError(
                    "Input text is empty."
                )

            logger.info(
                "Running readability analysis."
            )

            classifier = cls.get_classifier()

            truncated = (
                len(text)
                > cls.MAX_INPUT_LENGTH
            )

            processed_text = text[
                : cls.MAX_INPUT_LENGTH
            ]

            predictions_raw = classifier(
                processed_text,
            )

            predictions = [
                ReadabilityPrediction(
                    label=item["label"],
                    score=round(
                        float(
                            item["score"]
                        ),
                        4,
                    ),
                )
                for item in predictions_raw
            ]

            logger.info(
                (
                    "Readability analysis "
                    "completed successfully."
                )
            )

            return ReadabilityResult(
                text_length=len(text),
                truncated=truncated,
                predictions=predictions,
                model_name=cls.DEFAULT_MODEL,
            )

        except Exception as exc:
            logger.exception(
                (
                    "Readability analysis "
                    "failed: %s"
                ),
                exc,
            )

            raise

    @classmethod
    def classify_batch(
        cls,
        texts: list[str],
    ) -> list[ReadabilityResult]:
        try:
            if not texts:
                raise ValueError(
                    "Input text batch is empty."
                )

            logger.info(
                (
                    "Running batch readability "
                    "analysis."
                )
            )

            return [
                cls.classify(text)
                for text in texts
            ]

        except Exception as exc:
            logger.exception(
                (
                    "Batch readability "
                    "analysis failed: %s"
                ),
                exc,
            )

            raise

    @classmethod
    def warmup(
        cls,
    ) -> None:
        logger.info(
            (
                "Warming up readability "
                "classifier..."
            )
        )

        cls.get_classifier()

    @classmethod
    def unload(
        cls,
    ) -> None:
        with cls._lock:
            if cls._classifier is not None:
                logger.info(
                    (
                        "Unloading readability "
                        "classifier."
                    )
                )

                cls._classifier = None

    @classmethod
    def is_loaded(
        cls,
    ) -> bool:
        return (
            cls._classifier
            is not None
        )