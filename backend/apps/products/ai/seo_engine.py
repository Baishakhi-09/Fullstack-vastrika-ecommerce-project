# =========================================================
# SEO SCORE ENGINE
# =========================================================

import re

TITLE_SCORE = 30 
DESCRIPTION_SCORE = 30 
KEYWORD_SCORE = 20 
READABILITY_SCORE = 20 
MAX_SCORE = 100

def extract_keywords(
    text,
):
    """
    Extract clean keywords from text.
    """

    return {
        word.lower()

        for word in re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text or ""
        )

        if len(word) > 2
    }

def calculate_seo_score(
    title,
    description,
):
    """
    Calculate SEO quality score for
    Product Tags, Brands, Categories,
    and Products.

    Returns:
        int: SEO score (0-100)
    """

    title = (
        title or ""
    ).strip()

    description = (
        description or ""
    ).strip()

    score = 0

    title_length = len(
        title
    )

    description_length = len(
        description
    )

    description_words = (
        description.split()
    )

    if 30 <= title_length <= 60:

        score += TITLE_SCORE

    elif 20 <= title_length <= 70:

        score += (
            TITLE_SCORE // 2
        )

    if 120 <= description_length <= 160:

        score += DESCRIPTION_SCORE

    elif 80 <= description_length <= 200:

        score += (
            DESCRIPTION_SCORE // 2
        )

    title_keywords = extract_keywords(
        title
    )

    description_keywords = (
        extract_keywords(
            description
        )
    )

    matched_keywords = len(
        title_keywords &
        description_keywords
    )

    if matched_keywords >= 3:

        score += KEYWORD_SCORE
    elif matched_keywords >= 1:
        score += (
            KEYWORD_SCORE // 2
        )

    word_count = len(
        description_words
    )

    if word_count >= 20:
        score += READABILITY_SCORE

    elif word_count >= 10:
        score += (
            READABILITY_SCORE // 2
        )

    return min(
        score,
        MAX_SCORE
    )