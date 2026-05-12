from __future__ import annotations

import hashlib
import logging
import re
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Literal

from apps.ai.services.cache_service import AsyncCacheService


logger = logging.getLogger(__name__)


SearchIntentType = Literal[
    "informational",
    "transactional",
    "navigational",
    "general",
    "unknown",
]


DEFAULT_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
}


@dataclass(slots=True)
class KeywordData:
    keyword: str
    count: int
    density: float


@dataclass(slots=True)
class KeywordAnalysisResult:
    total_words: int
    unique_words: int
    top_keywords: List[KeywordData]
    long_tail_keywords: List[str]
    search_intent: SearchIntentType
    seo_score: int
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KeywordAnalysisService:
    """
    Enterprise keyword analysis service.
    """

    CACHE_TIMEOUT = 60 * 30
    MIN_KEYWORD_LENGTH = 3
    MAX_TOP_KEYWORDS = 10
    LONG_TAIL_SIZE = 3

    STOP_WORDS = DEFAULT_STOP_WORDS

    INTENT_KEYWORDS = {
        "informational": {
            "how",
            "guide",
            "tutorial",
            "learn",
            "tips",
            "what",
            "why",
        },
        "transactional": {
            "buy",
            "price",
            "purchase",
            "discount",
            "deal",
            "order",
        },
        "navigational": {
            "website",
            "homepage",
            "contact",
            "login",
            "dashboard",
        },
    }

    @classmethod
    async def analyze(cls, content: str) -> KeywordAnalysisResult:
        """
        Main keyword analysis pipeline.
        """

        try:
            normalized_content = cls.normalize_text(content)

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
                    "Keyword analysis loaded from cache.",
                )

                return KeywordAnalysisResult(**cached_result)

            extracted_keywords = cls.extract_keywords(
                normalized_content,
            )

            if not extracted_keywords:
                return cls.empty_result()

            keyword_counter = Counter(extracted_keywords)

            total_words = len(extracted_keywords)
            unique_words = len(keyword_counter)

            top_keywords = cls.build_keyword_data(
                keyword_counter=keyword_counter,
                total_words=total_words,
            )

            long_tail_keywords = cls.generate_long_tail_keywords(
                normalized_content,
            )

            search_intent = cls.detect_search_intent(
                normalized_content,
            )

            seo_score = cls.calculate_seo_score(
                total_words=total_words,
                unique_words=unique_words,
                keyword_data=top_keywords,
            )

            recommendations = cls.generate_recommendations(
                seo_score=seo_score,
                total_words=total_words,
                keyword_data=top_keywords,
            )

            result = KeywordAnalysisResult(
                total_words=total_words,
                unique_words=unique_words,
                top_keywords=top_keywords,
                long_tail_keywords=long_tail_keywords,
                search_intent=search_intent,
                seo_score=seo_score,
                recommendations=recommendations,
            )

            await AsyncCacheService.set(
                key=cache_key,
                value=result.to_dict(),
                timeout=cls.CACHE_TIMEOUT,
            )

            logger.info(
                "Keyword analysis completed successfully.",
            )

            return result

        except Exception as exc:
            logger.exception(
                "Keyword analysis failed: %s",
                exc,
            )

            return cls.empty_result(
                message="Keyword analysis failed.",
            )

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize multilingual text.
        """

        text = unicodedata.normalize("NFKC", text)
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    @classmethod
    def extract_keywords(cls, text: str) -> List[str]:
        """
        Extract filtered keywords.
        """

        words = text.split()

        return [
            word
            for word in words
            if word not in cls.STOP_WORDS
            and len(word) >= cls.MIN_KEYWORD_LENGTH
            and not word.isnumeric()
        ]

    @classmethod
    def build_keyword_data(
        cls,
        keyword_counter: Counter,
        total_words: int,
    ) -> List[KeywordData]:
        """
        Generate structured keyword metrics.
        """

        keyword_data = []

        for keyword, count in keyword_counter.most_common(
            cls.MAX_TOP_KEYWORDS,
        ):
            density = round(
                (count / total_words) * 100,
                2,
            )

            keyword_data.append(
                KeywordData(
                    keyword=keyword,
                    count=count,
                    density=density,
                )
            )

        return keyword_data

    @classmethod
    def generate_long_tail_keywords(
        cls,
        content: str,
    ) -> List[str]:
        """
        Generate long-tail keywords.
        """

        words = content.split()
        phrases = []

        for index in range(
            len(words) - cls.LONG_TAIL_SIZE + 1,
        ):
            phrase = " ".join(
                words[index:index + cls.LONG_TAIL_SIZE]
            )

            phrases.append(phrase)

        phrase_counter = Counter(phrases)

        return [
            phrase
            for phrase, _ in phrase_counter.most_common(5)
        ]

    @classmethod
    def detect_search_intent(
        cls,
        content: str,
    ) -> SearchIntentType:
        """
        Detect search intent.
        """

        words = set(content.split())

        for intent, keywords in cls.INTENT_KEYWORDS.items():
            if keywords.intersection(words):
                return intent

        return "general"

    @staticmethod
    def calculate_seo_score(
        total_words: int,
        unique_words: int,
        keyword_data: List[KeywordData],
    ) -> int:
        """
        Calculate weighted SEO score.
        """

        score = 0

        if total_words >= 1000:
            score += 35
        elif total_words >= 500:
            score += 25
        elif total_words >= 300:
            score += 15
        else:
            score += 5

        if unique_words >= 150:
            score += 30
        elif unique_words >= 75:
            score += 20
        else:
            score += 10

        optimal_keywords = [
            keyword
            for keyword in keyword_data
            if 1 <= keyword.density <= 3
        ]

        if optimal_keywords:
            score += 35
        else:
            score += 15

        return min(score, 100)

    @staticmethod
    def generate_recommendations(
        seo_score: int,
        total_words: int,
        keyword_data: List[KeywordData],
    ) -> List[str]:
        """
        Generate SEO recommendations.
        """

        recommendations = []

        if total_words < 300:
            recommendations.append(
                "Increase content length for better SEO performance.",
            )

        stuffed_keywords = [
            keyword.keyword
            for keyword in keyword_data
            if keyword.density > 3
        ]

        if stuffed_keywords:
            recommendations.append(
                "Reduce keyword stuffing for: "
                + ", ".join(stuffed_keywords)
            )

        if seo_score >= 80:
            recommendations.append(
                "SEO structure is professionally optimized.",
            )

        if seo_score < 50:
            recommendations.append(
                "Improve keyword diversity and semantic relevance.",
            )

        if not recommendations:
            recommendations.append(
                "Content quality appears balanced and optimized.",
            )

        return recommendations

    @staticmethod
    def generate_cache_key(content: str) -> str:
        """
        Generate stable cache key.
        """

        content_hash = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

        return f"keyword-analysis:{content_hash}"

    @staticmethod
    def empty_result(
        message: str = "Content is empty.",
    ) -> KeywordAnalysisResult:
        """
        Return safe empty result.
        """

        return KeywordAnalysisResult(
            total_words=0,
            unique_words=0,
            top_keywords=[],
            long_tail_keywords=[],
            search_intent="unknown",
            seo_score=0,
            recommendations=[message],
        )