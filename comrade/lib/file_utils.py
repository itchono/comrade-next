from __future__ import annotations

from mimetypes import guess_extension

from interactions.client.utils.serializer import get_file_mimetype


def give_filename_extension(filename: str, data: bytes) -> str:
    """
    Given a filename and some data, guess the extension of the file
    and return the filename with the extension appended.

    If it already has an extension, return the filename as-is.
    """
    if "." in filename:
        return filename
    else:
        # get_file_mimetype always has a return, so guess_extension will
        # never return None
        ext = guess_extension(get_file_mimetype(data), strict=False)
        return filename + ext
