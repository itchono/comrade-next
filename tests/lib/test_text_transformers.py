import random

import pytest
from interactions import CustomEmoji

from comrade.lib.text_utils.funny_formatting import emojify, mock, owoify


@pytest.fixture
def example_str() -> str:
    return "hello world We are Le Monke"


@pytest.fixture
def fake_emoji() -> CustomEmoji:
    return CustomEmoji.from_dict(
        {
            "id": 123456789012345678,
            "name": "test_emoji",
            "animated": False,
        },
        client=None,
        guild_id=123456789012345678,
    )


def test_owoify(example_str: str):
    assert owoify(example_str) == "hewwo wowwd We awe We Monke"


def test_mock(example_str: str):
    random.seed(0)  # This is to make sure the test is deterministic
    assert mock(example_str) == "heLlo worLD WE ArE le monKe"


def test_emojify(example_str: str, fake_emoji: CustomEmoji):
    assert emojify([fake_emoji], example_str) == example_str.replace(
        " ", "<:test_emoji:123456789012345678>"
    )
