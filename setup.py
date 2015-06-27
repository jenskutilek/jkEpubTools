#! /usr/bin/env python

from distutils.core import setup

setup(
		name = "jkEpubTools",
		version = "0.1",
		description = "Support libraries for epub generation.",
		author = "Jens Kutilek",
		url = "https://github.com/jenskutilek/jkEpubTools",
		license = "MIT",
		platforms = ["Mac"],
		packages = ["jkEpubTools"],
		package_dir = {"": "Lib"},
	)
