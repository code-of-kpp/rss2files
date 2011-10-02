# Saving files from a feeds

The main goal of rss2files is to help you in downloading latest
versions of files (binaries) stored on code.google.com and sf.net.
Should be helpfull in creating off-line file mirrors for specific set
of projects.

It also can download files from podcasts (one file per entry)
assuming links are stored in enclosures or in titles of feed entries.

It is based on FeedParser python library which supports almost all
existing feed formats.

rss2files should work with python2.x (2.5 or higher).

##  Basic usage

	rss2files urls_list_file.list

### URLs list file

This is a simple text file containing one RSS/ATOM url per line.
For example:

		http://example.com/some/poscast.rss
		https://example.com/feed/with/links/in/titles/atom
		http://code.google.com/feeds/p/nltk/downloads/basic
		http://sourceforge.net/api/file/index/project-name/sevenzip/mtime/desc/limit/20/rss


