from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from threading import Lock
from typing import Any

import language_tool_python
from django.conf import settings


logger = logging.getLogger(__name__)


@dataclass(
    frozen=True,
    slots=True,
)
class GrammarIssue:
    """
    Structured grammar issue DTO.
    """

    message: str
    rule_id: str

    offset: int
    error_length: int

    category: str

    replacements: list[str]


@dataclass(
    frozen=True,
    slots=True,
)
class GrammarCheckResult:
    """
    Structured grammar analysis result.
    """

    total_issues: int
    issues: list[GrammarIssue]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GrammarService:
    """
    Enterprise grammar analysis service.
    """

    _tool = None

    _lock = Lock()

    DEFAULT_LANGUAGE = getattr(
        settings,
        "DEFAULT_GRAMMAR_LANGUAGE",
        "en-US",
    )

    @classmethod
    def get_tool(
        cls,
    ) -> language_tool_python.LanguageTool:
        """
        Safely load grammar engine.
        """

        with cls._lock:

            if cls._tool is None:

                logger.info(
                    "Loading grammar engine..."
                )

                cls._tool = (
                    language_tool_python
                    .LanguageTool(
                        cls.DEFAULT_LANGUAGE
                    )
                )

                logger.info(
                    "Grammar engine loaded."
                )

        return cls._tool

    @classmethod
    def check(
        cls,
        text: str,
    ) -> GrammarCheckResult:
        """
        Analyze grammar safely.
        """

        try:
            if not text.strip():
                return GrammarCheckResult(
                    total_issues=0,
                    issues=[],
                )

            max_length = getattr(
                settings,
                "NLP_MAX_LENGTH",
                100000,
            )

            if len(text) > max_length:
                raise ValueError(
                    "Input exceeds maximum "
                    "grammar processing length."
                )

            tool = cls.get_tool()

            matches = tool.check(text)

            issues = [
                GrammarIssue(
                    message=match.message,
                    rule_id=match.ruleId,
                    offset=match.offset,
                    error_length=match.errorLength,
                    category=(
                        match.category
                        if match.category
                        else "unknown"
                    ),
                    replacements=(
                        match.replacements
                    ),
                )
                for match in matches
            ]

            logger.info(
                "Grammar analysis completed "
                "with %s issues.",
                len(issues),
            )

            return GrammarCheckResult(
                total_issues=len(issues),
                issues=issues,
            )

        except Exception as exc:

            logger.exception(
                "Grammar analysis failed: %s",
                exc,
            )

            raise

    @classmethod
    def check_batch(
        cls,
        texts: list[str],
    ) -> list[GrammarCheckResult]:
        """
        Batch grammar analysis.
        """

        try:
            if not texts:
                return []

            return [
                cls.check(text)
                for text in texts
            ]

        except Exception as exc:

            logger.exception(
                "Batch grammar analysis failed: %s",
                exc,
            )

            raise

    @classmethod
    def warmup(cls) -> None:
        """
        Warm up grammar engine.

        Useful for:
        - Docker startup
        - Kubernetes readiness
        - Celery workers
        """

        logger.info(
            "Warming up grammar engine..."
        )

        cls.get_tool()

    @classmethod
    def is_loaded(cls) -> bool:
        """
        Check whether grammar engine
        is initialized.
        """

        return cls._tool is not None

    @classmethod
    def unload(cls) -> None:
        """
        Unload grammar engine safely.
        """

        with cls._lock:

            if cls._tool is not None:

                logger.info(
                    "Unloading grammar engine..."
                )

                cls._tool.close()

                cls._tool = None

    @classmethod
    def change_language(
        cls,
        language: str,
    ) -> None:
        """
        Dynamically switch grammar language.
        """

        with cls._lock:

            logger.info(
                "Switching grammar language "
                "to %s",
                language,
            )

            if cls._tool is not None:
                cls._tool.close()

            cls._tool = (
                language_tool_python
                .LanguageTool(language)
            )

            cls.DEFAULT_LANGUAGE = (
                language
            )