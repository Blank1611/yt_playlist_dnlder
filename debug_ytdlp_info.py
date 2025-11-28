from yt_dlp import YoutubeDL
from yt_dlp.utils import ExtractorError

url = "https://www.youtube.com/watch?v=7aTpZ2R8aA4"

ydl_opts = {
    "quiet": False,
    "skip_download": True,
    "ignoreerrors": True,  # let it try to continue
    "verbose": True,
}

with YoutubeDL(ydl_opts) as ydl:
    try:
        info = ydl.extract_info(url, download=False)
    except ExtractorError as e:
        print("\n=== EXTRACTOR ERROR CAUGHT ===")
        print("type:", type(e))
        print("msg :", str(e))
        info = None

    print("\n=== RAW INFO OBJECT ===")
    print(repr(info))
