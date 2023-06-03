import booru

from comrade.lib.booru_lib import BOORUS


def test_booru_dict():
    assert BOORUS["danbooru"] == booru.Danbooru
    assert BOORUS["gelbooru"] == booru.Gelbooru
