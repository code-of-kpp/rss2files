import socket
import urllib2

from usualdomain import UsualDomain

class GoogleCode(UsualDomain):
	@staticmethod
	def is_my_netloc(netloc):
		return netloc == "code.google.com"

	@staticmethod
	def form_url(params):
		known = frozenset(('!googlecode', '!code.google.com'))
		if params[0].lower() not in known:
			return None
		if len(params) < 2:
			return None
		return ''.join(['http://code.google.com/feeds/p/',
			params[1], 
			'/downloads/basic',
		])

	@staticmethod
	def title(feed):
		name = feed.feed.title
		name = name.split('Downloads for project ')[1]
		name = name.split(' on ')[0]
		return name

	@staticmethod
	def description(feed):
		try:
			url = feed.feed.link.replace('downloads/basic', '')
			url = url.replace('feeds/', '')
			r = urllib2.urlopen(url)
			s = r.read()
			r.close()
			s = s.split('title>')[1].replace('</','')
			s = s.split(' - Google')[0].replace('Downloads -', '')
			s = s.replace('\n', '')
			return s.strip()
		except socket.error:
			return feed.feed.title.strip()

	@staticmethod
	def file_link(entry):
		link = entry['content'][0]['value']
		link = link.split('href="')[-1]
		link = link.split('">')[0]
		return link

	@staticmethod
	def file_description(entry):
		res = entry['content'][0]['value']
		res = res.split('<a')[:-1]
		res = ''.join(res)
		res = res.replace('<pre>', '')
		return res.strip()

	@staticmethod
	def file_size(entry):
		return None
