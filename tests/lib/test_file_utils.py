from base64 import b64decode

from comrade.lib.file_utils import give_filename_extension

IMG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEUAAACnej3aAAAAAXRSTlMAQObYZgAAAApJREFUCNdjYAAAAAIAAeIhvDMAAAAASUVORK5CYII="
IMG_BYTES = b64decode(IMG_B64)

GARBAGE_BYTES = b"garbage"


def test_give_filename_extension_nominal():
    filename = "image"
    assert give_filename_extension(filename, IMG_BYTES) == "image.png"


def test_give_filename_extension_already_has_extension():
    filename = "image.png"
    assert give_filename_extension(filename, IMG_BYTES) == "image.png"


def test_give_filename_extension_octet_stream():
    filename = "garbage"
    assert give_filename_extension(filename, GARBAGE_BYTES) == "garbage.bin"
