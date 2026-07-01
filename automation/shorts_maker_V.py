import os
import time
import logging
from datetime import datetime
from moviepy.editor import (
    VideoFileClip, CompositeVideoClip, AudioFileClip, ImageClip
)
from helper.minor_helper import cleanup_temp_directories
from helper.fetch import fetch_videos_parallel
from helper.text import TextHelper
from helper.audio import AudioHelper
from automation.renderer import render_video
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TEMP_DIR = os.getenv("TEMP_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp"))
os.makedirs(TEMP_DIR, exist_ok=True)


class YTShortsCreator_V:
    def __init__(self, fps=30):
        self.temp_dir = os.path.join(TEMP_DIR, f"shorts_v_{int(time.time())}")
        os.makedirs(self.temp_dir, exist_ok=True)

        self.text_helper = TextHelper()
        self.audio_helper = AudioHelper(self.temp_dir)

        self.resolution = (1080, 1920)
        self.fps = fps

    def create_youtube_short(
        self,
        title,
        script_sections,
        background_query="finance abstract",
        output_filename=None,
        style="video",
        voice_style=None,
        max_duration=25,
        background_queries=None
    ):
        try:
            if not output_filename:
                date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = os.path.join(self.temp_dir, f"short_{date_str}.mp4")

            # ------------------------------
            # 1. SIMPLE DURATION HANDLING
            # ------------------------------
            total_duration = sum(s.get("duration", 4) for s in script_sections)
            if total_duration > max_duration:
                scale = max_duration / total_duration
                for s in script_sections:
                    s["duration"] = s["duration"] * scale

            # ------------------------------
            # 2. BACKGROUND QUERIES
            # ------------------------------
            if not background_queries:
                background_queries = [background_query] * len(script_sections)

            videos_by_query = fetch_videos_parallel(
                queries=background_queries,
                count_per_query=1,
                min_duration=int(max(s["duration"] for s in script_sections)) + 1
            )

            # ------------------------------
            # 3. AUDIO GENERATION
            # ------------------------------
            audio_data = self.audio_helper.process_audio_for_script(
                script_sections=script_sections,
                voice_style=voice_style
            )

            # ------------------------------
            # 4. TEXT CLIPS (simple fade)
            # ------------------------------
            text_clips = self.text_helper.generate_text_clips_parallel(
                script_sections=script_sections,
                with_pill=True,
                font_size=60,
                animation="fade"
            )

            # ------------------------------
            # 5. BACKGROUND CLIPS
            # ------------------------------
            background_clips = []
            for i, section in enumerate(script_sections):
                query = background_queries[i]
                if query not in videos_by_query or not videos_by_query[query]:
                    logger.error(f"No background video for section {i}")
                    return None

