#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import errno

from os import makedirs
from os.path import exists, join
from shutil import copyfile

from jkEpubTools.files import ContentOPF, TocNCX, EpubMimeType, XHTMLFile
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
        self.safe_makedirs(epub_root)
        
        # mimetype file
        mimetype = EpubMimeType()
        mimetype.save(epub_root)
        
        content_opf = ContentOPF(self)
        content_opf.save(epub_root)
        
        toc_ncx = TocNCX(self)
        toc_ncx.save(epub_root)
        
        for i in range(len(self.chapters)):
            file_name = "%03i.xhtml" % (i+1)
            self.chapters[i].save_epub(epub_root, file_name)


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
            src = self.src
            if exists(src):
                copyfile(src, join(base_dir, file_name))
            else:
                print "ERROR: Chapter source not found: '%s'" % self.src


class Resource(object):
    def __init__(self, resource_dict):
        self.src = resource_dict.get("src", None)
        self.uri = resource_dict.get("uri", None)
        self.encrypt = resource_dict.get("encrypt", False)