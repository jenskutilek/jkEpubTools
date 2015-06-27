#!/usr/bin/env python

from hashlib import sha1
from operator import xor
from os.path import join, exists
from string import strip
from re import compile, search, IGNORECASE


def get_data_from_xml(xml_path, regex, one=True):
    c_regex = compile(regex, IGNORECASE)
    xml = open(xml_path, "rb")
    
    matches = []
    for line in xml:
        match = c_regex.search(line)
        if match is not None:
            try:
                matches.append(match.group(2))
            except:
                print "  WARNING: Could not extract data from \"%s\"." % xml_path
                print "    Line was:  %s" % line
                print "    Regex was: %s" % regex
            if one:
                break
    xml.close()
    return matches


def get_files_to_obfuscate(source_path):
    # Find and return the full paths of all files that should be encrypted
    file_path = join(source_path, "META-INF", "encryption.xml")
    if not exists(file_path):
        # no hands, no cookies
        return []
    
    return get_data_from_xml(
        file_path,
        '(<enc:CipherReference.*uri ?= ?[\"\'])(.*)([\"\'])',
        False,
    )


def get_obfuscation_key(source_path):
    print "Building obfuscation key ..."
    print "  Looking for .opf paths in \"%s\" ..." % join(source_path, "META-INF", "container.xml")
    opf_paths = get_data_from_xml(
        join(source_path, "META-INF", "container.xml"),
        '<rootfile.*full-path ?= ?([\"\'])(.*?)([\"\'])',
        False,
    )
    if opf_paths == []:
        print "  ERROR: Paths to content.opf could not be extracted from container.xml."
        return None
    
    uid_id_regex = compile('(unique-identifier ?= ?[\"\'])(.*?)([\"\'])', IGNORECASE)
    
    uids = []
    
    for opf_path in opf_paths:
        print "  Looking for unique identifier name in \"%s\" ..." % opf_path
        uid_ids = get_data_from_xml(
            join(source_path, opf_path),
            '(unique-identifier ?= ?[\"\'])(.*?)([\"\'])',
        )
        
        if uid_ids == []:
            print "  ERROR: Unique identifier name could not be extracted from %s." % opf_path
        
        uid_id = uid_ids[0]
        print "  Looking for unique identifier width name \"%s\" ..." % uid_id
        
        uids = get_data_from_xml(
            join(source_path, opf_path),
            '(<dc:identifier.*id ?= ?[\"\']%s[\"\'].*>)(.*)(</dc:identifier>)' % uid_id,
        )
    
    if uids == []:
        print "  ERROR: No unique identifiers could be extracted."
        return None
    
    print "  Found uids: %s" % uids
    
    key = u""
    for uid in uids:
        # TODO: strip all possible whitespace: 
        # http://www.idpf.org/epub/30/spec/epub30-ocf.html#fobfus-keygen
        #   Specifically the Unicode code points U+0020, U+0009, U+000D and U+000A
        #   must be stripped from each identifier before it is added to the
        #   concatenated space-delimited string.
        key += "%s " % strip(uid)
    
    #   An SHA-1 digest of the UTF-8 representation of this string should be
    #   generated as specified by the Secure Hash Standard [SHA-1].
    key = sha1(strip(key).encode("utf-8"))
    #print "Key size:", key.digest_size
    print "... done."
    return bytearray(key.digest())


def xor_array(array, key):
    for i in range(min(len(array), 1040)):
        j = i % len(key)
        #print u"XOR pos: %i, key: %i" % (i, j)
        #print u"  %s xor\n  %s =\n  %s" % (bin(array[i]), bin(key[j]), bin(array[i] ^ key[j]))
        array[i] = array[i] ^ key[j]
    return array
