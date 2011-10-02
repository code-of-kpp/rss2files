from usualdomain import UsualDomain

class SourceForge(UsualDomain):
	@staticmethod
	def is_my_netloc(netloc):
		locs = frozenset(('sf.net', 'sourceforge.net'))
		return netloc in locs

	@staticmethod
	def form_url(params):
		return None

	@staticmethod
	def title(feed):
		name = feed.feed.title
		name = name.split(' downloads')[0]
		return name.strip()

	@staticmethod
	def file_name(entry):
		return entry.title[1:]

	@staticmethod
	def file_size(entry):
		return None

	@staticmethod
	def file_link(entry):
		return entry.link
