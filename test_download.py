import os
import yt_dlp

os.makedirs("assets", exist_ok=True)

VIDEO_URL = "https://archive.org/download/BigBuckBunny_124/Content/big_buck_bunny_720p_surround.mp4"
MUSIC_URL = "https://archive.org/download/testmp3testfile/mpthreetest.mp3"

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

video_size = os.path.getsize("assets/clip.mp4") / (1024*1024)
music_size = os.path.getsize("assets/music.mp3") / (1024*1024)

print(f"\n📊 Video size: {video_size:.2f} MB")
print(f"📊 Music size: {music_size:.2f} MB")

if video_size > 1 and music_size > 0.1:
    print("\n✅ SUCCESS! Dono files ready hain!")
else:
    print("\n❌ FAILED! Files sahi download nahi hui!")
