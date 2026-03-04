import os
import asyncio
import edge_tts
import subprocess
import yt_dlp
import json

os.makedirs("assets", exist_ok=True)
os.makedirs("output", exist_ok=True)

VIDEO_URL = "https://archive.org/download/anime-amv-test/amv.mp4"
MUSIC_URL = "https://archive.org/download/testmp3testfile/mpthreetest.mp3"

VOICE_TEXT = "Discipline beats motivation. Most people quit too early. Stay consistent. Your future self will thank you."

# ─── Download ───────────────────────────────────────────────

def download_file(url, output_path):
    if not os.path.exists(output_path):
        ydl_opts = {
            'outtmpl': output_path,
            'format': 'mp4/best[ext=mp4]/best',
            'quiet': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"✅ Downloaded: {output_path}")
    else:
        print(f"✅ Already exists: {output_path}")

def download_music(url, output_path):
    if not os.path.exists(output_path):
        ydl_opts = {
            'outtmpl': output_path,
            'format': 'bestaudio/best',
            'quiet': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"✅ Music downloaded: {output_path}")
    else:
        print(f"✅ Music already exists: {output_path}")

print("⬇️ Downloading anime clip...")
download_file(VIDEO_URL, "assets/clip.mp4")

print("⬇️ Downloading music...")
download_music(MUSIC_URL, "assets/music.mp3")

# ─── Voice + Timestamps ──────────────────────────────────────

async def generate_voice():
    communicate = edge_tts.Communicate(VOICE_TEXT, "en-US-GuyNeural")
    words = []
    audio_chunks = []

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            words.append({
                "word": chunk["text"],
                "start": chunk["offset"] / 10_000_000,
                "end": (chunk["offset"] + chunk["duration"]) / 10_000_000
            })

    with open("assets/voice.mp3", "wb") as f:
        for c in audio_chunks:
            f.write(c)

    with open("assets/words.json", "w") as f:
        json.dump(words, f, indent=2)

    print(f"✅ Voice generated with {len(words)} words!")

print("🎙️ Generating voice with word timestamps...")
asyncio.run(generate_voice())

# ─── Build drawtext filter ───────────────────────────────────

with open("assets/words.json") as f:
    words = json.load(f)

drawtext_filters = []

for i, w in enumerate(words):
    start = w["start"]
    end = w["end"]
    word = w["word"].replace("'", "\\'").replace(":", "\\:").replace(",", "").replace(".", "")

    # All words shown dimly at same time (previous + next)
    # Highlighted word shown bright white + bigger

    # Background shadow
    drawtext_filters.append(
        f"drawtext=text='{word}'"
        f":fontsize=80"
        f":fontcolor=white@0.95"
        f":borderw=4"
        f":bordercolor=black@0.8"
        f":x=(w-text_w)/2"
        f":y=(h/2)-40"
        f":enable='between(t,{start:.3f},{end:.3f})'"
        f":box=1"
        f":boxcolor=black@0.4"
        f":boxborderw=10"
        f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    )

caption_filter = ",".join(drawtext_filters)

# ─── FFmpeg ──────────────────────────────────────────────────

filter_complex = (
    f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
    f"crop=1080:1920,"
    f"eq=contrast=1.3:brightness=-0.05:saturation=1.4[base];"
    f"[base]{caption_filter}[v];"
    f"[1:a]aloop=loop=-1:size=2e+09,atrim=duration=30,volume=0.25[a1];"
    f"[2:a]volume=1.0[a2];"
    f"[a1][a2]amix=inputs=2:duration=shortest[a]"
)

ffmpeg_command = [
    "ffmpeg", "-y",
    "-i", "assets/clip.mp4",
    "-i", "assets/music.mp3",
    "-i", "assets/voice.mp3",
    "-filter_complex", filter_complex,
    "-map", "[v]",
    "-map", "[a]",
    "-t", "30",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "23",
    "output/final.mp4"
]

print("🎬 Creating final video with captions...")
subprocess.run(ffmpeg_command, check=True)
print("✅ Done! output/final.mp4 ready hai!")
