from transformers import pipeline


class AIReadabilityClassifier:

    classifier = pipeline(
        "text-classification",
        model="distilbert-base-uncased",
    )

    @classmethod
    def classify(
        cls,
        text: str,
    ):
        return cls.classifier(text[:512])