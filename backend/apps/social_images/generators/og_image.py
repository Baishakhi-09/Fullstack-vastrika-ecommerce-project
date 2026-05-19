from __future__ import annotations

import logging
import textwrap
from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


logger = logging.getLogger(
    __name__
)


# =========================================================
# OPEN GRAPH IMAGE GENERATOR
# =========================================================
class OpenGraphImageGenerator:
    """
    Generate professional OpenGraph images.
    """

    WIDTH = 1200
    HEIGHT = 630

    BACKGROUND_COLOR = (
        18,
        18,
        18,
    )

    TEXT_COLOR = (
        255,
        255,
        255,
    )

    ACCENT_COLOR = (
        59,
        130,
        246,
    )

    PADDING_X = 80
    PADDING_Y = 80

    TITLE_MAX_WIDTH = 26

    DEFAULT_FONT_SIZE = 64

    FONT_PATH = (
        "static/fonts/Inter-Bold.ttf"
    )

    OUTPUT_QUALITY = 95

    # =====================================================
    # GENERATE IMAGE
    # =====================================================
    @classmethod
    def generate(
        cls,
        title: str,
        output_path: str,
        subtitle: str | None = None,
        background_image: str | None = None,
        logo_path: str | None = None,
    ) -> str:
        """
        Generate OpenGraph image.

        Returns generated image path.
        """

        try:

            # CREATE BASE IMAGE
            image = cls._create_base_image(
                background_image
            )

            draw = ImageDraw.Draw(
                image
            )

            # LOAD FONT
            title_font = cls._load_font(
                cls.DEFAULT_FONT_SIZE
            )

            subtitle_font = cls._load_font(
                32
            )

            # DRAW ACCENT BAR
            cls._draw_accent_bar(
                draw
            )

            # DRAW LOGO
            if logo_path:
                cls._draw_logo(
                    image=image,
                    logo_path=logo_path,
                )

            # DRAW TITLE
            current_y = (
                cls.PADDING_Y + 60
            )

            current_y = cls._draw_title(
                draw=draw,
                title=title,
                font=title_font,
                start_y=current_y,
            )

            # DRAW SUBTITLE
            if subtitle:
                cls._draw_subtitle(
                    draw=draw,
                    subtitle=subtitle,
                    font=subtitle_font,
                    start_y=current_y + 40,
                )

            # ENSURE DIRECTORY EXISTS
            output_file = Path(
                output_path
            )

            output_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            # SAVE IMAGE
            image.save(
                output_path,
                quality=cls.OUTPUT_QUALITY,
                optimize=True,
            )

            logger.info(
                (
                    "OpenGraph image "
                    "generated successfully | "
                    "Path=%s"
                ),
                output_path,
            )

            return output_path

        except Exception:
            logger.exception(
                (
                    "Failed to generate "
                    "OpenGraph image."
                )
            )

            raise

    # =====================================================
    # CREATE BASE IMAGE
    # =====================================================
    @classmethod
    def _create_base_image(
        cls,
        background_image: str | None,
    ) -> Image.Image:

        # USE BACKGROUND IMAGE
        if background_image:

            background = Image.open(
                background_image
            ).convert("RGB")

            background = background.resize(
                (
                    cls.WIDTH,
                    cls.HEIGHT,
                )
            )

            # DARK OVERLAY
            overlay = Image.new(
                "RGBA",
                (
                    cls.WIDTH,
                    cls.HEIGHT,
                ),
                (
                    0,
                    0,
                    0,
                    120,
                ),
            )

            background = background.convert(
                "RGBA"
            )

            background.alpha_composite(
                overlay
            )

            return background.convert(
                "RGB"
            )

        # DEFAULT BACKGROUND
        return Image.new(
            "RGB",
            (
                cls.WIDTH,
                cls.HEIGHT,
            ),
            color=cls.BACKGROUND_COLOR,
        )

    # =====================================================
    # LOAD FONT
    # =====================================================
    @classmethod
    def _load_font(
        cls,
        size: int,
    ) -> ImageFont.FreeTypeFont:

        font_path = Path(
            cls.FONT_PATH
        )

        if font_path.exists():

            return ImageFont.truetype(
                str(font_path),
                size,
            )

        logger.warning(
            (
                "Custom font not found. "
                "Using default font."
            )
        )

        return ImageFont.load_default()

    # =====================================================
    # DRAW TITLE
    # =====================================================
    @classmethod
    def _draw_title(
        cls,
        draw: ImageDraw.ImageDraw,
        title: str,
        font,
        start_y: int,
    ) -> int:

        wrapped_lines = textwrap.wrap(
            title,
            width=cls.TITLE_MAX_WIDTH,
        )

        y = start_y

        for line in wrapped_lines:

            draw.text(
                (
                    cls.PADDING_X,
                    y,
                ),
                line,
                fill=cls.TEXT_COLOR,
                font=font,
            )

            bbox = draw.textbbox(
                (
                    0,
                    0,
                ),
                line,
                font=font,
            )

            line_height = (
                bbox[3] - bbox[1]
            )

            y += (
                line_height + 16
            )

        return y

    # =====================================================
    # DRAW SUBTITLE
    # =====================================================
    @classmethod
    def _draw_subtitle(
        cls,
        draw: ImageDraw.ImageDraw,
        subtitle: str,
        font,
        start_y: int,
    ) -> None:

        wrapped_lines = textwrap.wrap(
            subtitle,
            width=50,
        )

        y = start_y

        for line in wrapped_lines:

            draw.text(
                (
                    cls.PADDING_X,
                    y,
                ),
                line,
                fill=(
                    210,
                    210,
                    210,
                ),
                font=font,
            )

            bbox = draw.textbbox(
                (
                    0,
                    0,
                ),
                line,
                font=font,
            )

            line_height = (
                bbox[3] - bbox[1]
            )

            y += (
                line_height + 12
            )

    # =====================================================
    # DRAW ACCENT BAR
    # =====================================================
    @classmethod
    def _draw_accent_bar(
        cls,
        draw: ImageDraw.ImageDraw,
    ) -> None:

        draw.rectangle(
            (
                0,
                0,
                cls.WIDTH,
                14,
            ),
            fill=cls.ACCENT_COLOR,
        )

    # =====================================================
    # DRAW LOGO
    # =====================================================
    @classmethod
    def _draw_logo(
        cls,
        image: Image.Image,
        logo_path: str,
    ) -> None:
        try:
            logo = Image.open(
                logo_path
            ).convert("RGBA")

            logo.thumbnail(
                (
                    140,
                    140,
                )
            )

            image.paste(
                logo,
                (
                    cls.WIDTH - 200,
                    50,
                ),
                logo,
            )

        except Exception:
            logger.exception(
                (
                    "Failed to render "
                    "logo in OpenGraph image."
                )
            )