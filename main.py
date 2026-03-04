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

CLIP_URL = "https://cdn.pixabay.com/video/2023/05/01/160198-823388103_large.mp4"
MUSIC_URL = "https://cdn.pixabay.com/download/audio/2022/10/25/audio_9463c1bb4f.mp3"

os.makedirs("assets", exist_ok=True)
os.makedirs("output", exist_ok=True)

def download(url, filename):
    if not os.path.exists(filename):
        r = requests.get(url)
        with open(filename, "wb") as f:
            f.write(r.content)

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

print("Video successfully created at output/final.mp4")git add .
git commit -m "Fix ffmpeg execution using subprocess"
git push