from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class OpenGraphImageGenerator:
    WIDTH = 1200
    HEIGHT = 630

    @staticmethod
    def generate(title, output_path):
        image = Image.new(
            "RGB",
            (
                OpenGraphImageGenerator.WIDTH,
                OpenGraphImageGenerator.HEIGHT,
            ),
            color=(18, 18, 18),
        )

        draw = ImageDraw.Draw(image)

        font = ImageFont.load_default()

        draw.text(
            (80, 220),
            title,
            fill=(255, 255, 255),
            font=font,
        )

        image.save(output_path)