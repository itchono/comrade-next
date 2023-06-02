import booru as booru_lib

from comrade.lib.standalone.booru import BOORUS


def test_booru_dict():
    assert BOORUS["danbooru"] == booru_lib.Danbooru
    assert BOORUS["gelbooru"] == booru_lib.Gelbooru
