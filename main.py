import os
import asyncio
import edge_tts
import subprocess
import json
import urllib.request

os.makedirs("assets", exist_ok=True)
os.makedirs("output", exist_ok=True)

# ─── Download Video from Pexels (GitHub Actions friendly) ────
# Get FREE API key from: https://www.pexels.com/api/
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

MUSIC_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3"

VOICE_TEXT = "Discipline beats motivation. Most people quit too early. Stay consistent. Your future self will thank you."


def download_pexels_video(path):
    """Download a free HD video from Pexels API"""
    if os.path.exists(path):
        print(f"✅ Already exists: {path}")
        return

    if not PEXELS_API_KEY:
        raise ValueError("❌ PEXELS_API_KEY not set! Add it as a GitHub Secret.")

    print("⬇️ Fetching video from Pexels...")
    req = urllib.request.Request(
        "https://api.pexels.com/videos/search?query=motivation+city+night&per_page=1&orientation=portrait",
        headers={"Authorization": PEXELS_API_KEY}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    # Get best quality video file
    video_files = data["videos"][0]["video_files"]
    # Prefer HD portrait video
    hd_files = [v for v in video_files if v.get("height", 0) >= 1080]
    best = hd_files[0] if hd_files else video_files[0]

    video_url = best["link"]
    print(f"⬇️ Downloading video: {video_url[:60]}...")
    urllib.request.urlretrieve(video_url, path)
    size = os.path.getsize(path) / (1024 * 1024)
    print(f"✅ Video downloaded! Size: {size:.2f} MB")


def download(url, path):
    if not os.path.exists(path):
        print(f"⬇️ Downloading {path}...")
        urllib.request.urlretrieve(url, path)
        size = os.path.getsize(path) / (1024 * 1024)
        print(f"✅ Done! Size: {size:.2f} MB")
    else:
        print(f"✅ Already exists: {path}")


download_pexels_video("assets/clip.mp4")
download(MUSIC_URL, "assets/music.mp3")


# ─── Voice + Word Timestamps ─────────────────────────────────

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

    print(f"✅ Voice ready! Words: {len(words)}")


print("🎙️ Generating voice...")
asyncio.run(generate_voice())

# ─── Word-by-word Captions ───────────────────────────────────

with open("assets/words.json") as f:
    words = json.load(f)

drawtext_filters = []
font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

for w in words:
    start = w["start"]
    end = w["end"]
    word = (w["word"]
            .replace("'", "")
            .replace(":", "")
            .replace(",", "")
            .replace(".", "")
            .replace('"', ""))

    if not word.strip():
        continue

    drawtext_filters.append(
        f"drawtext=fontfile={font}"
        f":text='{word}'"
        f":fontsize=90"
        f":fontcolor=white"
        f":borderw=5"
        f":bordercolor=black"
        f":x=(w-text_w)/2"
        f":y=(h*2/3)"
        f":enable='between(t,{start:.3f},{end:.3f})'"
        f":box=1"
        f":boxcolor=black@0.5"
        f":boxborderw=12"
    )

caption_filter = ",".join(drawtext_filters)

# ─── FFmpeg Final Render ─────────────────────────────────────

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

print("🎬 Rendering video with captions...")
subprocess.run(ffmpeg_command, check=True)
print("✅ output/final.mp4 ready!")
