from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from yt_dlp import YoutubeDL


def download_video_to_mp3(url: str, limit_time: int = None) -> BytesIO:
    """
    Download a YouTube video as an MP3 file.

    automatically creates a temporary file to store the MP3 file.
    and cleans up the file after the function is done.

    Parameters
    ----------
    url : str
        The URL of the video to download.
    limit_time : int
        Maximum number of seconds to download.

    Returns
    -------
    BytesIO
        The MP3 file.
    """

    with TemporaryDirectory() as temp_dir:
        f_path = Path(temp_dir) / "temp_ytdl"

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(f_path),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        if limit_time is not None:
            # limit the duration of the video
            ydl_opts.update({"noplaylist": True, "duration": limit_time})

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # get the data from the temporary file
        data = f_path.with_suffix(".mp3").read_bytes()

    return BytesIO(data)
