import re

# Regex for extracting gallery ID from href tag
# e.g. <a href="/g/185217/1"> -> 185217
GALLERY_ID_REGEX = re.compile(r"/g/(\d+)")


# Regex for extracting images ID from URL, based on cover image URL
# e.g. https://t3.nhentai.net/galleries/1019423/cover.jpg -> 1019423
IMAGES_ID_REGEX = re.compile(r"/(\d+)/cover")

# Regex for extracting image extension and page number from URL
# e.g. https://t3.nhentai.net/galleries/1019423/2t.jpg -> (2), (jpg)
# Must ignore other images (e.g. ads, thumbnails) that may be present
# Capture group 1: page number
# Capture group 2: image extension
IMAGES_URL_REGEX = re.compile(r"/\d+/(\d+)(?:t|\.)\.(jpg|png|gif)")


# Regex for extracting tags from tag list (<a> tags inside <div> with class "tag-container")
# e.g. <a href="/tag/sole-female/" class="tag tag-35762"> -> (sole-female)
TAGS_REGEX = re.compile(r"/tag/([\w-]+)/")
