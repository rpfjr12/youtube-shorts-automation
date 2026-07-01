import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

class YTShortsCreator_FFmpeg:
    def __init__(self, channel="default"):
        self.channel = channel

    def _generate_frames(self, script_sections):
        os.makedirs("frames", exist_ok=True)

        frame_index = 0

        for section in script_sections:
            text = section["text"]
            duration = section["duration"]  # seconds
            frames = duration * 30          # 30fps

            for _ in range(frames):
                img = Image.new("RGB", (1080, 1920), "black")
                draw = ImageDraw.Draw(img)
                draw.text((100, 100), text, fill="white")
                img.save(f"frames/frame_{frame_index:04d}.png")
                frame_index += 1

    def _render_video(self, output_filename):
        cmd = [
            "ffmpeg",
            "-framerate", "30",
            "-i", "frames/frame_%04d.png",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_filename
        ]
        subprocess.run(cmd, check=True)

    def create_youtube_short(
        self,
        title,
        script_sections,
        background_query,
        output_filename,
        style,
        voice_style,
        max_duration,
        background_queries,
        blur_background=False,
        edge_blur=False
    ):
        self._generate_frames(script_sections)
        self._render_video(output_filename)
        return output_filename

    def run(self):
        demo_sections = [
            {"text": "Demo Short", "duration": 3, "voice_style": "none"},
            {"text": "Generated with FFmpeg", "duration": 3, "voice_style": "none"},
        ]
        self._generate_frames(demo_sections)
        self._render_video("demo_output.mp4")
        return "demo_output.mp4"
