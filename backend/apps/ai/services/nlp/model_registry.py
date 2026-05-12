from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

import spacy


logger = logging.getLogger(__name__)


ModelAlias = Literal[
    "english",
    "multilingual",
    "scientific",
]


@dataclass(
    frozen=True,
    slots=True,
)
class SpacyModelConfig:
    """
    Immutable spaCy model configuration.
    """

    alias: str
    model_name: str

    language: str
    domain: str

    transformer: bool
    supports_gpu: bool

    batch_size: int
    max_length: int

    supports_embeddings: bool
    supports_ner: bool
    supports_text_classification: bool

    fallback_model: str | None = None


class ModelRegistry:
    """
    Enterprise NLP model registry.
    """

    _models: dict[
        str,
        SpacyModelConfig,
    ] = {

        "english": SpacyModelConfig(
            alias="english",
            model_name="en_core_web_trf",
            language="en",
            domain="general",
            transformer=True,
            supports_gpu=True,
            batch_size=32,
            max_length=100000,
            supports_embeddings=True,
            supports_ner=True,
            supports_text_classification=True,
            fallback_model="en_core_web_sm",
        ),

        "multilingual": SpacyModelConfig(
            alias="multilingual",
            model_name="xx_ent_wiki_sm",
            language="multi",
            domain="general",
            transformer=False,
            supports_gpu=False,
            batch_size=64,
            max_length=50000,
            supports_embeddings=False,
            supports_ner=True,
            supports_text_classification=False,
            fallback_model=None,
        ),

        "scientific": SpacyModelConfig(
            alias="scientific",
            model_name="en_core_sci_lg",
            language="en",
            domain="scientific",
            transformer=False,
            supports_gpu=True,
            batch_size=16,
            max_length=200000,
            supports_embeddings=True,
            supports_ner=True,
            supports_text_classification=False,
            fallback_model="en_core_web_sm",
        ),
    }

    @classmethod
    def get(
        cls,
        alias: str,
    ) -> SpacyModelConfig:
        """
        Retrieve model configuration safely.
        """

        if alias not in cls._models:
            raise ValueError(
                f"Unsupported NLP model alias: "
                f"{alias}"
            )

        return cls._models[alias]

    @classmethod
    def exists(
        cls,
        alias: str,
    ) -> bool:
        """
        Check whether model alias exists.
        """

        return alias in cls._models

    @classmethod
    def validate_model_installation(
        cls,
        alias: str,
    ) -> bool:
        """
        Validate installed spaCy package.
        """

        model_config = cls.get(alias)

        installed = spacy.util.is_package(
            model_config.model_name
        )

        if installed:

            logger.info(
                "spaCy model validated: %s",
                model_config.model_name,
            )

        else:

            logger.warning(
                "spaCy model missing: %s",
                model_config.model_name,
            )

        return installed

    @classmethod
    def register(
        cls,
        config: SpacyModelConfig,
    ) -> None:
        """
        Dynamically register NLP model.
        """

        logger.info(
            "Registering NLP model: %s",
            config.alias,
        )

        cls._models[
            config.alias
        ] = config

    @classmethod
    def unregister(
        cls,
        alias: str,
    ) -> None:
        """
        Remove NLP model from registry.
        """

        if alias not in cls._models:
            return

        logger.info(
            "Unregistering NLP model: %s",
            alias,
        )

        del cls._models[alias]

    @classmethod
    def available_models(
        cls,
    ) -> dict[
        str,
        SpacyModelConfig,
    ]:
        """
        Return registered models safely.
        """

        return cls._models.copy()

    @classmethod
    def get_fallback_model(
        cls,
        alias: str,
    ) -> str | None:
        """
        Retrieve fallback model.
        """

        model_config = cls.get(alias)

        return (
            model_config.fallback_model
        )

    @classmethod
    def supports_gpu(
        cls,
        alias: str,
    ) -> bool:
        """
        Check GPU compatibility.
        """

        return cls.get(
            alias
        ).supports_gpu

    @classmethod
    def supports_transformers(
        cls,
        alias: str,
    ) -> bool:
        """
        Check transformer support.
        """

        return cls.get(
            alias
        ).transformer

    @classmethod
    def get_batch_size(
        cls,
        alias: str,
    ) -> int:
        """
        Retrieve optimized batch size.
        """

        return cls.get(
            alias
        ).batch_size

    @classmethod
    def get_max_length(
        cls,
        alias: str,
    ) -> int:
        """
        Retrieve max processing length.
        """

        return cls.get(
            alias
        ).max_length