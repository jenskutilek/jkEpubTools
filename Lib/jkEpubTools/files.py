#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import time

from os.path import join, exists, isdir


class XHTMLFile(object):
    def __init__(self, language="en", title="No Title", stylesheet_path=None):
        self.language = language
        self.title = title
        self.stylesheet_path = stylesheet_path # relative path
    
    def get_header(self):
        h = '<?xml version="1.0" encoding="utf-8"?>\n<html xmlns="http://www.w3.org/1999/xhtml"\n      xmlns:ops="http://www.idpf.org/2007/ops"\n      xml:lang="%s">\n' % self.language
        h += '  <head>\n'
        h += '    <title>%s</title>\n' % self.title
        if self.stylesheet_path is not None:
            h += '    <link href="%s" type="text/css" rel="stylesheet"/>\n' % self.stylesheet_path
        h += '  </head>\n'
        h += '  <body>\n'
        
        return h
    
    def get_footer(self):
        return "  </body>\n</html>\n"


class EpubFile(object):
    def save(self, epub_root):
        c = self.get_contents()
        f = codecs.open(join(epub_root, self.name), "wb", "utf-8")
        f.write(c)
        f.close()


class ContainerXML(EpubFile):
    def __init__(self):
        self.name = "container.xml"
    
    def get_contents(self):
        return '<?xml version="1.0"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n   <rootfiles>\n      <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n   </rootfiles>\n</container>\n'


class ContentOPF(EpubFile):
    def __init__(self, document):
        self.document = document
        self.name = "content.opf"
    
    def get_contents(self):
        
        # header
        
        h = '<?xml version="1.0" encoding="UTF-8"?>\n<package xmlns="http://www.idpf.org/2007/opf" version="%s" unique-identifier="uuid_id">\n' % self.document.metadata.version
        
        # Meta data element
        
        h += '  <metadata xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        if self.document.metadata.publisher is not None:
            h += "    <dc:publisher>%s</dc:publisher>\n" % self.document.metadata.publisher
        if self.document.metadata.rights is not None:
            h += "    <dc:rights>%s</dc:rights>\n" % self.document.metadata.rights
        if self.document.metadata.language is not None:
            h += "    <dc:language>%s</dc:language>\n" % self.document.metadata.language
        else:
            h += "    <dc:language>en</dc:language>\n"
        if self.document.metadata.author is not None:
            if self.document.metadata.author_sortname is None:
                h += '    <dc:creator opf:role="aut">%s</dc:creator>\n' % self.document.metadata.author
            else:
                h += '    <dc:creator opf:file-as="%s" opf:role="aut">%s</dc:creator>\n' % (
                    self.document.metadata.author_sortname,
                    self.document.metadata.author
                )
        if self.document.metadata.title is not None:
            h += "    <dc:title>%s</dc:title>\n" % self.document.metadata.title
        if self.document.metadata.cover is not None:
            h += '    <meta name="cover" content="cover"/>\n'
        if self.document.metadata.date is None:
            h += '    <dc:date>%s</dc:date>\n' % time.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        else:
            h += '    <dc:date>%s</dc:date>\n' % self.document.metadata.date
        h += '    <dc:identifier id="uuid_id" opf:scheme="uuid">%s</dc:identifier>\n' % self.document.metadata.uuid
        if self.document.metadata.subject is not None:
            h += '    <dc:subject>%s</dc:subject>\n' % self.document.metadata.subject
        h += '  </metadata>\n'
        
        # Manifest element
        
        h += '  <manifest>\n'
        if self.document.metadata.cover is not None:
            h += '    <item href="%s" id="cover" media-type="image/jpeg"/>\n' % (self.document.metadata.cover, self.document.metadata.cover_type)
        for i in range(len(self.document.chapters)):
            h += '    <item href="OEBPS/%03i.xhtml" id="x%i" media-type="application/xhtml+xml"/>\n' % (i+1, i+1)
        h += '  </manifest>\n'
        
        # Spine element
        
        h += '  <spine toc="ncx">\n'
        for i in range(len(self.document.chapters)):
            h += '    <itemref idref="x%i"/>\n' % (i+1)
        h += '  </spine>\n'
        
        # Guide element
        
        h += '  <guide>\n'
        h += '  </guide>\n'
        
        h += "</package>\n"
        return h


class EncryptionXML(EpubFile):
    def __init__(self, document):
        self.document = document
        self.name = "encryption.xml"
    
    def get_contents(self):
        h = '<encryption\n    xmlns="urn:oasis:names:tc:opendocument:xmlns:container"\n    xmlns:enc="http://www.w3.org/2001/04/xmlenc#">\n'
        for r in self.document.resources:
            if r.encrypt:
                h += '    <enc:EncryptedData>\n        <enc:EncryptionMethod Algorithm="http://www.idpf.org/2008/embedding"/>\n        <enc:CipherData>\n            <enc:CipherReference URI="%s" />\n        </enc:CipherData>\n    </enc:EncryptedData>\n' % r.uri
        h += '</encryption>\n'
        return h


class TocNCX(EpubFile):
    def __init__(self, document):
        self.document = document
        self.name = "toc.ncx"
    
    def get_contents(self):
        
        # header
        
        h = u'<?xml version="1.0" encoding="utf-8"?>\n<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="%s">\n  <head>\n' % self.document.metadata.language
        if self.document.metadata.uuid is not None:
            h += '    <meta content="%s" name="dtb:uid"/>\n' % self.document.metadata.uuid
        
        # FIXME
        h += '    <meta content="2" name="dtb:depth"/>\n'
        h += '    <meta content="0" name="dtb:totalPageCount"/>\n'
        h += '    <meta content="0" name="dtb:maxPageNumber"/>\n'
        h += '  </head>\n'
        
        if self.document.metadata.title is not None:
            h += '  <docTitle>\n    <text>%s</text>\n  </docTitle>\n' % self.document.metadata.title
        if self.document.metadata.title is not None:
            h += '  <docAuthor>\n    <text>%s</text>\n  </docAuthor>\n' % self.document.metadata.author
        
        # nav map
        
        h += '  <navMap>\n'
        for i in range(len(self.document.chapters)):
            chapter = self.document.chapters[i]
            h += '    <navPoint class="chapter" id="navpoint-%i" playOrder="%i"/>\n' % (i+1, i)
            h += '        <navLabel>\n            <text>%s</text>\n' % chapter.title
            h += '        </navLabel>\n'
            h += '        <content src="OEBPS/%03i.xhtml"/>\n' % (i+1)
            h += '    </navPoint>\n'
        h += '  </navMap>\n'
        
        # footer
        
        h += '</ncx>\n'
        
        return h


class EpubMimeType(EpubFile):
    def __init__(self):
        self.name = 'mimetype'
    
    def get_contents(self):
        return 'application/epub+zip'