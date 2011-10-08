#!/usr/bin/env python

from __future__ import with_statement

from itertools import *

import socket
import urllib2
import urlparse
import feedparser

import sys
import os.path
from fnmatch import fnmatch

import xml.dom
import hashlib
import argparse

import codecs

import yaml

def construct_yaml_str(self, node):
	"""Override the default string handling function 
	to always return unicode objects"""
	return self.construct_scalar(node)
yaml.Loader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)
yaml.SafeLoader.add_constructor(u'tag:yaml.org,2002:str', construct_yaml_str)

from rss2files.domains import domains
from rss2files.download import download

def appdata_path():
	APPNAME = 'rss2files'
	appdata = os.path.join('~', '.' + APPNAME)
	if sys.platform == 'darwin':
		from AppKit import NSSearchPathForDirectoriesInDomains
		# NSApplicationSupportDirectory = 14
		# NSUserDomainMask = 1
		# True for expanding the tilde into a fully qualified path
		appdata = os.path.join(
			NSSearchPathForDirectoriesInDomains(14, 1, True)[0],
			APPNAME)
	elif sys.platform == 'win32':
		appdata = os.path.join(environ['APPDATA'], APPNAME)
	else:
		appdata = os.path.expanduser(
			os.path.join("~", ".local", 'share', APPNAME))
	return appdata

def make_right_dirs(root, name):
	try:
		name = os.path.join(root, name)
		if os.path.exists(name):
			if os.path.isdir(name):
				return name
			else:
				name = ''.join([name, os.path.sep, 'feed'])
		os.makedirs(name)
		return name
	except IOError:
		name = hashlib.md5(name).hexdigest()
		os.makedirs(name)
		return name

def rss2files(url, DomainClass, skip, root, existing=None):
	result = {}
	feed = feedparser.parse(url)

	result['url'] = url
	result['modified'] = feed.headers.get('last-modified')
	result['etag'] = feed.headers.get('etag')
	result['files'] = {}
	result['path'] = None
	if existing:
		if result['etag'] or result['modified']:
			if result['etag'] == existing['etag'] and \
				result['modified'] == existing['modified']:
					return existing
		for key,f in existing['files'].iteritems():
			result['files'][key] = f
			result['files'][key]['in feed'] = False
		result['path'] = existing.get('path')

	result['name'] = unicode(DomainClass.title(feed))
	result['description'] = unicode(DomainClass.description(feed))

	if not result.get('path'):
		result['path'] = make_right_dirs(root, result['name'])

	for entry in feed.entries:
		try:
			f = {}
			f['link'] = DomainClass.file_link(entry)
			f['info'] = unicode(DomainClass.file_description(entry))
			f['size'] = DomainClass.file_size(entry)
			f['in feed'] = True
			name = None
			try:
				name = DomainClass.file_name(entry)
			except NotImplementedError:
				pass
			if existing and name in existing:
				if not f['size']:
					f['size'] = existing[name].get('size')
			info = download(f['link'],
							path=result['path'],
							FileSize=f['size'],
							FileName=name,
							skip=skip)
			if info:
				(name, f['size']) = info
				result['files'][name] = f
		except xml.dom.DOMException:
			pass
	return result

def html_file_list(l, files_path, index_folder='.', files_prefix='./'):
	index_filepath = os.path.join(index_folder, l['path'].lstrip(files_path))
	project_path = '/'.join((files_prefix, l['path'].lstrip(files_path)))
	if not os.path.exists(index_filepath):
		os.makedirs(index_filepath)
	index_filename = os.path.join(index_filepath, 'index.html')
	with codecs.open(index_filename,  'w', 'utf8') as htmlf:
			htmlf.write(''.join([
			'<html>\n',
			'<head><meta http-equiv="content-type"\n',
			'content="text/html;charset=utf-8" /></head>\n',
			'<body>\n',
			'<h1 id="title">', l['name'], '</h1>\n',
			'<div id="description">', l['description'], '</div>\n',
			'<table id="FileList">\n']))
			for name,f in l['files'].iteritems():
				if name is None:
					continue
				htmlf.write(''.join([
				'\t<tr><td>\n',
				'\t\t<a href="', 
					'/'.join((project_path,) + os.path.split(name)), '">',
				name, '</a>\n',
				'\t\t<div>', f['info'], '</div>\n',
				'\t</td></tr>\n']))
			htmlf.write('</table></body></html>')

def html_projects_list(projects, files_path, index_folder='.', files_prefix='.'):
	index_filename = os.path.join(index_folder, "index.html")
	with codecs.open(index_filename, 'w', 'utf8') as htmlf:
		htmlf.write(''.join([
		'<html>\n',
		'<head><meta http-equiv="content-type"\n',
		'content="text/html;charset=utf-8" /></head>\n',
		'<body>\n',
		'<h1 id="title">', 'Mirrored projects', '</h1>\n',
		'<table id="ProjectsList">\n']))
		for p in projects:
			if p['name'] is None:
				continue
			htmlf.write(''.join([
			'\t<tr><td>\n',
			'\t\t<a href="', files_prefix,
					'/'.join(os.path.split(p['path'].lstrip(files_path))),
				'/">', p['name'], '</a>\n',
			'\t\t<div>', p['description'], '</div>\n',
			'\t</td></tr>\n']))
		htmlf.write('</table></body></html>')

def handle_url(url):
	url = url.strip()
	if url.startswith('#'):
		return None
	if url.startswith('!'):
		params = url.split()
		for domain in domains:
			url = domain.form_url(params)
			if url: return url
		return None
	if url.isspace():
		return None

def get_urls(parsed_args):
	file_name = None
	if parsed_args.urls is None:
		file_name = os.path.join(parsed_args.appdir, 'rss2files.list')
	else:
		file_name = parsed_args.urls

	with open(file_name) as f:
		return tuple(ifilter(None, imap(handle_url, f)))

def parse_args():
	parser = argparse.ArgumentParser(
		description='Save files mentioned in feeds')
	parser.add_argument('urls', type=str, metavar='FILE',
		nargs='?',
		#default='rss2files.list',
		help='file with list of urls (default: rss2files.list in appdir)')
	parser.add_argument('-D', '--rootdir', type=str, metavar='PATH',
		default='.',
		help='where to store downloaded files (default: current dir)')
	parser.add_argument('-H', '--htmldir', type=str, metavar='PATH',
		default='.',
		help="where to store html files (default: current dir)")
	parser.add_argument('-p', '--htmlprefix', type=str, metavar='prefix',
		default='./',
		help='prefix for links in html files (default: "./")')
	parser.add_argument('-A', '--appdir', type=str, metavar='PATH',
		default=appdata_path(),
		help="where to store internal files (default: %s)"%appdata_path() )
	parser.add_argument('-t', '--timeout', type=int, metavar='SECONDS',
		default=60,
		help="timeout for i/o operations (default: 60)")
	parser.add_argument('-E', '--exclude', type=str, metavar='MASK',
		nargs='*',
		help="GLOB mask to exclude files")
	parser.add_argument('-e', '--exclude-file', type=file, metavar='FILE',
		help="file with GLOBs (one per line) to exclude files")
	parser.add_argument('-d', '--downloads-file', type=str, metavar='FILE',
		help='YAML file to keep information about downloads' \
		' (default: downloads.yaml in appdir)' )
	namespace = parser.parse_args()
	namespace.rootdir = os.path.abspath(namespace.rootdir)
	return namespace

def main():
	parsed_args = parse_args()

	# `default` in argparse not working right in jython
	try:
		parsed_args.urls = get_urls(parsed_args)
	except IOError:
		sys.stderr.write("Can't load urls list\n")
		return -1;

	socket.setdefaulttimeout(parsed_args.timeout)

	exclude = parsed_args.exclude
	if exclude is None: exclude = []
	try:
		if parsed_args.exclude_file:
			exclude.extend(imap(str.strip, parsed_args.exclude_file))
	except IOError:
		sys.stderr.write("Can't load GLOBs from exclude file")
		return -1

	skip = lambda s: any(imap(fnmatch, repeat(s), exclude))
	
	projects = dict()
	if not parsed_args.downloads_file:
		downloads_file = os.path.join(parsed_args.appdir, 'downloaded.yaml')
		parsed_args.downloads_file = downloads_file

	if os.path.exists(parsed_args.downloads_file):
		with codecs.open(parsed_args.downloads_file, 'r', 'utf8') as f:
			projects = yaml.safe_load(f)

	for url in parsed_args.urls:
		urlh = hashlib.md5(url).hexdigest()
		netloc = urlparse.urlsplit(url).netloc
		for domain in domains:
			if domain.is_my_netloc(netloc):
				projects[urlh] = rss2files(url, domain, skip,
					root=parsed_args.rootdir,
					existing=projects.get(urlh))
				break
		html_file_list(projects[urlh],
			parsed_args.rootdir,
			index_folder=parsed_args.htmldir,
			files_prefix=parsed_args.htmlprefix)
	html_projects_list(projects.itervalues(),
		parsed_args.rootdir,
		index_folder=parsed_args.htmldir)

	with open(parsed_args.downloads_file, 'wb') as f:
		yaml.safe_dump(projects, f,
			default_flow_style=False,
			allow_unicode=True)

	return 0

if __name__ == '__main__':
	sys.exit( main() )
