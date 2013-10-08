import json
import os
import os.path
import subprocess

from .renderer import Renderer


class InvalidReference(StandardError):
    pass


class Assets:
    DEFAULT_BUILD = 'min'
    DEFAULT_CACHE = True
    DEFAULT_MODE  = 'targets'
    DEFAULT_WAKE  = os.path.join('.', 'node_modules', '.bin', 'wake')
    CACHE_FILE    = '.wake.json'
    MANIFEST      = '.manifest.json'
    PACKAGE_FILE  = 'package.json'
    WAKE_FILE     = 'wake.json'

    def __init__(self, **options):
        self._pwd   = os.path.abspath(options.get('pwd', os.getcwd()))
        self._cache = options.get('cache', self.DEFAULT_CACHE)
        self._wake  = options.get('wake', os.path.join(self._pwd, self.DEFAULT_WAKE))
        self._root  = os.path.abspath(options.get('root', self._pwd))
        self._mode  = options.get('mode', self.DEFAULT_MODE)

        self.clear_cache()

    def clear_cache(self):
        subprocess.call([self._wake, '--cache'])

        self._config   = None
        self._index    = None
        self._manifest = {}
        self._paths    = {}

    def paths_for(self, group, *names, **options):
        config = self._read_config()

        build = options.get('build', self.DEFAULT_BUILD)
        if not build in config[group].get('builds', {}):
            build = self.DEFAULT_BUILD

        paths = map(lambda name: self._read_paths(group, name, build), names)
        return reduce(lambda a, b: a + b, paths, [])

    def read_file(self, path):
        with open(path) as file_handle:
            return file_handle.read()

    def relative(self, path):
        return '/' + os.path.relpath(path, self._root)

    def renderer(self, **options):
        if not self._cache: self.clear_cache()
        return Renderer(self, **options)

    def _find_paths_for(self, key):
        group, name, build = key
        try:
            index = self._read_index()[group][name]
            if self._mode == 'sources':
                absolute_paths = index['sources']
            else:
                absolute_paths = [index['targets'][build]]
        except KeyError:
            raise InvalidReference('Could not find assets: group: %r, name: %r, build: %r' % (group, name, build))

        def resolve(path):
            basename = os.path.basename(path)
            dirname  = os.path.dirname(path)
            manifest = os.path.join(dirname, self.MANIFEST)
            return os.path.join(dirname, self._read_manifest(manifest).get(basename, basename))

        return map(resolve, absolute_paths)

    def _read_config(self):
        if self._config: return self._config

        wake    = os.path.join(self._pwd, self.WAKE_FILE)
        package = os.path.join(self._pwd, self.PACKAGE_FILE)

        if os.path.exists(wake):
            config = json.loads(self.read_file(wake))
        elif os.path.exists(package):
            config = json.loads(self.read_file(package))['wake']
        else:
            config = {}

        if self._cache: self._config = config
        return config

    def _read_index(self):
        if self._index: return self._index
        path = os.path.join(self._pwd, self.CACHE_FILE)
        index = json.loads(self.read_file(path))
        if self._cache: self._index = index
        return index

    def _read_manifest(self, path):
        if path in self._manifest: return self._manifest[path]
        mapping = json.loads(self.read_file(path)) if os.path.exists(path) else {}
        if self._cache: self._manifest[path] = mapping
        return mapping

    def _read_paths(self, group, name, build):
        key = (group, name, build)
        if key in self._paths: return self._paths[key]
        paths = self._find_paths_for(key)
        if self._cache: self._paths[key] = paths
        return paths

