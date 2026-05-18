from __future__ import annotations

import hashlib
import logging
import re
import time
import unicodedata
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Literal

from apps.ai.services.cache_service import AsyncCacheService


logger = logging.getLogger(__name__)


ReadabilityLevel = Literal[
    "easy",
    "medium",
    "hard",
    "unknown",
]


@dataclass(slots=True)
class ReadabilityResult:
    reading_ease_score: float
    grade_level: float
    readability_level: ReadabilityLevel
    average_sentence_length: float
    average_word_length: float
    difficult_word_count: int
    estimated_reading_time_minutes: float
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ReadabilityService:
    WORDS_PER_MINUTE = 200

    @classmethod
    async def analyze(
        cls,
        content: str,
    ) -> ReadabilityResult:
        start_time = time.perf_counter()

        try:
            normalized_content = cls.normalize_text(
                content,
            )

            if not normalized_content:
                return cls.empty_result()

            cache_key = cls.generate_cache_key(
                normalized_content,
            )

            cached_result = await AsyncCacheService.get(
                cache_key,
            )

            if cached_result:
                logger.info(
                    "Readability analysis loaded from cache.",
                )

                return ReadabilityResult(
                    **cached_result
                )

            sentences = cls.extract_sentences(
                normalized_content,
            )

            words = cls.extract_words(
                normalized_content,
            )

            if not words or not sentences:
                return cls.empty_result()

            total_words = len(words)
            total_sentences = len(sentences)

            total_syllables = sum(
                cls.count_syllables(word)
                for word in words
            )

            average_sentence_length = (
                total_words / total_sentences
            )

            average_word_length = (
                sum(len(word) for word in words)
                / total_words
            )

            reading_ease_score = (
                cls.calculate_flesch_reading_ease(
                    total_words=total_words,
                    total_sentences=(
                        total_sentences
                    ),
                    total_syllables=(
                        total_syllables
                    ),
                )
            )

            grade_level = (
                cls.calculate_flesch_kincaid_grade(
                    total_words=total_words,
                    total_sentences=(
                        total_sentences
                    ),
                    total_syllables=(
                        total_syllables
                    ),
                )
            )

            readability_level = (
                cls.detect_readability_level(
                    reading_ease_score
                )
            )

            difficult_word_count = len(
                [
                    word
                    for word in words
                    if cls.count_syllables(word)
                    >= 3
                ]
            )

            estimated_reading_time_minutes = (
                round(
                    total_words
                    / cls.WORDS_PER_MINUTE,
                    2,
                )
            )

            recommendations = (
                cls.generate_recommendations(
                    reading_ease_score=(
                        reading_ease_score
                    ),
                    average_sentence_length=(
                        average_sentence_length
                    ),
                    difficult_word_count=(
                        difficult_word_count
                    ),
                )
            )

            result = ReadabilityResult(
                reading_ease_score=round(
                    reading_ease_score,
                    2,
                ),
                grade_level=round(
                    grade_level,
                    2,
                ),
                readability_level=(
                    readability_level
                ),
                average_sentence_length=round(
                    average_sentence_length,
                    2,
                ),
                average_word_length=round(
                    average_word_length,
                    2,
                ),
                difficult_word_count=(
                    difficult_word_count
                ),
                estimated_reading_time_minutes=(
                    estimated_reading_time_minutes
                ),
                recommendations=recommendations,
            )

            await AsyncCacheService.set(
                key=cache_key,
                value=result.to_dict(),
                timeout=1800,
            )

            elapsed_time = round(
                time.perf_counter()
                - start_time,
                4,
            )

            logger.info(
                "Readability analysis completed "
                "in %s seconds.",
                elapsed_time,
            )

            return result

        except Exception as exc:
            logger.exception(
                "Readability analysis failed: %s",
                exc,
            )

            return cls.empty_result()

    @staticmethod
    def normalize_text(text: str) -> str:
        text = unicodedata.normalize(
            "NFKC",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    @staticmethod
    def extract_sentences(
        text: str,
    ) -> List[str]:
        return [
            sentence.strip()
            for sentence in re.split(
                r"[.!?]+",
                text,
            )
            if sentence.strip()
        ]

    @staticmethod
    def extract_words(
        text: str,
    ) -> List[str]:
        """
        Extract words safely.
        """

        return re.findall(
            r"\b\w+\b",
            text.lower(),
        )

    @staticmethod
    def count_syllables(
        word: str,
    ) -> int:
        word = word.lower()

        vowels = "aeiouy"

        syllable_count = 0
        previous_char_was_vowel = False

        for char in word:
            is_vowel = char in vowels

            if (
                is_vowel
                and not previous_char_was_vowel
            ):
                syllable_count += 1

            previous_char_was_vowel = (
                is_vowel
            )

        if word.endswith("e"):
            syllable_count = max(
                1,
                syllable_count - 1,
            )

        return max(1, syllable_count)

    @staticmethod
    def calculate_flesch_reading_ease(
        total_words: int,
        total_sentences: int,
        total_syllables: int,
    ) -> float:
        return (
            206.835
            - 1.015
            * (
                total_words
                / total_sentences
            )
            - 84.6
            * (
                total_syllables
                / total_words
            )
        )

    @staticmethod
    def calculate_flesch_kincaid_grade(
        total_words: int,
        total_sentences: int,
        total_syllables: int,
    ) -> float:
        return (
            0.39
            * (
                total_words
                / total_sentences
            )
            + 11.8
            * (
                total_syllables
                / total_words
            )
            - 15.59
        )

    @staticmethod
    def detect_readability_level(
        reading_ease_score: float,
    ) -> ReadabilityLevel:
        if reading_ease_score >= 70:
            return "easy"

        if reading_ease_score >= 50:
            return "medium"

        return "hard"

    @staticmethod
    def generate_recommendations(
        reading_ease_score: float,
        average_sentence_length: float,
        difficult_word_count: int,
    ) -> List[str]:
        recommendations = []

        if reading_ease_score < 60:
            recommendations.append(
                "Use simpler language "
                "for better readability."
            )

        if average_sentence_length > 20:
            recommendations.append(
                "Reduce sentence length "
                "for easier reading."
            )

        if difficult_word_count > 20:
            recommendations.append(
                "Reduce complex words "
                "to improve clarity."
            )

        if not recommendations:
            recommendations.append(
                "Content readability "
                "looks well optimized."
            )

        return recommendations

    @staticmethod
    def generate_cache_key(
        content: str,
    ) -> str:
        content_hash = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

        return (
            f"readability-analysis:"
            f"{content_hash}"
        )

    @staticmethod
    def empty_result() -> ReadabilityResult:
        """
        Return safe empty result.
        """

        return ReadabilityResult(
            reading_ease_score=0,
            grade_level=0,
            readability_level="unknown",
            average_sentence_length=0,
            average_word_length=0,
            difficult_word_count=0,
            estimated_reading_time_minutes=0,
            recommendations=[
                "Content is empty."
            ],
        )