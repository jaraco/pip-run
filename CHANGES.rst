2.8
---

Issue #7: Extract entries from .pth files in the
temporary install folder and include those values
in PYTHONPATH when launching the subprocess.

2.7.1
-----

Issue #6: Only augment but don't replace PYTHONPATH.

2.7
---

Issue #4: No longer use execve because it will suppress
the cleanup code after the child exits. Instead, trap
the interrupt in the parent process and suppress
it.

2.6
---

Issue #3: ``rwt`` now relies on ``execve`` to overlay
the child process over the current one.

2.5
---

Allow dependencies to be declared in the file in the
parameters to the Python interpreter, even if other
parameters are supplied. Allows for invocation like::

    rwt -- -i myscript.py

2.4.2
-----

Fixed issue in ``__requires__`` parsing when script
contained attribute assignment.

2.4.1
-----

Restored simple python launch process.

2.4
---

Added support for resolving dependencies declared in
``__requires__`` in the script.

2.3
---

New technique uses PYTHONPATH and subprocess to launch any
arbitrary Python process.

2.2
---

Add support for entry points on older versions of setuptools.

2.1
---

Add support for pkg_resources entry points in added modules.

2.0
---

``python -m rwt`` now has a new signature, requiring a full list of
args to pip install and a separate script to execute, separated by
"--".

1.0
---

Initial implementation. Basic dependency context for running a script.
