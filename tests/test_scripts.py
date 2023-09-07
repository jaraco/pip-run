import codecs
import textwrap
import sys
import subprocess

import pytest
import nbformat
import jaraco.path

from pip_run import scripts
from pip_run.commands import _has_shebang


def DALS(str):
    return textwrap.dedent(str).lstrip()


@pytest.mark.network
def test_pkg_imported(tmp_path):
    """
    Create a script that loads a package and ensure it runs.
    """
    jaraco.path.build(
        {
            'script': DALS(
                """
                import sample
                print("Import succeeded")
                """
            )
        },
        tmp_path,
    )
    script = tmp_path / 'script'
    pip_args = ['sampleproject']
    cmd = [sys.executable, '-m', 'pip-run'] + pip_args + ['--', str(script)]

    out = subprocess.check_output(cmd, text=True, encoding='utf-8')
    assert 'Import succeeded' in out


class TestSourceDepsReader:
    def test_reads_files_with_attribute_assignment(self):
        script = textwrap.dedent(
            '''
            __requires__=['foo']
            x.a = 'bar'
            '''
        )
        assert scripts.DepsReader(script).read() == ['foo']

    def test_reads_files_with_multiple_assignment(self):
        script = textwrap.dedent(
            '''
            __requires__=['foo']
            x, a = [a, x]
            '''
        )
        assert scripts.DepsReader(script).read() == ['foo']

    def test_single_dep(self):
        script = textwrap.dedent(
            '''
            __requires__='foo'
            '''
        )
        assert scripts.DepsReader(script).read() == ['foo']

    def test_index_url(self):
        script = textwrap.dedent(
            '''
            __requires__ = ['foo']
            __index_url__ = 'https://my.private.index/'
            '''
        )
        reqs = scripts.DepsReader(script).read()
        assert reqs.index_url == 'https://my.private.index/'

    def test_fstrings_allowed(self):
        """
        It should be possible to read dependencies from a script
        with f-strings on all Pythons.
        """
        script = DALS(
            '''
            # coding: future_fstrings
            __requires__ = 'foo'
            f'boo'
            f'coo'
            '''
        )
        reqs = scripts.DepsReader(script).read()
        assert reqs == ['foo']

    def test_comment_style(self):
        script = textwrap.dedent(
            """
            #! shebang

            # Requirements:
            # foo == 3.1
            """
        )
        reqs = scripts.DepsReader(script).read()
        assert reqs == ['foo==3.1']

    def test_search_long_parameter(self):
        """
        A parameter that is too long to be a filename should not fail.
        """
        exes = 'x' * 248
        command = f'print("{exes}")'
        params = ['-c', command]
        scripts.DepsReader.search(params)


class TestNotebookDepsReader:
    @pytest.fixture
    def notebook_factory(self, tmpdir, request):
        class Factory:
            def __init__(self):
                self.nb = nbformat.v4.new_notebook()
                self.path = tmpdir / (request.node.name + '.ipynb')

            @property
            def filename(self):
                return str(self.path)

            def write(self):
                nbformat.write(self.nb, self.filename)

            def add_code(self, code):
                self.nb['cells'].append(nbformat.v4.new_code_cell(code))

            def add_markdown(self, text):
                self.nb['cells'].append(nbformat.v4.new_markdown_cell(text))

        return Factory()

    def test_one_code_block(self, notebook_factory):
        notebook_factory.add_code('__requires__ = ["matplotlib"]')
        notebook_factory.write()
        reqs = scripts.DepsReader.try_read(notebook_factory.path)
        assert reqs == ['matplotlib']

    def test_multiple_code_blocks(self, notebook_factory):
        notebook_factory.add_code('__requires__ = ["matplotlib"]')
        notebook_factory.add_code("import matplotlib")
        notebook_factory.write()
        reqs = scripts.DepsReader.try_read(notebook_factory.path)
        assert reqs == ['matplotlib']

    def test_code_and_markdown(self, notebook_factory):
        notebook_factory.add_code('__requires__ = ["matplotlib"]')
        notebook_factory.add_markdown("Mark this down please")
        notebook_factory.write()
        reqs = scripts.DepsReader.try_read(notebook_factory.path)
        assert reqs == ['matplotlib']

    def test_jupyter_directives(self, notebook_factory):
        notebook_factory.add_code('__requires__ = ["matplotlib"]')
        notebook_factory.add_code("%matplotlib inline\nimport matplotlib")
        notebook_factory.write()
        reqs = scripts.DepsReader.try_read(notebook_factory.path)
        assert reqs == ['matplotlib']


@pytest.mark.network
def test_pkg_loaded_from_alternate_index(tmp_path):
    """
    Create a script that loads cython from an alternate index
    and ensure it runs.
    """
    jaraco.path.build(
        {
            'script': DALS(
                """
                __requires__ = ['sampleproject']
                __index_url__ = 'https://devpi.net/root/pypi/+simple/'
                import sample
                print("Import succeeded")
                """
            )
        },
        tmp_path,
    )
    cmd = [sys.executable, '-m', 'pip-run', '-v', '--', str(tmp_path / 'script')]

    out = subprocess.check_output(cmd, text=True, encoding='utf-8')
    assert 'Import succeeded' in out
    assert 'devpi.net' in out


def _minimal_flit(name):
    return {
        'pyproject.toml': DALS(
            f"""
            [project]
            name = "{name}"
            # flit requires a version
            version = "1"
            # flit requires a description
            description = ""

            [build-system]
            build-backend = "flit_core.buildapi"
            requires = ["flit_core"]
            """
        ),
        name: {
            # flit requires an init file
            '__init__.py': '',
        },
    }


def test_pkg_loaded_from_url(tmp_path):
    """
    Create a script whose dependency is only installable
    from a custom url and ensure it runs.
    """
    dependency = tmp_path / 'barbazquux-1.0'
    url_req = f'barbazquux @ file://{dependency.as_posix()}'
    jaraco.path.build(
        {
            'barbazquux-1.0': _minimal_flit('barbazquux'),
            'script_dir': {
                'script': DALS(
                    f"""
                    __requires__ = [{url_req!r}]
                    import barbazquux
                    print("Successfully imported barbazquux")
                    """
                ),
            },
        },
        tmp_path,
    )

    script = tmp_path.joinpath('script_dir', 'script')
    cmd = [
        sys.executable,
        '-m',
        'pip-run',
        '--no-index',
        '--no-build-isolation',
        '--',
        str(script),
    ]
    out = subprocess.check_output(cmd, text=True, encoding='utf-8')
    assert 'Successfully imported barbazquux' in out


@pytest.mark.parametrize(
    "shebang, expect_success",
    [
        # simple cases
        (b"#!/usr/bin/env python", True),
        (b"#!/usr/bin/env -S pip-run", True),
        (b"#!/usr/bin/python -W error", True),
        (b"#/usr/bin/env python", False),
        (b"!/usr/bin/env python", False),
        # invalid start byte (not BOM)
        (b"\xf1#!/usr/bin/env -S python", False),
        # valid BOM start bytes
        (codecs.BOM_UTF8 + b"#!/usr/bin/env -S python", True),
        (codecs.BOM_LE + b"#!/usr/bin/env -S python", True),
        (codecs.BOM_BE + b"#!/usr/bin/env -S python", True),
        # invalid start sequence (BOM appears multiple times)
        (codecs.BOM_UTF8 + codecs.BOM_UTF8 + b"#!/usr/bin/env -S python", False),
    ],
)
def test_shebang_line_detection(tmp_path, shebang, expect_success):
    script = tmp_path / 'script'
    script.write_bytes(shebang + b'\nprint("Hello world!")')
    if expect_success:
        assert _has_shebang(script)
    else:
        assert not _has_shebang(script)
