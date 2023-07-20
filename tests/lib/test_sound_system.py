import pytest
from pydub import AudioSegment

from comrade.lib.sound_system import SoundboardAudio, download_video_to_mp3


@pytest.mark.online
def test_download_video_to_mp3_nominal():
    # You Watanabe saying "OHAYOUSORO" from Love Live! Sunshine!!
    # this video may get taken down, so if it does, just replace the url with another
    url = "https://www.youtube.com/watch?v=1ZNYksU0_jg"
    raw_audio = download_video_to_mp3(url)

    assert raw_audio is not None

    audio = AudioSegment.from_mp3(raw_audio)

    assert audio.duration_seconds > 2


@pytest.mark.online
def test_download_video_to_mp3_limited_duration():
    url = "https://www.youtube.com/watch?v=1ZNYksU0_jg"
    raw_audio = download_video_to_mp3(url, limit_time=1)

    assert raw_audio is not None

    audio = AudioSegment.from_mp3(raw_audio)
    assert audio.duration_seconds <= 1


@pytest.mark.online
def test_download_video_to_mp3_too_long():
    with pytest.raises(ValueError):
        # steve1989mreinfo, 15 min long video
        url = "https://www.youtube.com/watch?v=u_sY-nJ179U"
        download_video_to_mp3(url)


def test_soundboardaudio():
    audio = SoundboardAudio("test", 123, 456, "https://example.com", "👍")
    assert audio.button.label == "test"
    assert audio.button.emoji.name == "👍"
    assert audio.button.custom_id.startswith("soundboard:")
