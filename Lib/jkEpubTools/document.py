#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import errno

from os import makedirs
from os.path import dirname, exists, join
from shutil import copyfile

from jkEpubTools.files import ContainerXML, ContentOPF, EncryptionXML, EpubMimeType, IBooksDisplayOptions, NavXHTML, TocNCX, XHTMLFile
from jkEpubTools.metadata import MetaData


class BaseDocument(object):
    def get_id(self):
        return self._id
    
    def safe_makedirs(self, path):
        try:
            makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


class Document(BaseDocument):
    def __init__(self, doc_id="unknown", title=""):
        self._id = doc_id
        self.title = title
        
        self.chapters = []
        self.resources = []
        self.stylesheet = None
        
        self.cover = None
        self.metadata = None
    
    def __repr__(self):
        r = "Document '%s'\n    Chapters:\n" % self.title
        for c in self.chapters:
            r += "        %s\n        Sections:\n" % c.title
            for s in c.sections:
                r += "            %s\n" % s.name
        return r
    
    def as_dict(self):
        return {
            "id": self.get_id(),
            "title": self.title,
            "chapters": [
                "%03i_%s.json" % (
                    i+1, self.chapters[i].get_id()
                ) for i in range(len(self.chapters))
            ]
        }
    
    def set_metadata_from_dict(self, meta_dict):
        self.metadata = MetaData(meta_dict)
    
    def set_cover_from_dict(self, cover_dict):
        self.cover = Cover(cover_dict)
    
    def add_chapter_from_dict(self, chapter_dict):
        c = Chapter()
        c.from_dict(chapter_dict)
        self.chapters.append(c)
    
    def add_chapters_from_dict_list(self, chapter_list):
        for chapter_dict in chapter_list:
            self.add_chapter_from_dict(chapter_dict)
    
    def add_resource_from_dict(self, resource_dict):
        self.resources.append(Resource(resource_dict))
    
    def add_resources_from_dict_list(self, resource_list):
        for resource_dict in resource_list:
            self.add_resource_from_dict(resource_dict)
    
    def save_epub(self, epub_root):
        self.safe_makedirs(join(epub_root, "OEBPS"))
        self.safe_makedirs(join(epub_root, "META-INF"))
        
        # mimetype file
        mimetype = EpubMimeType()
        mimetype.save(epub_root)
        
        content_opf = ContentOPF(self)
        content_opf.save(epub_root)
        
        if self.cover is not None:
            self.cover.save_epub(epub_root)
        
        toc_ncx = TocNCX(self)
        toc_ncx.save(epub_root)
        
        if self.metadata.version == "3.0":
            nav_xhtml = NavXHTML(self)
            nav_xhtml.save(epub_root)
        
        for i in range(len(self.chapters)):
            file_name = "%03i.xhtml" % (i+1)
            self.chapters[i].save_epub(epub_root, file_name)
        
        for res in self.resources:
            res.save_epub(epub_root)
        
        # META-INF
        
        container_xml = ContainerXML()
        container_xml.save(epub_root)
        
        encryption_xml = EncryptionXML(self)
        encryption_xml.save(epub_root)
        
        ibooks_options = IBooksDisplayOptions()
        ibooks_options.save(epub_root)


class Chapter(BaseDocument):
    def __init__(self, chapter_id="", title=""):
        self._id = chapter_id
        self.title = title
        self.src = None
        self.sections = []
    
    def as_dict(self):
        return {
            "id": self.get_id(),
            "sections": [self.sections[i].as_dict() for i in range(len(self.sections))],
        }
    
    def from_dict(self, chapter_dict):
        self._id = chapter_dict.get("id", "")
        self.title = chapter_dict.get("title", "Untitled Chapter")
        self.src = chapter_dict.get("src", None)
    
    def as_html(self):
        #print "Chapter.as_html:", self.get_id()
        x = XHTMLFile(title=self.title, stylesheet_path='style/stylesheet.css')
        h = x.get_header()
        h += '    <h1>%s</h1>\n' % self.title
        for i in range(len(self.sections)):
            s = self.sections[i]
            h += s.as_html()
        h += x.get_footer()
        return h
    
    def save_epub(self, epub_root, file_name):
        base_dir = join(epub_root, 'OEBPS')
        self.safe_makedirs(base_dir)
        if self.src is None:
            # Chapter content has been built programmatically
            c = self.as_html()
            f = codecs.open(join(base_dir, file_name), 'wb', 'utf-8')
            f.write(c)
            f.close()
        else:
            # Chapter content is copied verbatim from src file
            if exists(self.src):
                copyfile(self.src, join(base_dir, file_name))
            else:
                print "ERROR: Chapter source not found: '%s'" % self.src


class Cover(BaseDocument):
    def __init__(self, cover_dict):
        self.src = cover_dict.get("src", None)
        self.uri = cover_dict.get("uri", None)
        # TODO guess mime type if not supplied
        self.mime = cover_dict.get("mime", None)
        if self.mime is None:
            from jkEpubTools.mime import guess_mime_type
            self.mime = guess_mime_type(self.uri)
        self.encrypt = cover_dict.get("encrypt", False)
        self.width = cover_dict.get("width", None)
        self.height = cover_dict.get("height", None)
        if None in (self.width, self.height):
            print "ERROR: width and height of cover image must be supplied, or resulting epub will be invalid."
    
    def as_html(self):
        #print "Cover.as_html:", self.get_id()
        x = XHTMLFile(title='Cover', stylesheet_path='style/stylesheet.css')
        h = x.get_header()
        h += '    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"\n'
        h += '      width="100%%" height="100%%" viewBox="0 0 %s %s" preserveAspectRatio="xMidYMid meet">\n' % (self.width, self.height)
        h += '      <image width="%s" height="%s" xlink:href="%s" />\n' % (self.width, self.height, self.uri)
        h += '    </svg>\n'
        h += x.get_footer()
        return h
    
    def save_epub(self, epub_root):
        base_dir = join(epub_root, 'OEBPS')
        self.safe_makedirs(base_dir)
        c = self.as_html()
        f = codecs.open(join(base_dir, 'cover.xhtml'), 'wb', 'utf-8')
        f.write(c)
        f.close()
        
        self.safe_makedirs(join(epub_root, "OEBPS", dirname(self.uri)))
        if exists(self.src):
            copyfile(self.src, join(epub_root, "OEBPS", self.uri))
        else:
            print "ERROR: Cover image not found: '%s'" % self.src


class Resource(BaseDocument):
    def __init__(self, resource_dict):
        self.src = resource_dict.get("src", None)
        self.uri = resource_dict.get("uri", None)
        # TODO guess mime type if not supplied
        self.mime = resource_dict.get("mime", None)
        if self.mime is None:
            from jkEpubTools.mime import guess_mime_type
            self.mime = guess_mime_type(self.uri)
        self.encrypt = resource_dict.get("encrypt", False)
    
    def save_epub(self, epub_root):
        self.safe_makedirs(join(epub_root, "OEBPS", dirname(self.uri)))
        if exists(self.src):
            copyfile(self.src, join(epub_root, "OEBPS", self.uri))
        else:
            print "ERROR: Resource not found: '%s'" % self.src