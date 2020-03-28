v6.0.0
------

#39: Removed ``pip_run.deps.on_sys_path``, originally intended
for API-use for making packages available at run time in
the same process.

5.3
---

#36: Instead of soliciting the environment variable,
the workaround for pip #4106 is now automatically
applied, but only when it is needed.

5.2
---

#36: Allow bypass of workaround for pip #4106
by setting ``PIP_RUN_NO_PATCH_PREFIX``.

5.1
---

* Updated documentation.

5.0
---

#34: Renamed project from ``rwt`` to ``pip-run``.

4.4.2
-----

#32: Fix regression in the 4.2 release where ``rwt``
sometimes fails to install some local packages.

4.4.1
-----

Fixed issue with file encoding declaration in future
f-string handling.

4.4
---

#30: Support reading deps from scripts with f-strings
on older Pythons.

4.3
---

#29: Unconditionally honor ``.pth`` files in installed
packages.

4.2
---

#28: Avoid error when arguments to ``pip install``
existed but did not indicate any packages to install.

4.1
---

Added support for Jython by using JYTHONPATH instead
of PYTHONPATH when on Jython.

4.0.1
-----

Use ``io.open`` in ``scripts`` reader for better Jython
compatibility. See `Jython 2696
<http://bugs.jython.org/issue2696>`_ for more info.

4.0
---

Dropped support for injecting modules to sys.path when
Setuptools is older than 19.6.2 (presumed unused).

Package now uses Setuptools declarative config and thus
will not install from sdist without Setuptools 30.3 or later.

3.3
---

Added support for pip 10, including addressing #25. As a
side benefit, warnings are no longer issued when no
requirements are supplied.

3.2
---

Added ``rwt.read-deps`` command.

3.1
---

#24: Add support for ``__dependency_links__``.

#23: Fix test failures on Windows.

3.0
---

Minor incompatibilty - ``DepsReader.read`` no longer accepts a
``var_name`` parameter.

#19: DepsReader.read and DepsReader.try_read now return a
scripts.Dependencies instance, which always has an
``index_url`` attribute whose value will reflect
the value of ``__index_url__`` from the script (if present)
or None otherwise.

#19: For standalone scripts, if ``__index_url__`` is indicated,
it will be used to resolve dependencies.

2.16
----

#18: More fully support ``__requires__`` syntax as supported
by pkg_resources. This change had the unintended side-effect
of disallowing full dependency links (URLs) in ``__requires__``.
See #22 for details.

Updated package from skeleton.

2.15.1
------

Issue #15: Fixed issue where rwt would crash in environments
where pip's vendored dependencies (namely pkg_resources)
were unbundled.

2.15
----

Issue #14: Added workaround for pip #4106 such that rwt now
runs on Homebrew Python and other environments where a distutils
prefix is defined.

2.14
----

Added support for excluding already installed packages, but
only when requirements are not specified in a requirements.txt
file. Inspired by conversations at HackIllinois and Issue #13.

2.13
----

Issue #10: When launching the target subprocess, pass through
the exit code.

Now renders normal output from ``pip install``.

2.12
----

Allow args to ``rwt.run`` function to be passed directly.

2.11
----

Issue #1: Inject a sitecustomize into the install path
to work around the lack of -nspkg.pth execution. Skip the
execution on Python 3.3 and later, as it will degrade the
behavior in those environments as indicated in #5.

2.10
----

Issue #9: Intercept the ``--help`` argument if specified
rather than passing that to pip install.

2.9
---

Issue #8: Add a console entrypoint, so one can
invoke simply ``rwt``.

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
