from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from yt_dlp import YoutubeDL

MAX_DOWNLOAD_TIME = 60 * 10  # 10 minutes


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
            # limit the duration of the video in postprocessing
            ydl_opts["postprocessor_args"] = [
                "-ss",
                "0",
                "-t",
                str(limit_time),
            ]

        with YoutubeDL(ydl_opts) as ydl:
            # sanity check length first
            info_dict = ydl.extract_info(url, download=False)
            if info_dict["duration"] > MAX_DOWNLOAD_TIME:
                raise ValueError(
                    f"Video duration exceeds maximum of {MAX_DOWNLOAD_TIME} seconds"
                )

            ydl.download([url])

        # get the data from the temporary file
        data = f_path.with_suffix(".mp3").read_bytes()

    return BytesIO(data)
