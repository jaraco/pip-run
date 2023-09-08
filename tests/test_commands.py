import pytest

from pip_run import commands


valid_shebangs = [
    '#!/usr/bin/env python',
    '#!/usr/bin/env -S pip-run',
    '#!/usr/bin/python -W error',
    # with BOM
    '#!/usr/bin/env -S python'.encode('utf-8-sig').decode('utf-8'),
]

invalid_shebangs = [
    '#/usr/bin/env python',
    '!/usr/bin/env python',
]


@pytest.mark.parametrize('shebang', valid_shebangs)
def test_shebang_detected(tmp_path, shebang):
    script = tmp_path / 'script'
    script.write_text(f'{shebang}\nprint("Hello world!")', encoding='utf-8')
    assert commands._has_shebang(script)


@pytest.mark.parametrize('shebang', invalid_shebangs)
def test_shebang_not_detected(tmp_path, shebang):
    script = tmp_path / 'script'
    script.write_text(f'{shebang}\nprint("Hello world!")', encoding='utf-8')
    assert not commands._has_shebang(script)


def test_shebang_invalid_encoding(tmp_path):
    """
    If the script cannot be decoded in UTF-8, value should be false.
    """
    script = tmp_path / 'script'
    shebang = '\xf1#!/usr/bin/env -S python'
    script.write_text(f'{shebang}\nprint("Hello world!")', encoding='latin-1')
    assert not commands._has_shebang(script)
