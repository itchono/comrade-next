from typing import Type

import booru as booru_lib

# Create a type alias that can be any of the booru classes
BooruType = (
    booru_lib.Danbooru
    | booru_lib.Gelbooru
    | booru_lib.Rule34
    | booru_lib.Safebooru
    | booru_lib.Xbooru
)
# Execute some wizardry using type hints to get a dict of booru names to booru classes
BOORUS: dict[str, Type[BooruType]] = {
    t.__name__.lower(): t for t in BooruType.__args__
}
