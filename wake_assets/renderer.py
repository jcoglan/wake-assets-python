import cgi
import mimetypes
import re

class Renderer:
    CSS = 'css'
    JS  = 'javascript'
    IMG = 'binary'

    def __init__(self, assets, **options):
        self._assets = assets
        self._builds = options.get('builds', {})
        self._hosts  = options.get('hosts', [])
        self._inline = options.get('inline', False)

    def include_css(self, *names, **options):
        if options.get('inline', self._inline):
            tags = map(lambda path: self._tag('style', options, type='text/css') + self._assets.read_file(path) + '</style>',
                       self.paths_for(self.CSS, *names, **options))
        else:
            tags = map(lambda url: self._tag('link', options, rel='stylesheet', type='text/css', href=url),
                       self.urls_for(self.CSS, *names, **options))

        return ''.join(tags)

    def include_image(self, *names, **options):
        if options.get('inline', self._inline):
            tags = map(lambda path: self._tag('img', options, src=self._base64_file(path)),
                       self.paths_for(self.IMG, *names, **options))
        else:
            tags = map(lambda url: self._tag('img', options, src=url),
                       self.urls_for(self.IMG, *names, **options))

        return ''.join(tags)
    
    def include_js(self, *names, **options):
        if options.get('inline', self._inline):
            tags = map(lambda path: self._tag('script', options, type='text/javascript') + self._assets.read_file(path) + '</script>',
                       self.paths_for(self.JS, *names, **options))
        else:
            tags = map(lambda url: self._tag('script', options, type='text/javascript', src=url) + '</script>',
                       self.urls_for(self.JS, *names, **options))

        return ''.join(tags)

    def paths_for(self, type, *names, **options):
        options = dict({'build': self._builds.get(type, None)}.items() + options.items())
        return self._assets.paths_for(type, *names, **options)

    def urls_for(self, type, *names, **options):
        paths = map(self._assets.relative, self.paths_for(type, *names, **options))
        hosts = self._hosts

        if not hosts: return paths

        return map(lambda path: re.sub(r'/*$', '', hosts[path.__hash__() % len(hosts)]) + path,
                   paths)

    def _base64_file(self, path):
        base64 = self._assets.read_file(path).encode('base64').replace('\n', '')
        mime   = mimetypes.guess_type(path)[0]
        return 'data:%s;base64,%s' % (mime, base64)

    def _tag(self, name, options, **attrs):
        attrs = dict(attrs.items() + options.get('html', {}).items())
        list  = []

        for key in attrs:
            list.append('%s="%s"' % (key, cgi.escape(attrs[key])))

        tag = '<' + name
        if list: tag += ' ' + ' '.join(list)
        return tag + '>'

