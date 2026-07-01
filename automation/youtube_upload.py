import os
import logging
import io
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from automation.youtube_auth import authenticate_youtube
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


def get_authenticated_service():
    """Authenticate and return YouTube API client."""
    credentials = authenticate_youtube()
    return build("youtube", "v3", credentials=credentials)


def upload_video(
    youtube,
    file_path,
    title,
    description,
    tags=None,
    thumbnail_path=None,
    privacy="public"
):
    """
    Upload a finance‑facts short to YouTube.

    Args:
        youtube: Authenticated YouTube API client
        file_path (str): Path to video file
        title (str): Video title
        description (str): Video description
        tags (list): Tags for SEO
        thumbnail_path (str): Optional thumbnail path
        privacy (str): 'public', 'private', or 'unlisted'
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Video file not found: {file_path}")

    # Default finance tags
    if tags is None:
        tags = ["shorts", "finance", "money", "wealth", "saving"]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"  # People & Blogs
        },
        "status": {
            "privacyStatus": privacy
        }
    }

    media_body = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    try:
        logger.info(f"Uploading video: {title}")

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media_body
        )
        response = request.execute()

        video_id = response.get("id")
        logger.info(f"✔ Video uploaded successfully — ID: {video_id}")

        # ------------------------------
        # Upload thumbnail (optional)
        # ------------------------------
        if thumbnail_path and os.path.exists(thumbnail_path):
            try:
                logger.info("Uploading thumbnail...")
                media = MediaFileUpload(
                    thumbnail_path,
                    mimetype="image/jpeg",
                    resumable=True
                )
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=media
                ).execute()
                logger.info("✔ Thumbnail uploaded successfully")

            except HttpError:
                logger.warning("Thumbnail upload failed — trying fallback method")

                try:
                    with open(thumbnail_path, "rb") as f:
                        image_data = f.read()

                    youtube.thumbnails().set(
                        videoId=video_id,
                        media_body=MediaIoBaseUpload(
                            io.BytesIO(image_data),
                            mimetype="image/jpeg",
                            resumable=True
                        )
                    ).execute()

                    logger.info("✔ Thumbnail uploaded using fallback method")

                except Exception as e:
                    logger.error(f"Thumbnail fallback failed: {e}")

        return video_id

    except HttpError as e:
        logger.error(f"Video upload failed: {e}")
        return None


if __name__ == "__main__":
    youtube = get_authenticated_service()
    upload_video(
        youtube,
        "short_output.mp4",
        "Test Finance Short",
        "A test finance video.",
        ["shorts", "finance", "money"]
    )
