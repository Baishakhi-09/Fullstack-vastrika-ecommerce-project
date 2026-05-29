from difflib import SequenceMatcher


def check_similarity(

    current_tag,
    existing_tags
):

    matches = []

    for tag in existing_tags:

        similarity = SequenceMatcher(
            None,
            current_tag.lower(),
            tag.lower()
        ).ratio()

        if similarity > 0.7:

            matches.append({
                "tag": tag,
                "score": round(
                    similarity * 100,
                    2
                )
            })

    return matches