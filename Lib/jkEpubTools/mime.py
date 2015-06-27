#!/usr/bin/env python
# -*- coding: utf-8 -*-

from string import rsplit

mime_types = {
    "css":   "text/css",
    "otf":   "application/x-font-opentype",
    "svg":   "image/svg+xml",
    "xhtml": "application/xhtml+xml",
    "xml":   "application/xhtml+xml",
    "woff":  "application/font-woff",
}

def guess_mime_type(filename):
    suffix = filename.rsplit(".")[-1]
    if suffix in mime_types:
        return mime_types[suffix]
    return "application/octet-stream"