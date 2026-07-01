import os
import time
import logging
from datetime import datetime
from moviepy.editor import (
    VideoFileClip, CompositeVideoClip, AudioFileClip
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
            # ------------------------------
            # Output filename
            # ------------------------------
            if not output_filename:
                date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = os.path.join(self.temp_dir, f"short_{date_str}.mp4")

            # ------------------------------
            # Duration scaling
            # ------------------------------
            total_duration = sum(s.get("duration", 4) for s in script_sections)
            if total_duration > max_duration:
                scale = max_duration / total_duration
                for s in script_sections:
                    s["duration"] = s["duration"] * scale

            # ------------------------------
            # Background queries
            # ------------------------------
            if not background_queries:
                background_queries = [background_query] * len(script_sections)

            videos_by_query = fetch_videos_parallel(
                queries=background_queries,
                count_per_query=1,
                min_duration=int(max(s["duration"] for s in script_sections)) + 1
            )

            # ------------------------------
            # Audio generation
            # ------------------------------
            audio_data = self.audio_helper.process_audio_for_script(
                script_sections=script_sections,
                voice_style=voice_style
            )

            # ------------------------------
            # Text clips
            # ------------------------------
            text_clips = self.text_helper.generate_text_clips_parallel(
                script_sections=script_sections,
                with_pill=True,
                font_size=60,
                animation="fade"
            )

            # ------------------------------
            # Background clips
            # ------------------------------
            background_clips = []
            for i, section in enumerate(script_sections):
                query = background_queries[i]

                if query not in videos_by_query or not videos_by_query[query]:
                    logger.error(f"No background video for section {i}")
                    return None

                bg_path = videos_by_query[query][0]
                bg_clip = VideoFileClip(bg_path).resize(self.resolution)
                bg_clip = bg_clip.with_duration(section["duration"])
                background_clips.append(bg_clip)

            # ------------------------------
            # Composite each section
            # ------------------------------
            section_clips = []
            for i, section in enumerate(script_sections):
                duration = section["duration"]

                bg = background_clips[i].with_duration(duration)

                audio_path = audio_data[i]["path"]
                audio_clip = AudioFileClip(audio_path)

                txt = text_clips[i].with_duration(duration)

                composite = CompositeVideoClip([bg, txt]).with_duration(duration)
                composite = composite.with_audio(audio_clip)

                section_clips.append(composite)

            # ------------------------------
            # Final render
            # ------------------------------
            render_temp = os.path.join(self.temp_dir, "render")
            os.makedirs(render_temp, exist_ok=True)

            output_path = render_video(
                clips=section_clips,
                output_file=output_filename,
                fps=self.fps,
                temp_dir=render_temp,
                preset="ultrafast",
                parallel=False,
                memory_per_worker_gb=1.0,
                options={"clean_temp": True}
            )

            return output_path

        except Exception as e:
            logger.error(f"Error creating video: {e}")
            cleanup_temp_directories([self.temp_dir])
            return None

    def cleanup(self):
        try:
            cleanup_temp_directories([self.temp_dir])
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
