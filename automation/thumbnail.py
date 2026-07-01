import os
import time
import logging
import textwrap
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

TEMP_DIR = os.getenv("TEMP_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp"))
os.makedirs(TEMP_DIR, exist_ok=True)


class ThumbnailGenerator:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.temp_dir = os.path.join(TEMP_DIR, f"thumbnail_{int(time.time())}")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

        # Thumbnail size for YouTube Shorts
        self.thumbnail_size = (1080, 1920)

        # Font
        self.fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
        self.title_font_path = os.path.join(self.fonts_dir, "default_font.ttf")

    def generate_thumbnail(self, title, script_sections=None, prompt=None, style=None, output_path=None):
        """
        Generate a simple finance-themed thumbnail.
        """

        if not output_path:
            timestamp = int(time.time())
            output_path = os.path.join(self.output_dir, f"thumbnail_{timestamp}.jpg")

        logger.info(f"Generating finance thumbnail for: {title}")

        # ------------------------------
        # 1. Create solid finance background
        # ------------------------------
        img = Image.new("RGB", self.thumbnail_size, color=(20, 20, 20))  # dark finance background
        draw = ImageDraw.Draw(img)

        # ------------------------------
        # 2. Load font
        # ------------------------------
        try:
            font_size = 80 if len(title) < 25 else 60
            font = ImageFont.truetype(self.title_font_path, font_size)
        except:
            font = ImageFont.load_default()

        # ------------------------------
        # 3. Wrap text
        # ------------------------------
        wrapped = textwrap.fill(title, width=20)

        # ------------------------------
        # 4. Position text
        # ------------------------------
        text_bbox = draw.textbbox((0, 0), wrapped, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]

        text_x = (self.thumbnail_size[0] - text_w) // 2
        text_y = (self.thumbnail_size[1] - text_h) // 2

        # ------------------------------
        # 5. Draw neon green text with shadow
        # ------------------------------
        shadow_color = (0, 0, 0)
        neon_green = (0, 255, 100)

        # Shadow
        draw.text((text_x + 3, text_y + 3), wrapped, font=font, fill=shadow_color)

        # Main text
        draw.text((text_x, text_y), wrapped, font=font, fill=neon_green)

        # ------------------------------
        # 6. Add SMALL "SHORTS" tag
        # ------------------------------
        shorts_font = ImageFont.truetype(self.title_font_path, 40) if os.path.exists(self.title_font_path) else ImageFont.load_default()

        draw.text(
            (20, 20),
            "SHORTS",
            font=shorts_font,
            fill=(255, 0, 0)
        )

        # ------------------------------
        # 7. Save thumbnail
        # ------------------------------
        img.save(output_path, quality=95)
        logger.info(f"Thumbnail saved: {output_path}")

        return output_path

    def cleanup(self):
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
