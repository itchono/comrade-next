from typing import Type

import booru

# Create a type alias that can be any of the booru classes
BooruType = (
    booru.Danbooru
    | booru.Gelbooru
    | booru.Rule34
    | booru.Safebooru
    | booru.Xbooru
)
# Execute some wizardry using type hints to get a dict of booru names to booru classes
BOORUS: dict[str, Type[BooruType]] = {
    t.__name__.lower(): t for t in BooruType.__args__
}
