# Saving files from feeds

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

This is a simple text file containing one RSS/ATOM URL per line.
For example:

	http://example.com/some/poscast.rss
	https://example.com/feed/with/links/in/titles/atom
	http://code.google.com/feeds/p/nltk/downloads/basic
	http://sourceforge.net/api/file/index/project-name/sevenzip/mtime/desc/limit/20/rss

#### Shortcuts in URLs lists
There is a few shortcuts that could be used in URLs lists.
Shortcut format:
	!<site-id> <project-name> [<params>]

Examples
	!code.google.com django-jython
	!sf.net pywin32 5

Last line tells rss2files to ask sf.net for last five files posted to 
pywin32 project.

### Excluding unneeded files
There are two ways to exclude unwanted files from download list
First is passing --exclude argument to rss2files:
	rss2files http://mysite/my_feed --exclude *.rpm *.deb
Last line will force rss2files to ignore iny files matching `*.rpm` or
`*.deb` globs.

Second is based on using exclude-list file. This is simple text file
with one glob per line. This file can be passed to rss2files with 
`--exclude-file option`
	rss2files https://some.local/link --exclude file avoid_this_files:
avoid_this_files:
	*.exe
	*.dll
	*.sys
	*.scr

## Listing of downloaded files to html
HTML files containing links to every downloaded file will be created for
every URL in URLs list as well as main index.html file for all
projects/podcasts mirrored.
