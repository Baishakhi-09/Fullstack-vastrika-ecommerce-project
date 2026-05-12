from apps.ai.services.nlp.nlp_pipeline import (
    NLPPipeline,
)


class PassiveVoiceDetector:

    @classmethod
    def detect(
        cls,
        text: str,
    ):

        doc = NLPPipeline.process(text)

        passive_sentences = []

        for sentence in doc.sents:
            for token in sentence:
                if token.dep_ == "auxpass":
                    passive_sentences.append(
                        sentence.text
                    )
                    break

        return passive_sentences