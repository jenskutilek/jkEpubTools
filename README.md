jkEpubTools
===========

`jkEpubTools` is a Python module which builds an epub file structure from prepared input files and compiles the final compressed epub file.

Features
--------

* epub 2.0 and 3.0 standards
* Font obfuscation (epub 3.0)
* iBooks display options
* Generation of an XHTML cover page from a supplied image file

What it doesn’t do

* Build content XHTML files. You have to supply the content files in XHTML which jkEpubTools will pack into the correct file structure.
* Format your content. You must supply a CSS file or build the styles into your content XHTML files.
* DRM

There is a demo project in the `examples` folder which you can build on your computer if you have Python 2.7 installed. Just run the included `compile.py` script.


Installation
------------

```bash
$ python setup.py build
$ sudo python setup.py install
```