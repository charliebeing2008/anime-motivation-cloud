import os
import asyncio
import edge_tts
import subprocess
import yt_dlp

os.makedirs("assets", exist_ok=True)
os.makedirs("output", exist_ok=True)

VIDEO_URL = "https://archive.org/download/BigBuckBunny_124/Content/big_buck_bunny_720p_surround.mp4"
MUSIC_URL = "https://archive.org/download/testmp3testfile/mpthreetest.mp3"

VOICE_TEXT = """
Discipline beats motivation.
Most people quit too early.
Stay consistent.
Your future self will thank you.
"""

def download_video(url, output_path):
    if not os.path.exists(output_path):
        ydl_opts = {
            'outtmpl': output_path,
            'format': 'mp4/best[ext=mp4]/best',
            'quiet': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("✅ Video downloaded!")
    else:
        print("✅ Video already exists!")

def download_music(url, output_path):
    if not os.path.exists(output_path):
        ydl_opts = {
            'outtmpl': output_path,
            'format': 'bestaudio/best',
            'quiet': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("✅ Music downloaded!")
    else:
        print("✅ Music already exists!")

print("⬇️ Downloading video...")
download_video(VIDEO_URL, "assets/clip.mp4")

print("⬇️ Downloading music...")
download_music(MUSIC_URL, "assets/music.mp3")

async def generate_voice():
    communicate = edge_tts.Communicate(VOICE_TEXT, "en-US-GuyNeural")
    await communicate.save("assets/voice.mp3")

print("🎙️ Generating voice...")
asyncio.run(generate_voice())

ffmpeg_command = [
    "ffmpeg", "-y",
    "-i", "assets/clip.mp4",
    "-i", "assets/music.mp3",
    "-i", "assets/voice.mp3",
    "-filter_complex",
    "[0:v]scale=1080:1920,eq=contrast=1.2:brightness=-0.05[v];"
    "[1:a]volume=0.3[a1];"
    "[2:a]volume=1.0[a2];"
    "[a1][a2]amix=inputs=2:duration=shortest[a]",
    "-map", "[v]", "-map", "[a]",
    "-t", "30", "-c:v", "libx264",
    "-preset", "fast", "-crf", "23",
    "output/final.mp4"
]

print("🎬 Creating final video...")
subprocess.run(ffmpeg_command, check=True)
print("✅ Video created at output/final.mp4")
