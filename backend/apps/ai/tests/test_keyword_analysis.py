from __future__ import annotations

import pytest

from apps.ai.services.keyword_analysis import (
    KeywordAnalysisService,
)


# SEARCH INTENT TESTS
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("text", "expected_intent"),
    [
        (
            "How to learn Django SEO optimization",
            "informational",
        ),
        (
            "Buy best gaming laptop online",
            "transactional",
        ),
        (
            "Top SEO tools comparison",
            "commercial",
        ),
        (
            "Open GitHub login page",
            "navigational",
        ),
    ],
)
async def test_search_intent_detection(
    text: str,
    expected_intent: str,
):
    """
    Validate search intent classification.
    """

    result = (
        await KeywordAnalysisService.analyze(
            text,
        )
    )

    assert (
        result.search_intent
        == expected_intent
    )


# KEYWORD EXTRACTION TESTS
@pytest.mark.asyncio
async def test_keyword_extraction():
    result = (
        await KeywordAnalysisService.analyze(
            (
                "Django SEO Django "
                "optimization tutorial"
            )
        )
    )

    assert result.total_words > 0

    assert (
        len(result.top_keywords) > 0
    )

    extracted_keywords = {
        keyword.keyword.lower()
        for keyword
        in result.top_keywords
    }

    assert "django" in extracted_keywords

    assert "seo" in extracted_keywords


# SEO SCORE TESTS
@pytest.mark.asyncio
async def test_seo_score_range():
    """
    Validate SEO score range.
    """

    result = (
        await KeywordAnalysisService.analyze(
            (
                "SEO optimization tutorial "
                "for Django developers"
            )
        )
    )

    assert (
        0
        <= result.seo_score
        <= 100
    )


# EMPTY INPUT TESTS
@pytest.mark.asyncio
async def test_empty_text():
    """
    Validate empty input handling.
    """

    result = (
        await KeywordAnalysisService.analyze(
            "",
        )
    )

    assert result.total_words == 0

    assert result.seo_score == 0

    assert (
        result.search_intent
        == "unknown"
    )


# UNICODE TESTS
@pytest.mark.asyncio
async def test_unicode_content():
    """
    Validate multilingual content support.
    """

    result = (
        await KeywordAnalysisService.analyze(
            (
                "Django SEO বাংলা "
                "optimization tutorial"
            )
        )
    )

    assert result.total_words > 0

    assert (
        result.seo_score >= 0
    )


# LARGE CONTENT TESTS
@pytest.mark.asyncio
async def test_large_content():
    """
    Validate large content handling.
    """

    large_text = (
        "Django SEO optimization "
        * 500
    )

    result = (
        await KeywordAnalysisService.analyze(
            large_text,
        )
    )

    assert result.total_words > 0

    assert (
        result.seo_score >= 0
    )


# RECOMMENDATION TESTS
@pytest.mark.asyncio
async def test_recommendations_generated():
    """
    Validate SEO recommendation generation.
    """

    result = (
        await KeywordAnalysisService.analyze(
            "Short SEO content"
        )
    )

    assert isinstance(
        result.recommendations,
        list,
    )


# DETERMINISTIC ANALYSIS TESTS
@pytest.mark.asyncio
async def test_analysis_is_deterministic():
    """
    Validate deterministic analysis behavior.
    """

    text = (
        "Django SEO optimization "
        "tutorial"
    )

    result_1 = (
        await KeywordAnalysisService.analyze(
            text,
        )
    )

    result_2 = (
        await KeywordAnalysisService.analyze(
            text,
        )
    )

    assert (
        result_1.seo_score
        == result_2.seo_score
    )

    assert (
        result_1.search_intent
        == result_2.search_intent
    )


# DTO STRUCTURE TESTS
@pytest.mark.asyncio
async def test_result_structure():
    """
    Validate DTO response structure.
    """

    result = (
        await KeywordAnalysisService.analyze(
            (
                "Django SEO "
                "optimization guide"
            )
        )
    )

    assert hasattr(
        result,
        "seo_score",
    )

    assert hasattr(
        result,
        "top_keywords",
    )

    assert hasattr(
        result,
        "recommendations",
    )

    assert hasattr(
        result,
        "search_intent",
    )