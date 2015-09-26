#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
from jkEpubTools import build
from jkEpubTools.document import Document

build_tolino = False

if build_tolino:
    epub_version = "2.0"
    obfuscate_fonts = False
else:
    epub_version = "3.0"
    obfuscate_fonts = True

doc = Document(
    "de.kutilek.the-haunter-of-the-dark",
    "The Haunter of the Dark"
)

doc.set_metadata_from_dict({
    "version": epub_version,
    "publisher": "Jens Kutilek",
    "rights": "Copyright 2015 by Jens Kutilek. All rights reserved.",
    "language": "en",
    "author": "H. P. Lovecraft",
    "author_sortname": "Lovecraft, H. P.",
    "title": "The Haunter of the Dark",
    "uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, 'http://www.kutilek.de/the-haunter-of-the-dark')),
    "subject": "Horror",
})

doc.stylesheet = "style/stylesheet.css"

doc.set_cover_from_dict(
    {
        "src": "resources/cover-image.jpg",
        "uri": "cover-image.jpg",
        "mime": "image/jpeg",
        "width": 768,
        "height": 1024,
    }
)

doc.add_resources_from_dict_list([
    {
        "src": "resources/stylesheet.css",
        "uri": doc.stylesheet,
        "mime": "text/css",
    },
    {
        "src": "resources/hertz-specimen-1.png",
        "uri": "hertz-specimen-1.png",
        "mime": "image/png", # svg+xml
    },
    {
        "src": "resources/hertz-specimen-2.png",
        "uri": "hertz-specimen-2.png",
        "mime": "image/png", # svg+xml
    },
    {
        "src": "resources/hertz-specimen-3.png",
        "uri": "hertz-specimen-3.png",
        "mime": "image/png", # svg+xml
    },
    {
        "src": "resources/hertz-specimen-4.png",
        "uri": "hertz-specimen-4.png",
        "mime": "image/png", # svg+xml
    },
    {
        "src": "resources/hertz-specimen-5.png",
        "uri": "hertz-specimen-5.png",
        "mime": "image/png", # svg+xml
    },
    {
        "src": "resources/hertz-specimen-6.png",
        "uri": "hertz-specimen-6.png",
        "mime": "image/png", # svg+xml
    },
    {
        "src": "resources/Merriweather-Regular.ttf",
        "uri": "style/Merriweather-Regular.ttf",
        "mime": "application/x-font-opentype",
        "encrypt": obfuscate_fonts,
    },
    {
        "src": "resources/Merriweather-Italic.ttf",
        "uri": "style/Merriweather-Italic.ttf",
        "mime": "application/x-font-opentype",
        "encrypt": obfuscate_fonts,
    },
    {
        "src": "resources/Merriweather-Light.ttf",
        "uri": "style/Merriweather-Light.ttf",
        "mime": "application/x-font-opentype",
        "encrypt": obfuscate_fonts,
    },
])

doc.add_chapters_from_dict_list([
    {
        "id": "x1",
        "title": "About FF Hertz",
        "src": "contents/001.xhtml",
    },
    {
        "id": "x2",
        "title": "The Haunter of the Dark",
        "src": "contents/002.xhtml",
    },
    {
        "id": "x3",
        "title": "Trademark Notice",
        "src": "contents/003.xhtml",
    },
])

compile_path = './build/epub'

doc.save_epub(compile_path)
build(compile_path, 'The Haunter of the Dark.epub')