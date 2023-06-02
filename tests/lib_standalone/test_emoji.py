from comrade.lib.standalone.regional_indicator import (
    regional_indicator_to_txt,
    txt_to_regional_indicator,
)


def test_emoji_fwd_conversion():
    test_s = "apple"
    expected_s = "🇦🇵🇵🇱🇪"

    assert txt_to_regional_indicator(test_s) == expected_s


def test_emoji_rev_conversion():
    test_s = "🇦🇵🇵🇱🇪"
    expected_s = "apple"

    assert regional_indicator_to_txt(test_s) == expected_s
