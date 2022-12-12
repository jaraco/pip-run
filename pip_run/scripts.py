import sys
import ast
import tokenize
import json
import pathlib
import abc
import contextlib
import itertools
import re

import packaging.requirements
import jaraco.text
from jaraco.context import suppress


class Dependencies(list):
    index_url = None

    def params(self):
        prefix = ['--index-url', self.index_url] if self.index_url else []
        return prefix + self

    @classmethod
    def load(cls, items):
        """
        Construct self from items, validated as requirements.
        """
        reqs = map(packaging.requirements.Requirement, items)
        strings = map(str, reqs)
        return cls(strings)


class DepsReader:
    """
    Given a Python script, read the dependencies it declares.
    Does not execute the script, so expects __requires__ to be
    assigned a static list of strings.
    """

    def __init__(self, script):
        self.script = script

    @classmethod
    def try_read(cls, script_path: pathlib.Path):
        results = (subclass._try_read(script_path) for subclass in cls.__subclasses__())
        return next(filter(None, results), Dependencies())

    @classmethod
    @suppress(Exception)
    def _try_read(cls, script_path: pathlib.Path):
        """
        Attempt to load the dependencies from the script,
        but return None if unsuccessful.
        """
        reader = cls.load(script_path)
        return reader.read()

    @classmethod
    @abc.abstractmethod
    def load(cls, script: pathlib.Path):
        """
        Construct a DepsReader from the script path.
        """

    @classmethod
    def search(cls, params):
        """
        Given a (possibly-empty) series of parameters to a
        Python interpreter, return any dependencies discovered
        in a script indicated in the parameters. Only honor the
        first file found.
        """
        files = filter(pathlib.Path.is_file, map(pathlib.Path, params))
        return cls.try_read(next(files, None)).params()

    def read(self):
        return self.read_comments() or self.read_python()

    def read_comments(self):
        r"""
        >>> DepsReader("# Requirements:\n# foo\n\n# baz").read()
        ['foo']
        >>> DepsReader("# foo\n# bar").read_comments()
        []
        >>> DepsReader("# Requirements:\n# foo\n# bar").read()
        ['foo', 'bar']
        """
        match = re.search(
            r'^# Requirements:\n(.*)',
            self.script,
            flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )

        try:
            lines = match.group(1).splitlines()
        except AttributeError:
            lines = []

        comment = re.compile(r'#\s+(.*)')
        matches = itertools.takewhile(bool, map(comment.match, lines))
        return Dependencies.load(match.group(1) for match in matches)

    def read_python(self):
        r"""
        >>> DepsReader("__requires__=['foo']").read()
        ['foo']
        >>> DepsReader(r"__requires__='foo\nbar\n#baz'").read()
        ['foo', 'bar']
        """
        raw_reqs = self._read('__requires__')
        reqs_items = jaraco.text.yield_lines(raw_reqs)
        deps = Dependencies.load(reqs_items)
        with contextlib.suppress(Exception):
            deps.index_url = self._read('__index_url__')
        return deps

    def _read(self, var_name):
        mod = ast.parse(self.script)
        (node,) = (
            node
            for node in mod.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == var_name
        )
        return ast.literal_eval(node.value)


class SourceDepsReader(DepsReader):
    @classmethod
    def load(cls, script: pathlib.Path):
        return cls(script.read_text())


class NotebookDepsReader(DepsReader):
    @classmethod
    def load(cls, script: pathlib.Path):
        with script.open() as stream:
            doc = json.load(stream)
        lines = (
            line
            for cell in doc['cells']
            for line in cell['source'] + ['\n']
            if cell['cell_type'] == 'code' and not line.startswith('%')
        )
        return cls(''.join(lines))


def run(cmdline):
    """
    Execute the script as if it had been invoked naturally.
    """
    namespace = dict()
    filename = cmdline[0]
    namespace['__file__'] = filename
    namespace['__name__'] = '__main__'
    sys.argv[:] = cmdline

    open_ = getattr(tokenize, 'open', open)
    script = open_(filename).read()
    norm_script = script.replace('\\r\\n', '\\n')
    code = compile(norm_script, filename, 'exec')
    exec(code, namespace)
