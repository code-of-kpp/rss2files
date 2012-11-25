from usualdomain import UsualDomain


class SourceForge(UsualDomain):
    @staticmethod
    def is_my_netloc(netloc):
        locs = frozenset(('sf.net', 'sourceforge.net'))
        return netloc in locs

    @staticmethod
    def form_url(params):
        known = frozenset(('!sourceforge', '!sf.net',
                            '!sourceforge.net'))
        if params[0].lower() not in known:
            return None
        if len(params) < 2:
            return None
        url = ''.join(['http://sourceforge.net/api/file/index/',
            'project-name/', params[1], '/mtime/desc/'])
        if len(params) >= 3 and int(params[2]):
            url = ''.join([url, 'limit/', params[2], '/'])
        url = ''.join([url, 'rss'])

        return url

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
