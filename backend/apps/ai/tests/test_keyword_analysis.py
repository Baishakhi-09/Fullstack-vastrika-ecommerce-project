import pytest

from apps.ai.services.keyword_analysis import (
    KeywordAnalysisService,
)


@pytest.mark.asyncio
async def test_search_intent_detection():
    result = await KeywordAnalysisService.analyze(
        "How to learn Django SEO optimization"
    )

    assert result.search_intent == "informational"


@pytest.mark.asyncio
async def test_keyword_extraction():
    result = await KeywordAnalysisService.analyze(
        "Django SEO Django optimization tutorial"
    )

    assert result.total_words > 0
    assert len(result.top_keywords) > 0


@pytest.mark.asyncio
async def test_seo_score():
    result = await KeywordAnalysisService.analyze(
        "SEO optimization tutorial for Django developers"
    )

    assert result.seo_score >= 0