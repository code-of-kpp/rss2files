from setuptools import setup, find_packages

setup(
	name = "rss2files",
	version = "0.1.1",
	packages = find_packages(),
	scripts = ('rss2files_main.py',),

	install_requires = (
		'FeedParser >= 5.0.0',
		'PyYAML >= 3.10',
		'argparse >= 1.2.1',
	),

	entry_points = {
		'console_scripts': [
			'rss2files = rss2files_main:main',
		]
	},

	package_data = {
		# If any package contains *.txt or *.rst files, include them:
		'': ['*.txt', '*.md'],
		# And include any *.msg files found in the 'hello' package, too:
		#'hello': ['*.msg'],
	},

	# metadata for upload to PyPI
	author = "Konstantin Podshumok",
	author_email = "kpp.live@gmail.com",
	description = "Saving files mentiod in feeds",
	license = "GPLv3",
	keywords = "rss atom files download googlecode sourcefourge",
	#url = "http://example.com/HelloWorld/",   # project home page, if any
	zip_safe = True,
	classifiers = (
		"Development Status :: 3 - Alpha",
		"Environment :: Console",
		"Intended Audience :: System Administrators",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 2.5",
		"Programming Language :: Python :: 2.6",
		"Programming Language :: Python :: 2.7",
		"Topic :: Internet",
		"Topic :: Utilities",
	),
	# could also include long_description, download_url, classifiers, etc.
)
