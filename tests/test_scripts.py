import textwrap
import sys
import subprocess

import pytest
import nbformat
import jaraco.path

from pip_run import scripts
from pip_run.commands import _has_python_shebang


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
    "shebang",
    [
        # env invocations
        "#!/usr/bin/env python",
        "#!/usr/bin/env python3",
        "#!/usr/bin/env python3.7",
        "#!/usr/bin/env python3.8",
        "#!/usr/bin/env python3.9",
        "#!/usr/bin/env python3.10",
        "#!/usr/bin/env python3.11",
        "#!/usr/bin/env python3.12",
        "#!/usr/bin/env py",
        "#!/usr/bin/env pypy",
        "#!/usr/bin/env pypy3",
        "#!/usr/bin/env pip-run",
        # env -S invocations
        "#!/usr/bin/env -S pip-run",
        "#!/usr/bin/env -S python3.12 -W ignore::foo",
        # direct invocations
        "#!/usr/bin/python -W error",
        "#!/home/user/.local/bin/python",
        "#!/some/custom/abspath/py",
        "#!/opt/bin/python3",
        "#!/usr/local/bin/python3.7",
    ],
)
def test_shebang_line_detection_success(tmp_path, shebang):
    script = tmp_path / 'script'
    script.write_text(f'{shebang}\nprint("Hello world!")')

    assert _has_python_shebang(script)


@pytest.mark.parametrize(
    "shebang",
    [
        # not a proper shebang
        "#/usr/bin/env python",
        "!/usr/bin/env python",
        # python2, yikes!
        "#!/usr/bin/env python2",
        # some other tool or command entirely
        "#!/usr/bin/env bash",
        "#!/bin/bash",
        # env -S invocations with other commands
        "#!/usr/bin/env -S bash",
        # a command that actually could be a python invocation, but isn't
        # reasonable to expect pip-run to detect
        "#!/usr/bin/env -S bash -c 'python'",
        "#!/home/user/bin/cpython",
        "#!/home/user/bin/mypython",
    ],
)
def test_shebang_line_detection_fails(tmp_path, shebang):
    script = tmp_path / 'script'
    script.write_text(f'{shebang}\nprint("Hello world!")')
    assert not _has_python_shebang(script)


def test_shebang_line_detection_fails_on_invalid_unicode(tmp_path):
    script = tmp_path / 'script'
    # \xf1 is not a valid codepoint in utf-8
    script.write_bytes(b'#!/usr/bin/env -S python \xf1\nprint("Hello world!")')
    # checking this should fail but without an exception
    assert not _has_python_shebang(script)


def test_shebang_line_detection_ignores_invalid_unicode_in_body(tmp_path):
    script = tmp_path / 'script'
    # \xf1 is not a valid codepoint in utf-8, but it's in the body and
    # therefore should be ignored
    script.write_bytes(b'#!/usr/bin/env -S python\nx = "\xf1"\nprint(x)')
    # checking this should pass
    assert _has_python_shebang(script)
