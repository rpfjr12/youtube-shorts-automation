import os
import json
from dotenv import load_dotenv

load_dotenv()

class Secrets:
    """
    Simple secrets loader.
    No Google Cloud.
    No Secret Manager.
    No service accounts.
    Only .env + GitHub Secrets.
    """

    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.ENABLE_YOUTUBE_UPLOAD = os.getenv("ENABLE_YOUTUBE_UPLOAD", "false").lower() == "true"

        # YouTube OAuth JSON (from GitHub secret GOOGLE_CREDS_JSON)
        self.YOUTUBE_CLIENT_JSON = os.getenv("GOOGLE_CREDS_JSON")

    def get_youtube_credentials(self):
        """Return YouTube OAuth client JSON as a dict."""
        if not self.YOUTUBE_CLIENT_JSON:
            return None
        try:
            return json.loads(self.YOUTUBE_CLIENT_JSON)
        except:
            return None

    def write_temp_credentials(self, base_path="automation/credentials"):
        """Write YouTube OAuth JSON to a temp file."""
        creds = self.get_youtube_credentials()
        if creds is None:
            return None

        os.makedirs(base_path, exist_ok=True)
        path = os.path.join(base_path, "client_secret.json")

        with open(path, "w") as f:
            json.dump(creds, f)

        return path

    def cleanup_temp_credentials(self, *paths):
        for p in paths:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass
