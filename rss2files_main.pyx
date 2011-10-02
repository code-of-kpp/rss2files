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

from domains import domains
from download import download

def rss2files(url, DomainClass, skip, existing=None):
	result = {}
	feed = feedparser.parse(url)

	result['url'] = url
	result['modified'] = feed.headers.get('last-modified')
	result['etag'] = feed.headers.get('etag')
	result['files'] = {}
	if existing:
		if result['etag'] or result['modified']:
			if result['etag'] == existing['etag'] and \
				result['modified'] == existing['modified']:
					return existing
		for key,f in existing['files'].iteritems():
			result['files'][key] = f
			result['files'][key]['in feed'] = False

	result['name'] = unicode(DomainClass.title(feed))
	result['description'] = unicode(DomainClass.description(feed))

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
			info = download(f['link'],
							path=result['name'],
							FileSize=f['size'],
							FileName=name,
							skip=skip)
			if info:
				(name, f['size']) = info
				result['files'][name] = f
		except xml.dom.DOMException:
			pass
	return result

def html_file_list(l, index_folder='.', files_prefix='./'):
	index_filename = ''.join([index_folder, os.path.sep,
								l['name'], os.path.sep, "index.html"])
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
				'\t\t<a href="', files_prefix, name, '">',
				name, '</a>\n',
				'\t\t<div>', f['info'], '</div>\n',
				'\t</td></tr>\n']))
			htmlf.write('</table></body></html>')

def html_projects_list(projects, index_folder='.'):
	index_filename = ''.join([index_folder, os.path.sep, "index.html"])
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
			'\t\t<a href="', p['name'], '/">', p['name'], '</a>\n',
			'\t\t<div>', p['description'], '</div>\n',
			'\t</td></tr>\n']))
		htmlf.write('</table></body></html>')

def handle_url(url):
	url = url.strip()
	if url.startswith('!'):
		params = url.split()
		for domain in domains:
			url = domain.form_url(params)
			if url: return url
	return url

def get_urls(file_name):
	with open(file_name) as f:
		return tuple(imap(handle_url, f))

def parse_args():
	parser = argparse.ArgumentParser(description='Download files from feeds')
	parser.add_argument('urls', type=get_urls, metavar='urls.list',
		nargs='?',
		#default='rss2files.list',
		help='File with list of urls')
	parser.add_argument('--timeout', type=int, metavar='seconds',
		default=60,
		help="Timeout for i/o operations (default: 60)")
	parser.add_argument('--exclude', type=str,
		nargs='*',
		help="GLOB to exclude files")
	parser.add_argument('--exclude-file', type=file, metavar='exclude.txt',
		help="file with GLOBs (one per line) to exclude files")
	parser.add_argument('--downloads-file', type=str, metavar='downloades.yaml',
		help='YAML file to keep information about downloads')
	return parser.parse_args()

def main():
	parsed_args = parse_args()
	#print parsed_args

	# `default` in argparse not working right in jython
	if parsed_args.urls is None:
		try:
			parsed_args.urls = get_urls('rss2files.list')
		except IOError:
			sys.stderr.write("Can't load urls list\n")
			return -1;

	socket.setdefaulttimeout(parsed_args.timeout)

	exclude = parsed_args.exclude
	if exclude is None: exclude = []
	if parsed_args.exclude_file:
		exclude.extend(imap(str.strip, parsed_args.exclude_file))

	skip = lambda s: any(imap(fnmatch, repeat(s), exclude))
	
	projects = dict()
	if not parsed_args.downloads_file:
		parsed_args.downloads_file = 'downloaded.yaml'

	if os.path.exists(parsed_args.downloads_file):
		with codecs.open(parsed_args.downloads_file, 'r', 'utf8') as f:
			projects = yaml.safe_load(f)

	for url in parsed_args.urls:
		urlh = hashlib.md5(url).hexdigest()
		netloc = urlparse.urlsplit(url).netloc
		for domain in domains:
			if domain.is_my_netloc(netloc):
				projects[urlh] = rss2files(url, domain, skip,
					existing=projects.get(urlh))
				break
		html_file_list(projects[urlh])
	html_projects_list(projects.itervalues())

	with open(parsed_args.downloads_file, 'wb') as f:
		yaml.safe_dump(projects, f,
			default_flow_style=False,
			allow_unicode=True)
		
	return 0

if __name__ == '__main__':
	sys.exit( main() )
