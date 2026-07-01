import openai
import os
from dotenv import load_dotenv
import logging
import time
import json

# Logging
logger = logging.getLogger(__name__)

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# ---------------------------------------------------------
# FINANCE FACTS — BATCH VIDEO QUERY GENERATOR
# ---------------------------------------------------------
def generate_batch_video_queries(
    texts: list[str],
    overall_topic="finance",
    model="gpt-4o-mini-2024-07-18",
    retries=3
):
    """
    Generate 2–4 word stock video search queries for each finance fact card.
    """
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY missing")

    formatted_texts = ""
    for i, text in enumerate(texts):
        formatted_texts += f"--- Card {i} ---\n{text}\n\n"

    prompt = f"""
    Generate a 2–4 word stock video search query for EACH finance-related card.
    Focus on money, savings, wealth, habits, or financial psychology.

    Input:
    {formatted_texts}

    Return ONLY JSON:
    {{
      "0": "abstract money",
      "1": "saving habits",
      "2": "wealth mindset"
    }}
    """

    for attempt in range(retries):
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.4,
                response_format={"type": "json_object"}
            )

            data = json.loads(response.choices[0].message.content)
            return {int(k): v for k, v in data.items()}

        except Exception as e:
            logger.error(f"Batch video query error: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)

    return {}


# ---------------------------------------------------------
# FINANCE FACTS — BATCH IMAGE PROMPT GENERATOR
# ---------------------------------------------------------
def generate_batch_image_prompts(
    texts: list[str],
    overall_topic="finance",
    model="gpt-4o-mini-2024-07-18",
    retries=3
):
    """
    Generate 15–25 word image prompts for each finance fact card.
    """
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY missing")

    formatted_texts = ""
    for i, text in enumerate(texts):
        formatted_texts += f"--- Card {i} ---\n{text}\n\n"

    prompt = f"""
    Generate a 15–25 word image prompt for EACH finance-related card.
    Focus on money, savings, wealth, habits, financial psychology.
    DO NOT include style words (photorealistic, digital art, etc.).

    Input:
    {formatted_texts}

    Return ONLY JSON:
    {{
      "0": "pile of coins with soft lighting symbolizing savings",
      "1": "person tracking expenses on notebook with calm background",
      "2": "abstract upward financial growth arrows glowing"
    }}
    """

    for attempt in range(retries):
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
                temperature=0.6,
                response_format={"type": "json_object"}
            )

            data = json.loads(response.choices[0].message.content)
            return {int(k): v for k, v in data.items()}

        except Exception as e:
            logger.error(f"Batch image prompt error: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)

    return {}


# ---------------------------------------------------------
# REMOVE — NOT USED IN FINANCE FACT SYSTEM
# ---------------------------------------------------------
# generate_comprehensive_content is NOT needed anymore.
# We intentionally remove it to avoid accidental calls.
