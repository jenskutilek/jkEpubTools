from __future__ import annotations

import codecs
import time
from os.path import exists, isdir, join
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jkEpubTools.document import Document


class XHTMLFile:
    def __init__(
        self,
        language: str = "en",
        title: str = "No Title",
        stylesheet_path: str | None = None,
    ) -> None:
        self.language = language
        self.title = title
        self.stylesheet_path = stylesheet_path  # relative path

    def get_header(self) -> str:
        h = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml"\n'
            '      xmlns:ops="http://www.idpf.org/2007/ops"\n'
            f'      xml:lang="{self.language}">\n'
        )
        h += "  <head>\n"
        h += "    <title>%s</title>\n" % self.title
        if self.stylesheet_path is not None:
            h += (
                '    <link href="%s" type="text/css" rel="stylesheet"/>\n'
                % self.stylesheet_path
            )
        h += "  </head>\n"
        h += "  <body>\n"

        return h

    def get_footer(self) -> str:
        return "  </body>\n</html>\n"


class EpubFile:
    def save(self, epub_root: str) -> None:
        if self.path is not None:
            path = join(epub_root, self.path, self.name)
        else:
            path = join(epub_root, self.name)
        c = self.get_contents()
        if c is not None:
            f = codecs.open(path, "wb", "utf-8")
            f.write(c)
            f.close()


class ContainerXML(EpubFile):
    def __init__(self) -> None:
        self.path = "META-INF"
        self.name = "container.xml"

    def get_contents(self) -> str:
        return (
            '<?xml version="1.0"?>\n'
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
            "   <rootfiles>\n"
            '      <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
            "   </rootfiles>\n'"
            "'</container>\n"
        )


class ContentOPF(EpubFile):
    def __init__(self, document: Document) -> None:
        self.document = document
        self.path = "OEBPS"
        self.name = "content.opf"

    def get_contents(self) -> str:
        # header
        assert self.document.metadata is not None
        h = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<package xmlns="http://www.idpf.org/2007/opf" version="{self.document.metadata.version}" unique-identifier="uuid_id">\n'
        )

        # Meta data element

        h += '  <metadata xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        if self.document.metadata.publisher is not None:
            h += (
                f"    <dc:publisher>{self.document.metadata.publisher}</dc:publisher>\n"
            )

        if self.document.metadata.rights is not None:
            h += f"    <dc:rights>{self.document.metadata.rights}</dc:rights>\n"
        if self.document.metadata.language is not None:
            h += f"    <dc:language>{self.document.metadata.language}</dc:language>\n"
        else:
            h += "    <dc:language>en</dc:language>\n"
        if self.document.metadata.author is not None:
            if self.document.metadata.author_sortname is None:
                h += f'    <dc:creator opf:role="aut">{self.document.metadata.author}</dc:creator>\n'
            else:
                h += f'    <dc:creator opf:file-as="{self.document.metadata.author_sortname}" opf:role="aut">{self.document.metadata.author}</dc:creator>\n'
        if self.document.metadata.title is not None:
            h += f"    <dc:title>{self.document.metadata.title}</dc:title>\n"
        if self.document.cover is not None:
            h += '    <meta name="cover" content="cover-image"/>\n'
        if self.document.metadata.date is None:
            h += "    <dc:date>%s</dc:date>\n" % time.strftime(
                "%Y-%m-%dT%H:%M:%S+00:00"
            )
        else:
            h += f"    <dc:date>{self.document.metadata.date}</dc:date>\n"
        h += f'    <dc:identifier id="uuid_id" opf:scheme="uuid">{self.document.metadata.uuid}</dc:identifier>\n'
        if self.document.metadata.subject is not None:
            h += f"    <dc:subject>{self.document.metadata.subject}</dc:subject>\n"
        h += "  </metadata>\n"

        # Manifest element

        h += "  <manifest>\n"
        if self.document.cover is not None:
            h += f'    <item href="{self.document.cover.uri}" id="cover-image" media-type="{self.document.cover.mime}"/>\n'

        h += (
            '    <item id="ncx"\n'
            '          href="toc.ncx"\n'
            '          media-type="application/x-dtbncx+xml"/>\n'
        )

        if self.document.metadata.version == "3.0":
            h += (
                '    <item id="nav"\n'
                '          href="nav.xhtml"\n'
                '          media-type="application/xhtml+xml"\n'
                '          properties="nav"/>\n'
            )

        if self.document.cover is not None:
            h += (
                '    <item id="cover"\n'
                '          href="cover.xhtml"\n'
                '          media-type="application/xhtml+xml"/>\n'
            )

        for i in range(len(self.document.chapters)):
            h += (
                f'    <item id="x{i + 1}"\n'
                f'          href="%{i + 1:03i}.xhtml"\n'
                '          media-type="application/xhtml+xml"/>\n'
            )

        for i in range(len(self.document.resources)):
            r = self.document.resources[i]
            h += (
                f'    <item id="resource{i}"\n'
                f'          href="{r.uri}"\n'
                f'          media-type="{r.mime}"/>\n'
            )

        h += "  </manifest>\n"

        # Spine element

        h += '  <spine toc="ncx">\n'

        if self.document.metadata.version == "3.0":
            h += '    <itemref idref="nav"/>\n'

        if self.document.cover is not None:
            h += '    <itemref idref="cover"/>\n'

        for i in range(len(self.document.chapters)):
            h += '    <itemref idref="x%i"/>\n' % (i + 1)
        h += "  </spine>\n"

        # Guide element

        h += "  <guide>\n"
        # TODO?
        h += '    <reference href="cover.xhtml" title="Cover" type="cover" />\n'
        h += "  </guide>\n"

        h += "</package>\n"
        return h


class EncryptionXML(EpubFile):
    def __init__(self, document: Document) -> None:
        self.document = document
        self.path = "META-INF"
        self.name = "encryption.xml"

    def get_contents(self) -> str | None:
        num_encrypted_items = 0
        h = (
            "<encryption\n"
            '    xmlns="urn:oasis:names:tc:opendocument:xmlns:container"\n'
            '    xmlns:enc="http://www.w3.org/2001/04/xmlenc#">\n'
        )
        for r in self.document.resources:
            if r.encrypt:
                num_encrypted_items += 1
                h += (
                    "    <enc:EncryptedData>\n"
                    '        <enc:EncryptionMethod Algorithm="http://www.idpf.org/2008/embedding"/>\n'
                    "        <enc:CipherData>\n"
                    f'            <enc:CipherReference URI="OEBPS/{r.uri}" />\n'
                    "        </enc:CipherData>\n"
                    "    </enc:EncryptedData>\n"
                )
        h += "</encryption>\n"
        if num_encrypted_items == 0:
            return None
        return h


class NavXHTML(EpubFile):
    def __init__(self, document: Document) -> None:
        self.document = document
        self.path = "OEBPS"
        self.name = "nav.xhtml"

    def get_contents(self) -> str:
        # header
        assert self.document.metadata is not None
        h = (
            '<?xml version="1.0" encoding="UTF-8" ?>\n'
            '<html xmlns="http://www.w3.org/1999/xhtml"\n'
            '    xmlns:ops="http://www.idpf.org/2007/ops"\n'
            f'    xml:lang="{self.document.metadata.language}">\n'
            "    <head>\n"
            "        <title>Table of contents</title>\n"
        )
        if self.document.stylesheet is not None:
            h += (
                f'        <link rel="stylesheet" href="{self.document.stylesheet}" '
                'type="text/css" />\n'
            )
        h += (
            "    </head>\n"
            "    <body>\n"
            '        <nav ops:type="toc">\n'
            "            <h1>Table of contents</h1>\n"
            "            <ol>\n"
            '                <li><a href="nav.xhtml">Table of contents</a></li>\n'
        )

        for i in range(len(self.document.chapters)):
            chapter = self.document.chapters[i]
            h += '                <li><a href="%03i.xhtml">%s</a></li>' % (
                i + 1,
                chapter.title,
            )

        # footer

        h += "            </ol>\n        </nav>\n     </body>\n</html>\n"

        return h


class TocNCX(EpubFile):
    def __init__(self, document: Document) -> None:
        self.document = document
        self.path = "OEBPS"
        self.name = "toc.ncx"

    def get_contents(self) -> str:
        # header
        assert self.document.metadata is not None
        h = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            f'<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="{self.document.metadata.language}">\n'
            "  <head>\n"
        )
        if self.document.metadata.uuid is not None:
            h += f'    <meta content="{self.document.metadata.uuid}" name="dtb:uid"/>\n'

        # FIXME
        h += '    <meta content="1" name="dtb:depth"/>\n'
        h += '    <meta content="0" name="dtb:totalPageCount"/>\n'
        h += '    <meta content="0" name="dtb:maxPageNumber"/>\n'
        h += "  </head>\n"

        if self.document.metadata.title is not None:
            h += f"  <docTitle>\n    <text>{self.document.metadata.title}</text>\n  </docTitle>\n"
        if self.document.metadata.title is not None:
            h += f"  <docAuthor>\n    <text>{self.document.metadata.author}</text>\n  </docAuthor>\n"

        # nav map

        h += "  <navMap>\n"
        for i in range(len(self.document.chapters)):
            chapter = self.document.chapters[i]
            h += f'    <navPoint class="chapter" id="navpoint-{i + 1}" playOrder="{i}">\n'
            h += f"        <navLabel>\n            <text>{chapter.title}</text>\n"
            h += "        </navLabel>\n"
            h += f'        <content src="{i + 1:03i}.xhtml"/>\n'
            h += "    </navPoint>\n"
        h += "  </navMap>\n"

        # footer

        h += "</ncx>\n"

        return h


class EpubMimeType(EpubFile):
    def __init__(self) -> None:
        self.path = None
        self.name = "mimetype"

    def get_contents(self) -> str:
        return "application/epub+zip"


class IBooksDisplayOptions(EpubFile):
    def __init__(self) -> None:
        self.path = "META-INF"
        self.name = "com.apple.ibooks.display-options.xml"

    def get_contents(self) -> str:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n<display_options>\n'
            '<platform name="*">\n<option name="specified-fonts">true</option>\n'
            "</platform>\n</display_options>\n"
        )
