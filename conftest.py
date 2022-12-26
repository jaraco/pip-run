import textwrap

import jaraco.path
import pytest


collect_ignore = ['examples']


@pytest.fixture
def reqs_files(tmp_path):
    """Create a couple of requirements files."""
    jaraco.path.build(
        {
            'reqs1.txt': textwrap.dedent(
                """
                abc
                def
                """
            ).lstrip(),
            'reqs2.txt': textwrap.dedent(
                """
                uvw
                xyz
                """
            ).lstrip(),
        },
        tmp_path,
    )
    return tmp_path.glob('reqs*.txt')
