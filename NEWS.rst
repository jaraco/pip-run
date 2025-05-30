v16.1.0
=======

Features
--------

- Implement support for max_age in persistent environments. To set a max age on persistent environments, use ``PIP_RUN_RETENTION_STRATEGY=persist {"max age": "2 weeks"}``. Default is unchanged, but likely the default retention strategy will switch to ``persist {"max age": "1 day"}`` (or multiple days) in a future release. (#85)


v16.0.4
=======

Bugfixes
--------

- Declare py_modules using underscore. Avoids deprecation warning. (#118)


v16.0.3
=======

Bugfixes
--------

- Suppress FileNotFoundError when attempting to inject sitecustomize file on a degenerate install. (#123)


v16.0.2
=======

Bugfixes
--------

- Rely on ignore_cleanup_errors on Python 3.10+ to suppress cleanup errors. (#122)


v16.0.1
=======

No significant changes.


v16.0.0
=======

Deprecations and Removals
-------------------------

- Now supports and prefers uv as the installer if present. Now either 'uv' or 'pip' must be installed as commands. 'pip' has been removed as a dependency. (#100)


v15.1.0
=======

Features
--------

- Leverages coherent.deps to infer dependencies from scripts. Now it's possible to omit the dependencies in most cases when executing a script. (#115)


v15.0.0
=======

Deprecations and Removals
-------------------------

- Removed support for comment style requirements.


v14.0.0
=======

Deprecations and Removals
-------------------------

- Removed support for PIP_RUN_MODE.
- Removed support for a single string arg to ``__requires__``.


v13.0.0
=======

Deprecations and Removals
-------------------------

- Dropped support for filtering out satisfied requirements. (#51)


v12.7.0
=======

Features
--------

- Deprecated support for non-sequence __requires__. (#109)


v12.6.1
=======

Bugfixes
--------

- Ensure docs/tests not unintentionally included.


v12.6.0
=======

Features
--------

- Comment-style declarations are now deprecated in favor of Python or TOML style. (#97)


v12.5.0
=======

Features
--------

- Add support for script dependencies in a TOML block per PEP 723. (#96)


v12.4.0
=======

Features
--------

- Ensure requirements with a URL are not detected as installed. (#77)


v12.3.1
=======

Bugfixes
--------

- Removed Python 3.7 compatibility code.


v12.3.0
=======

Features
--------

- Renamed PIP_RUN_MODE variable to PIP_RUN_RETENTION_STRATEGY. Also renamed the default value of 'ephemeral' to 'destroy'. If PIP_RUN_MODE is used, a warning is emitted. (#84)


v12.2.2
=======

Bugfixes
--------

- Made pydragon example portable to Windows


v12.2.1
=======

Bugfixes
--------

- Refreshed README


v12.2.0
=======

Features
--------

- Presence of Python script parameters now honors files with a shebang even if no Python extension is present. (#78)


v12.1.0
=======

Features
--------

- Require Python 3.8 or later.


Bugfixes
--------

- Fixed EncodingWarning in scripts module.


v12.0.1
=======

Bugfixes
--------

- Fix IndexError when no parameters are supplied. (#76)


v12.0.0
=======

Features
--------

- The executable parameters now accept a ``!`` prefix, indicating to run a separate executable instead of Python in the context. (#75)


Deprecations and Removals
-------------------------

- ``pip_run.launch.with_path`` now expects the literal command to be passed and no longer injects the ``sys.executable``. For compatibility, pass the executable in the params or wrap the params in something like ``pip_run.launch.infer_cmd``. (#75)


v11.0.0
=======

IPython inference now uses a different variable and an
explicit string value to disable inference. Instead of
``PIP_RUN_INFER_IPYTHON=0``, use
``PIP_RUN_IPYTHON_MODE=ignore``.

v10.2.0
=======

#67: Now if ``ipython`` is included in the dependencies, it
will be used as the default interactive interpreter
(implying ``-m IPython``).

v10.1.1
=======

#73: Added missing implicit test dependencies on setuptools
and wheel (revealed by virtualenv 20.23.0).

v10.1.0
=======

#72: Now the ``bin`` directory in the target is inserted at
the front of the ``PATH`` variable, making scripts available
as installed by packages.

v10.0.7
=======

#70: Avoid OSError when a parameter to Python exceeds the
allowed filename length.

v10.0.6
=======

Fixed ``EncodingWarnings``.

v10.0.5
=======

#69: Fixed handling of inferred Python args.

v10.0.4
=======

#68: Fixed ``FileNotFoundError`` in persistent mode.

v10.0.3
=======

#66: Fixed regression in sitecustomize generation where pathlib
objects were being rendered.

v10.0.2
=======

#65: Tests that require connectivity are now tagged with the
``network`` marker.

v10.0.1
=======

#65: Tests that require connectivity to the Internet now are skipped.

v10.0.0
=======

Removed ``launch.with_path_overlay``, unused in this project.

Removed explicit parsing of ``.pth`` files, redundant to the
use of ``sitecustomize``.

Removed ``commands.parse_script_args`` (use ``separate`` instead).

Removed processing of ``JYTHONPATH`` as Jython is Python 2 only.

Removed ``commands.separate_dash``.

v9.5.0
======

Modernized path handling using pathlib (internal refactoring).

Renamed ``commands.parse_script_args`` to ``separate``, with an
alias for compatibility.

Restored coverage in tests.

v9.4.0
======

#64: Switch to ``platformdirs`` for resolving the cache dir.

v9.3.0
======

#52: ``pip-run`` now honors a ``PIP_RUN_MODE``.

v9.2.1
======

#62: Fixed minimum dependency on ``more_itertools`` to match
usage.

v9.2.0
======

#60: ``pip-run`` additionally supports the "limited requirements"
in comments in a script.

v9.1.0
======

#57: ``pip-run`` no longer requires a ``--`` separator when
the first argument to Python is an extant Python script.

v9.0.0
======

#58: ``pip-run`` now sets ``PIP_QUIET=1`` when invoking
pip to install packages. To see the pip installer output during
installation, pass ``-v`` and in general one additional ``v``
to achieve the prior behavior. It is no longer necessary to pass
``-q`` to suppress the installer output.

v8.8.2
======

Packaging refresh.

v8.8.1
======

Packaging refresh.

v8.8.0
======

Expose ``pip_run.launch.inject_sitecustomize``.

v8.7.2
======

#56: Prevent ResourceWarning when opening pth files.

v8.7.1
======

Restore missing ``Requires-Python`` metadata.

v8.7.0
======

Require Python 3.7 or later.

v8.6.1
======

#55: Suppressed deprecation warning in test suite.

v8.6.0
======

#53: ``read-deps`` script now accepts a ``--separator`` argument
accepting arbitrary separators or any of the named separators:

 - newline
 - space
 - null

v8.5.1
======

Updated build to exclude 'examples', not intended to be installed.

v8.5.0
======

Removed dependency on ``pkg_resources``. Just importing that
module mucks with sys.path and causes problems.

v8.4.3
======

Refreshed package metadata.

v8.4.2
======

Refreshed package metadata.

v8.4.1
======

#49: Declare dependency on ``packaging``.

v8.4.0
======

#40: Remove dependency on ``pkg_resources``.

v8.3.0
======

#47: ``read_deps`` now errors on non-existent files.

v8.2.1
======

#46: Fixed AttributeError in ``read-deps``.

v8.2.0
======

Add support for reading deps from Jupyter Notebooks.

v6.3.0
======

Add support for reading deps from Jupyter Notebooks.

v8.1.0
======

#43: Removed workaround for pip 4106. Project now requires
pip 19.3 or later.

v6.2.0
======

#43: Removed workaround for pip 4106. Project now requires
pip 19.3 or later.

v8.0.0
======

#41: Removed support for ``__dependency_links__``
in scripts. Instead, use PEP 508 syntax.
For example, to run a script requiring requests at master::

    __requires__ = ['requests @ git+https://github.com/requests/requests']

v6.1.0
======

* semver deviation *

#41: Removed support for ``__dependency_links__``
in scripts. Instead, use PEP 508 syntax.

For example, to run a script requiring requests at master::

    __requires__ = ['requests @ git+https://github.com/requests/requests']

v7.0.1
======

Updated readme to remove ``setup_requires`` as a targeted
use-case.

v7.0.0
======

Project now requries Python 3.6 or later.

v6.0.0
======

#39: Removed ``pip_run.deps.on_sys_path``, originally intended
for API-use for making packages available at run time in
the same process.

5.3
===

#36: Instead of soliciting the environment variable,
the workaround for pip #4106 is now automatically
applied, but only when it is needed.

5.2
===

#36: Allow bypass of workaround for pip #4106
by setting ``PIP_RUN_NO_PATCH_PREFIX``.

5.1
===

* Updated documentation.

5.0
===

#34: Renamed project from ``rwt`` to ``pip-run``.

4.4.3
=====

Update README to reflect project rename.

4.4.2
=====

#32: Fix regression in the 4.2 release where ``rwt``
sometimes fails to install some local packages.

4.4.1
=====

Fixed issue with file encoding declaration in future
f-string handling.

4.4
===

#30: Support reading deps from scripts with f-strings
on older Pythons.

4.3
===

#29: Unconditionally honor ``.pth`` files in installed
packages.

4.2
===

#28: Avoid error when arguments to ``pip install``
existed but did not indicate any packages to install.

4.1
===

Added support for Jython by using JYTHONPATH instead
of PYTHONPATH when on Jython.

4.0.1
=====

Use ``io.open`` in ``scripts`` reader for better Jython
compatibility. See `Jython 2696
<http://bugs.jython.org/issue2696>`_ for more info.

4.0
===

Dropped support for injecting modules to sys.path when
Setuptools is older than 19.6.2 (presumed unused).

Package now uses Setuptools declarative config and thus
will not install from sdist without Setuptools 30.3 or later.

3.3
===

Added support for pip 10, including addressing #25. As a
side benefit, warnings are no longer issued when no
requirements are supplied.

3.2
===

Added ``rwt.read-deps`` command.

3.1
===

#24: Add support for ``__dependency_links__``.

#23: Fix test failures on Windows.

3.0
===

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
====

#18: More fully support ``__requires__`` syntax as supported
by pkg_resources. This change had the unintended side-effect
of disallowing full dependency links (URLs) in ``__requires__``.
See #22 for details.

Updated package from skeleton.

2.15.1
======

Issue #15: Fixed issue where rwt would crash in environments
where pip's vendored dependencies (namely pkg_resources)
were unbundled.

2.15
====

Issue #14: Added workaround for pip #4106 such that rwt now
runs on Homebrew Python and other environments where a distutils
prefix is defined.

2.14
====

Added support for excluding already installed packages, but
only when requirements are not specified in a requirements.txt
file. Inspired by conversations at HackIllinois and Issue #13.

2.13
====

Issue #10: When launching the target subprocess, pass through
the exit code.

Now renders normal output from ``pip install``.

2.12
====

Allow args to ``rwt.run`` function to be passed directly.

2.11
====

Issue #1: Inject a sitecustomize into the install path
to work around the lack of -nspkg.pth execution. Skip the
execution on Python 3.3 and later, as it will degrade the
behavior in those environments as indicated in #5.

2.10
====

Issue #9: Intercept the ``--help`` argument if specified
rather than passing that to pip install.

2.9
===

Issue #8: Add a console entrypoint, so one can
invoke simply ``rwt``.

2.8
===

Issue #7: Extract entries from .pth files in the
temporary install folder and include those values
in PYTHONPATH when launching the subprocess.

2.7.1
=====

Issue #6: Only augment but don't replace PYTHONPATH.

2.7
===

Issue #4: No longer use execve because it will suppress
the cleanup code after the child exits. Instead, trap
the interrupt in the parent process and suppress
it.

2.6
===

Issue #3: ``rwt`` now relies on ``execve`` to overlay
the child process over the current one.

2.5
===

Allow dependencies to be declared in the file in the
parameters to the Python interpreter, even if other
parameters are supplied. Allows for invocation like::

    rwt -- -i myscript.py

2.4.2
=====

Fixed issue in ``__requires__`` parsing when script
contained attribute assignment.

2.4.1
=====

Restored simple python launch process.

2.4
===

Added support for resolving dependencies declared in
``__requires__`` in the script.

2.3
===

New technique uses PYTHONPATH and subprocess to launch any
arbitrary Python process.

2.2
===

Add support for entry points on older versions of setuptools.

2.1
===

Add support for pkg_resources entry points in added modules.

2.0
===

``python -m rwt`` now has a new signature, requiring a full list of
args to pip install and a separate script to execute, separated by
"--".

1.0
===

Initial implementation. Basic dependency context for running a script.
