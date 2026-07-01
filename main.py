import os
import datetime
from automation.shorts_maker_FFmpeg import YTShortsCreator_FFmpeg

def generate_finance_fact():
    return {
        "hook": "Finance Fact!",
        "fact": "The S&P 500 has averaged ~10% annual returns.",
        "explanation": "This includes reinvested dividends.",
        "curiosity": "Long-term investing beats timing the market."
    }

def main():
    creator = YTShortsCreator_FFmpeg()

    fact = generate_finance_fact()

    script_cards = [
        {"text": fact["hook"], "duration": 3},
        {"text": f"{fact['fact']} {fact['explanation']}", "duration": 5},
        {"text": fact["curiosity"], "duration": 3}
    ]

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"finance_fact_{timestamp}.mp4")

    creator.create_youtube_short(
        title=fact["hook"],
        script_sections=script_cards,
        background_query="none",
        output_filename=output_path,
        style="none",
        voice_style="none",
        max_duration=25,
        background_queries=["none", "none", "none"],
        blur_background=False,
        edge_blur=False
    )

    print("Video created:", output_path)

if __name__ == "__main__":
    main()
