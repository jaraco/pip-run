import hashlib
import contextlib

import platformdirs

from .. import deps


paths = platformdirs.PlatformDirs(appname='pip run', appauthor=False)


class Hash:
    """
    Hash class with support for unicode text.
    """

    def __init__(self, name):
        self._hash = hashlib.new(name)

    def update(self, text):
        self._hash.update(text.encode('utf-8'))

    def hexdigest(self):
        return self._hash.hexdigest()


def cache_key(args):
    """
    Generate a cache key representing the packages to be installed.

    >>> reqs1, reqs2 = getfixture('reqs_files')
    >>> cache_key(['-r', str(reqs1), '--requirement', str(reqs2), 'requests'])
    '88d9f8a3a4009c1f685a7a724519bd5187e1227d72be6bc7f20a4a02f36d14b3'

    The key should be insensitive to order.

    >>> cache_key(['--requirement', str(reqs2), 'requests', '-r', str(reqs1)])
    '88d9f8a3a4009c1f685a7a724519bd5187e1227d72be6bc7f20a4a02f36d14b3'

    >>> cache_key(['--foo', '-q'])
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    """
    parsed = deps.Install.parse(args)
    hash = Hash('sha256')
    for req in sorted(parsed.package):
        hash.update(req + '\n')
    for file in sorted(parsed.requirement):
        hash.update('req:\n' + file.read_text(encoding='utf-8'))
    return hash.hexdigest()


@contextlib.contextmanager
def context(args):
    yield paths.user_cache_path.joinpath(cache_key(args))
