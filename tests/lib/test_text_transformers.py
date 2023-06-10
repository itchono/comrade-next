import random

import pytest

from comrade.lib.text_utils.funny_formatting import mock, owoify


@pytest.fixture
def example_str() -> str:
    return "hello world We are Le Monke"


def test_owoify(example_str: str):
    assert owoify(example_str) == "hewwo wowwd We awe We Monke"


def test_mock(example_str: str):
    random.seed(0)  # This is to make sure the test is deterministic
    assert mock(example_str) == "heLlo worLD WE ArE le monKe"


# Pending: a way to test emojify offline
