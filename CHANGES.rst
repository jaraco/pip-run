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
