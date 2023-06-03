from comrade.lib.standalone.markdown_utils import escape_md


def test_escape_md():
    test_str = "hello_world *this* is a `test` of _escaping_ markdown"

    assert (
        escape_md(test_str)
        == "hello\\_world \\*this\\* is a \\`test\\` of \\_escaping\\_ markdown"
    )
