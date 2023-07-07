import random

import pytest
from interactions import CustomEmoji

from comrade.lib.text_utils.funny_formatting import emojify, mock, owoify
from comrade.lib.text_utils.length_filter import text_safe_length
from comrade.lib.text_utils.markdown import escape_md
from comrade.lib.text_utils.regional_indicator import (
    regional_indicator_to_txt,
    txt_to_regional_indicator,
)


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


def test_escape_md():
    test_str = "hello_world *this* is a `test` of _escaping_ markdown"

    assert (
        escape_md(test_str)
        == "hello\\_world \\*this\\* is a \\`test\\` of \\_escaping\\_ markdown"
    )


def test_text_safe_length_nominal():
    """
    Make sure a regular string is returned
    when it is shorter than the limit
    """
    assert text_safe_length("hello world", 100) == "hello world"


def test_text_safe_length_truncate():
    """
    Make sure a string is truncated when it is
    longer than the limit
    """
    result_str = text_safe_length("hello world", 5)

    assert result_str == "he..."


def test_text_safe_length_edge():
    """
    Make sure a string is not truncated with ellipsis
    when it is exactly the same length as the limit
    """
    result_str = text_safe_length("hello world", 11)
    assert result_str == "hello world"


def test_reg_ind_fwd_conversion():
    test_s = "apple"
    expected_s = "🇦🇵🇵🇱🇪"

    assert txt_to_regional_indicator(test_s) == expected_s


def test_reg_ind_rev_conversion():
    test_s = "🇦🇵🇵🇱🇪"
    expected_s = "apple"

    assert regional_indicator_to_txt(test_s) == expected_s
