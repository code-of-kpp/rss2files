#!/usr/bin/env python

try:
	import pyximport; pyximport.install()
	from rss2files_main import main
except ImportError:
	import imp
	import os.path
	path = os.path.split(__file__)[:-1] + ('rss2files_main.pyx',)
	path = os.path.join(*path)
	mod = imp.load_source('mod', path)
	main = mod.main

import sys

#_temp = __import__('rss2files_main.pyx', globals(), locals(), ['main'], -1)
#main = _temp.main

#from rss2files_main.pyx import main

if __name__ == '__main__':
	sys.exit( main() )
