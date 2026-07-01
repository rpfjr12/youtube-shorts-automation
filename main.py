import os
import sys
import logging
import logging.handlers
from pathlib import Path
from dotenv import load_dotenv
import datetime

# --- FINANCE FACT GENERATOR ---
from automation.finance_fact_generator import generate_finance_fact

# --- NEW FFmpeg-BASED CREATOR ---
from automation.shorts_maker_FFmpeg import YTShortsCreator_FFmpeg

# --- EXISTING PIPELINE MODULES (UNCHANGED) ---
from automation.youtube_upload import upload_video, get_authenticated_service
from automation.thumbnail import ThumbnailGenerator
from automation.content_generator import generate_batch_video_queries, generate_batch_image_prompts
from helper.minor_helper import ensure_output_directory, cleanup_temp_directories

load_dotenv()

# ---------------- LOGGING SETUP ----------------
LOG_DIR = 'logs'
LOG_FILENAME = os.path.join(LOG_DIR, 'finance_facts_daily.log')
LOG_LEVEL = logging.INFO

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
if DEBUG_MODE:
    LOG_LEVEL = logging.DEBUG

Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
logging.getLogger().handlers = []

root_logger = logging.getLogger()
root_logger.setLevel(LOG_LEVEL)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

file_handler = logging.handlers.TimedRotatingFileHandler(
    LOG_FILENAME, when='midnight', interval=1, backupCount=7, encoding='utf-8'
)
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)

# ---------------- CREATOR SELECTION ----------------
def get_creator_for_day():
    """
    Previously alternated between MoviePy video creator and image creator.
    Now ALWAYS uses FFmpeg creator (safe, stable, CI-friendly).
    """
    today = datetime.datetime.now()
    day_of_year = today.timetuple().tm_yday

    logger.info(f"Day {day_of_year}: Using FFmpeg creator")
    return YTShortsCreator_FFmpeg()

# ---------------- FINANCE FACT SHORT GENERATOR ----------------
def generate_youtube_short(style="photorealistic", max_duration=25, creator_type=None):
    try:
        output_dir = ensure_output_directory()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # --- FINANCE FACT ---
        fact = generate_finance_fact()

        title = fact["hook"]
        description = f"{fact['fact']} {fact['explanation']}\n\n{fact['curiosity']}"

        logger.info("Finance fact generated:")
        logger.info(f"Title: {title}")
        logger.info(f"Fact: {fact['fact']}")

        # --- SCRIPT CARDS ---
        script_cards = [
            {"text": fact["hook"], "duration": 3, "voice_style": "calm"},
            {"text": f"{fact['fact']} {fact['explanation']}", "duration": 5, "voice_style": "calm"},
            {"text": fact["curiosity"], "duration": 3, "voice_style": "calm"}
        ]

        safe_title = title.replace(' ', '_').replace(':', '').replace('?', '').replace('!', '')[:30]
        output_filename = f"finance_fact_{safe_title}_{timestamp}.mp4"
        output_path = os.path.join(output_dir, output_filename)

        # --- CREATOR ---
        if creator_type is None:
            creator_type = get_creator_for_day()

        # --- BACKGROUND QUERIES ---
        card_texts = [card["text"] for card in script_cards]
        default_query = "abstract finance money savings"

        # FFmpeg creator uses image prompts only
        batch_query_results = generate_batch_image_prompts(
            card_texts,
            overall_topic="finance",
            model="gpt-4o-mini-2024-07-18"
        )

        section_queries = []
        for i in range(len(script_cards)):
            q = batch_query_results.get(i, default_query)
            if not q:
                q = default_query
            section_queries.append(q)

        fallback_query = section_queries[0]

        # --- VIDEO CREATION (FFmpeg) ---
        video_path = creator_type.create_youtube_short(
            title=title,
            script_sections=script_cards,
            background_query=fallback_query,
            output_filename=output_path,
            style=style,
            voice_style="none",
            max_duration=max_duration,
            background_queries=section_queries,
            blur_background=False,
            edge_blur=False
        )

        # --- THUMBNAIL ---
        thumbnail_dir = os.path.join(output_dir, "thumbnails")
        os.makedirs(thumbnail_dir, exist_ok=True)

        thumbnail_generator = ThumbnailGenerator(output_dir=thumbnail_dir)
        safe_title_thumbnail = safe_title[:20]
        thumbnail_output_path = os.path.join(
            thumbnail_dir, f"thumbnail_{safe_title_thumbnail}_{timestamp}.jpg"
        )

        thumbnail_prompt = "minimalist finance, money, savings, dark background, neon green text"

        thumbnail_path = thumbnail_generator.generate_thumbnail(
            title=title,
            script_sections=script_cards,
            prompt=thumbnail_prompt,
            style=style,
            output_path=thumbnail_output_path
        )

        if not thumbnail_path:
            fallback_img = thumbnail_generator.fetch_image_unsplash("finance money savings")
            if fallback_img:
                thumbnail_path = thumbnail_generator.create_thumbnail(
                    title=title,
                    image_path=fallback_img,
                    output_path=thumbnail_output_path
                )

        thumbnail_generator.cleanup()

        # --- OPTIONAL UPLOAD ---
        if os.getenv("ENABLE_YOUTUBE_UPLOAD", "false").lower() == "true":
            youtube = get_authenticated_service()
            upload_video(
                youtube,
                video_path,
                title,
                description,
                ["shorts", "finance", "money", "wealth"],
                thumbnail_path=thumbnail_path
            )

        return video_path, thumbnail_path

    except Exception as e:
        logger.error(f"Error generating finance fact short: {e}")
        raise

# ---------------- MAIN ----------------
def main(creator_type=None):
    try:
        if creator_type is None:
            creator_type = get_creator_for_day()

        style = "photorealistic"
        max_duration = 25

        result = generate_youtube_short(
            style=style,
            max_duration=max_duration,
            creator_type=creator_type
        )

        if isinstance(result, tuple):
            video_path, thumbnail_path = result
            logger.info(f"Video created: {video_path}")
            if thumbnail_path:
                logger.info(f"Thumbnail: {thumbnail_path}")
        else:
            logger.info(f"Video created: {result}")

        return result

    except Exception as e:
        logger.error(f"Process failed: {e}")
        return None

    finally:
        try:
            logger.info("Cleaning temporary files")
            cleanup_temp_directories(max_age_hours=24)
        except Exception as cleanup_error:
            logger.error(f"Cleanup error: {cleanup_error}")

if __name__ == "__main__":
    main()
    cleanup_temp_directories(max_age_hours=24, force_all=True)
