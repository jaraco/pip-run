import codecs

import pytest

from pip_run import commands


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
        # invalid start sequence (BOM appears multiple times)
        (codecs.BOM_UTF8 + codecs.BOM_UTF8 + b"#!/usr/bin/env -S python", False),
    ],
)
def test_shebang_line_detection(tmp_path, shebang, expect_success):
    script = tmp_path / 'script'
    script.write_bytes(shebang + b'\nprint("Hello world!")')
    if expect_success:
        assert commands._has_shebang(script)
    else:
        assert not commands._has_shebang(script)
