class UsualDomain:
	@staticmethod
	def is_my_netloc(netloc):
		return True

	@staticmethod
	def form_url(params):
		return None

	@staticmethod
	def title(feed):
		'''Returns podcast/project name'''
		return feed.feed.title

	@staticmethod
	def description(feed):
		'''Return description of podcast/project'''
		return feed.feed.subtitle.strip()
	
	@staticmethod
	def file_link(entry):
		'''Returns link to the file'''
		try:
			enclosure = entry.enclosures[0]
			return enclosure.href
		except (KeyError, AttributeError, IndexError):
			return entry.link

	@staticmethod
	def file_description(entry):
		'''Returns some details about the file'''
		return entry.title.strip()

	@staticmethod
	def file_name(entry):
		'''Returns name for local file'''
		raise NotImplementedError()

	@staticmethod
	def file_size(entry):
		'''Return expected file size. None means there is no
		such information'''
		try:
			enclosure = entry.enclosures[0]
			return int(enclosure.length)
		except (KeyError, AttributeError, IndexError):
			return None
