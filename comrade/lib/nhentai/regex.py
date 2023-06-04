import re

# Regex for extracting gallery ID from href tag
# e.g. <a href="/g/185217/1"> -> 185217
GALLERY_ID_REGEX = re.compile(r"/g/(\d+)/")


# Regex for extracting images ID from URL, based on cover image URL
# e.g. https://t3.nhentai.net/galleries/1019423/cover.jpg -> 1019423
IMAGES_ID_REGEX = re.compile(r"/galleries/(\d+)/cover")

# Regex for extracting image extension and page number from URL
# e.g. https://t3.nhentai.net/galleries/1019423/2t.jpg -> (2), (jpg)
# Must ignore other images
IMAGES_URL_REGEX = re.compile(r"/galleries/\d+/(\d+)(?:t|\.).+")
