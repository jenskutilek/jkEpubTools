#!/usr/bin/env python

import codecs
import zipfile

from os import walk
from os.path import join

from obfuscation import get_obfuscation_key, get_files_to_obfuscate, xor_array


def build(in_path, out_file):
    # build obfuscation key
    key = get_obfuscation_key(in_path)
    
    # read file names from encryption.xml
    print "Obfuscating requested files ..."
    obfuscated_files = {}
    for f in get_files_to_obfuscate(in_path):
        print "  Obfuscating \"%s\" ..." % f
        with open(join(in_path, f), "rb") as in_file:
            ba = bytearray(in_file.read())
        obfuscated_files[f] = xor_array(ba, key)
    #print "Obfuscated files:", obfuscated_files.keys()
    print "... done."
    
    print "Adding files to epub file \"%s\" ..." % out_file
    z = zipfile.ZipFile(out_file, "w")
    for root, dirs, files in walk(in_path):
        epub_root = root[len(in_path)+1:]
        for f in files:
            if not f.startswith("."):
                print "  Adding file: \"%s\"" % join(epub_root, f),
                if join(epub_root, f) in obfuscated_files:
                    print "with obfuscation"
                    z.writestr(join(epub_root, f), str(obfuscated_files[join(epub_root, f)]))
                else:
                    print "from disk"
                    z.write(join(root, f), join(epub_root, f))
    z.close()
    print "... done."

if __name__ == "__main__":
    build("build/epub", "RoboRef.epub")