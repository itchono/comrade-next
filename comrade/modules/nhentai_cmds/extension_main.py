from interactions import Extension

from .gallery_cmds import NHGalleryHandler
from .search_cmds import NHSearchHandler


class NHentai(Extension, NHSearchHandler, NHGalleryHandler):
    pass
