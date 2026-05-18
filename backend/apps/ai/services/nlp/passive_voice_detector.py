from __future__ import annotations

import logging
from dataclasses import (
    asdict,
    dataclass,
)
from typing import Any

from apps.ai.services.nlp.nlp_pipeline import (
    NLPPipeline,
)


logger = logging.getLogger(__name__)


# DTOs
@dataclass(
    frozen=True,
    slots=True,
)
class PassiveSentence:
    sentence: str

    start_char: int

    end_char: int

    matched_rules: list[str]


@dataclass(
    frozen=True,
    slots=True,
)
class PassiveVoiceResult:
    total_passive_sentences: int

    passive_sentences: list[
        PassiveSentence
    ]

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize result safely.
        """

        return asdict(self)


# =========================================================
# PASSIVE VOICE DETECTOR
# =========================================================
class PassiveVoiceDetector:
    PASSIVE_DEPENDENCIES = {
        "auxpass",
        "nsubjpass",
    }

    @classmethod
    def detect(
        cls,
        text: str,
        model_alias: str | None = None,
    ) -> PassiveVoiceResult:
        """
        Detect passive voice sentences.

        Args:
            text:
                Input text.

            model_alias:
                Optional NLP model alias.

        Returns:
            Structured passive voice result.
        """

        try:

            if not text.strip():

                raise ValueError(
                    "Input text is empty."
                )

            logger.info(
                "Running passive voice detection."
            )

            doc = NLPPipeline.process(
                text=text,
                model_alias=model_alias,
            )

            passive_sentences = []

            seen_sentences = set()

            for sentence in doc.sents:

                matched_rules = set()

                for token in sentence:

                    if (
                        token.dep_
                        in cls.PASSIVE_DEPENDENCIES
                    ):

                        matched_rules.add(
                            token.dep_
                        )

                if matched_rules:

                    normalized_sentence = (
                        sentence.text.strip()
                    )

                    if (
                        normalized_sentence
                        in seen_sentences
                    ):
                        continue

                    seen_sentences.add(
                        normalized_sentence
                    )

                    passive_sentences.append(
                        PassiveSentence(
                            sentence=(
                                normalized_sentence
                            ),
                            start_char=(
                                sentence.start_char
                            ),
                            end_char=(
                                sentence.end_char
                            ),
                            matched_rules=sorted(
                                matched_rules
                            ),
                        )
                    )

            logger.info(
                (
                    "Passive voice detection "
                    "completed with %s matches."
                ),
                len(passive_sentences),
            )

            return PassiveVoiceResult(
                total_passive_sentences=(
                    len(passive_sentences)
                ),
                passive_sentences=(
                    passive_sentences
                ),
            )

        except Exception as exc:

            logger.exception(
                (
                    "Passive voice detection "
                    "failed: %s"
                ),
                exc,
            )

            raise

    @classmethod
    def detect_batch(
        cls,
        texts: list[str],
        model_alias: str | None = None,
    ) -> list[PassiveVoiceResult]:
        try:
            if not texts:
                raise ValueError(
                    "Input text batch is empty."
                )

            logger.info(
                (
                    "Running batch passive "
                    "voice detection."
                )
            )

            return [
                cls.detect(
                    text=text,
                    model_alias=model_alias,
                )
                for text in texts
            ]

        except Exception as exc:
            logger.exception(
                (
                    "Batch passive voice "
                    "detection failed: %s"
                ),
                exc,
            )
            
            raise