import os
import requests
import asyncio
import edge_tts
import subprocess

VOICE_TEXT = """
Discipline beats motivation.
Most people quit too early.
Stay consistent.
Your future self will thank you.
"""

CLIP_URL = "https://videos.pexels.com/video-files/3571264/3571264-uhd_2160_4096_25fps.mp4"
MUSIC_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
os.makedirs("assets", exist_ok=True)
os.makedirs("output", exist_ok=True)

def download(url, filename):
    if not os.path.exists(filename):
        r = requests.get(url, stream=True, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

download(CLIP_URL, "assets/clip.mp4")
download(MUSIC_URL, "assets/music.mp3")

async def generate_voice():
    communicate = edge_tts.Communicate(
        VOICE_TEXT,
        "en-US-GuyNeural"
    )
    await communicate.save("assets/voice.mp3")

asyncio.run(generate_voice())

ffmpeg_command = [
    "ffmpeg",
    "-y",
    "-i", "assets/clip.mp4",
    "-i", "assets/music.mp3",
    "-i", "assets/voice.mp3",
    "-filter_complex",
    "[0:v]scale=1080:1920,eq=contrast=1.2:brightness=-0.05[v];"
    "[1:a]volume=0.3[a1];"
    "[2:a]volume=1.0[a2];"
    "[a1][a2]amix=inputs=2:duration=shortest[a]",
    "-map", "[v]",
    "-map", "[a]",
    "-t", "30",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "23",
    "output/final.mp4"
]

subprocess.run(ffmpeg_command, check=True)

print("Video successfully created at output/final.mp4")
