# =========================================================
# SMART SEO SLUG ENGINE
# =========================================================

import re
import unicodedata

STOP_WORDS = {
    "the",
    "and",
    "of",
    "for",
    "best",
    "with",
    "from",
    "this",
    "that",
    "your",
    "our",
}

def normalize_text(
    text: str | None,
) -> str:
    
    text = (
        text or ""
    ).strip()

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = text.encode(
        "ascii",
        "ignore"
    ).decode(
        "ascii"
    )

    return text.lower()

def generate_smart_slug(
    tag_name: str | None,
) -> str:
    
    tag_name = normalize_text(
        tag_name
    )

    tag_name = re.sub(
        r"[^\w\s-]",
        "",
        tag_name
    )

    tag_name = re.sub(
        r"\s+",
        " ",
        tag_name
    ).strip()

    words = tag_name.split()

    filtered_words = [ 
        word for word in words 
        
        if ( 
            word not in STOP_WORDS 
            and len(word) > 1 
        ) 
    ]

    slug = "-".join( 
        filtered_words 
    )

    if not slug:
        slug = "product-tag"

    slug = re.sub(
        r"-+",
        "-",
        slug
    )

    return slug