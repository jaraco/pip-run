.. image:: https://img.shields.io/pypi/v/pip-run.svg
   :target: https://pypi.org/project/pip-run

.. image:: https://img.shields.io/pypi/pyversions/pip-run.svg

.. image:: https://github.com/jaraco/pip-run/workflows/tests/badge.svg
   :target: https://github.com/jaraco/pip-run/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: Black

.. image:: https://readthedocs.org/projects/pip-run/badge/?version=latest
   :target: https://pip-run.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2023-informational
   :target: https://blog.jaraco.com/skeleton

.. image:: https://tidelift.com/badges/package/pypi/pip-run
   :target: https://tidelift.com/subscription/pkg/pypi-pip-run?utm_source=pypi-pip-run&utm_medium=readme

``pip-run`` provides on-demand temporary package installation
for a single execution run.

It replaces this series of commands (or their Windows equivalent)::

    $ virtualenv --python pythonX.X --system-site-packages $temp/env
    $ $temp/env/bin/pip install pkg1 pkg2 -r reqs.txt
    $ $temp/env/bin/python ...
    $ rm -rf $temp/env

With this single-line command::

    $ py -X.X -m pip-run pkg1 pkg2 -r reqs.txt -- ...

Features include

- Downloads missing dependencies and makes their packages available for import.
- Installs packages to a special staging location such that they're not installed after the process exits.
- Relies on pip to cache downloads of such packages for reuse.
- Leaves no trace of its invocation (except files in pip's cache).
- Supersedes installed packages when required.
- Relies on packages already satisfied [1]_.
- Re-uses the pip tool chain for package installation.

``pip-run`` is not intended to solve production dependency management, but does aim to address the other, one-off scenarios around dependency management:

- trials and experiments
- build setup
- test runners
- just in time script running
- interactive development
- bug triage

``pip-run`` is a compliment to Pip and Virtualenv, intended to more
readily address the on-demand needs.

.. [1] Except when a requirements file is used.

Installation
============

``pip-run`` is meant to be installed in the system site packages
alongside pip, though it can also be installed in a virtualenv.

Usage
=====

- as script launcher
- as runtime dependency context manager
- as interactive interpreter in dependency context
- as module launcher (akin to `python -m`)
- as a shell shebang (``#!/usr/bin/env pip-run``), to create single-file Python tools

Invoke ``pip-run`` from the command-line using the console entry
script (simply ``pip-run``) or using the module executable (
``python -m pip-run``). This latter usage is particularly convenient
for testing a command across various Python versions.

Parameters following pip-run are passed directly to ``pip install``,
so ``pip-run numpy`` will install ``numpy`` (reporting any work done
during the install) and ``pip-run -v -r requirements.txt`` will verbosely
install all the requirements listed in a file called requirements.txt
(quiet is the default).
Any `environment variables honored by pip
<https://pip.pypa.io/en/stable/user_guide/#environment-variables>`_
are also honored.

Following the parameters to ``pip install``, one may optionally
include a ``--`` after which any parameters will be executed
by a Python interpreter in the context or directly if prefixed by
``!``.

See ``pip-run --help`` for more details.

Examples
========

The `examples folder in this project
<https://github.com/jaraco/pip-run/tree/master/examples>`_
includes some examples demonstrating
the power and usefulness of the project. Read the docs on those examples
for instructions.

Module Script Runner
--------------------

Perhaps the most powerful usage of ``pip-run`` is its ability to invoke
executable modules and packages via
`runpy <https://docs.python.org/3/library/runpy.html>`_ (aka
``python -m``)::

    $ pip-run cowsay -- -m cowsay "moove over, pip-run"

      -------------------
    < moove over, pip-run >
      -------------------
       \   ^__^
        \  (oo)\_______
           (__)\       )\/\
               ||----w |
               ||     ||

.. image:: docs/cowsay.svg
   :alt: cowsay example animation

Module Executable Runner
------------------------

Some package tools, like `ranger <https://github.com/ranger/ranger>`_, are
invoked with a unique executable instead of a module. ``pip-run`` can
run an executable from a package if it is prependend by a ``!``::

    $ pip-run ranger-fm -- '!ranger'

Command Runner
--------------

Note that everything after the -- is passed to the python invocation,
so it's possible to have a one-liner that runs under a dependency
context::

    $ python -m pip-run requests -- -c "import requests; print(requests.get('https://pypi.org/project/pip-run').status_code)"
    200

As long as ``pip-run`` is installed in each of Python environments
on the system, this command can be readily repeated on the other
python environments by specifying the relevant interpreter::

    $ python3.7 -m pip-run ...

or on Windows or Unix with [pylauncher](https://python-launcher.app/)::

    $ py -3.7 -m pip-run ...

Script Runner
-------------

``pip-run`` can run a Python file with indicated dependencies. Because
arguments after ``--`` are passed directly to the Python interpreter
and because the Python interpreter will run any script, invoking a script
with dependencies is easy. Consider this script "myscript.py":

.. code-block:: python

    #!/usr/bin/env python

    import requests

    req = requests.get('https://pypi.org/project/pip-run')
    print(req.status_code)

To invoke it while making sure requests is present:

    $ pip-run requests -- myscript.py

``pip-run`` will make sure that requests is installed then invoke
the script in a Python interpreter configured with requests and its
dependencies.

For added convenience when running scripts, ``pip-run`` will infer
the beginning of Python parameters if it encounters a filename
of a Python script that exists, allowing for omission of the ``--``
for script invocation:

    $ pip-run requests myscript.py

Script-declared Dependencies
----------------------------

Building on Script Runner above, ``pip-run`` also allows
dependencies to be declared in the script itself so that
the user need not specify them at each invocation.

To declare dependencies in a script, add a ``__requires__``
variable or ``# Requirements:`` section to the script:

.. code-block:: python

    #!/usr/bin/env python

    __requires__ = ['requests']

    # or

    # Requirements:
    # requests

    import requests

    req = requests.get('https://pypi.org/project/pip-run')
    print(req.status_code)

With that declaration in place, one can now invoke ``pip-run`` without
declaring any parameters to pip::

    $ pip-run myscript.py
    200

The format for requirements must follow `PEP 508 <https://www.python.org/dev/peps/pep-0508/>`_.

Single-script Tools and Shebang Support
---------------------------------------

Combined with in-script dependencies, ``pip-run`` can be used as a shebang to
create fully self-contained scripts that install and run their own
dependencies, as long as ``pip-run`` is installed on the system ``PATH``.
Consider, for example, the ``pydragon`` script:

.. code-block:: shell

    #!/usr/bin/env pip-run
    __requires__ = ['requests', 'beautifulsoup4', 'cowsay']
    import requests
    from bs4 import BeautifulSoup as BS
    import cowsay
    res = requests.get('https://python.org')
    b = BS(res.text, 'html.parser')
    cowsay.dragon(b.find("div", class_="introduction").get_text())

This executable script is available in the repo as ``examples/pydragon`` (for
Unix) and ``examples/pydragon.py`` (for Windows [2]_). Executing this script is
equivalent to executing ``pip-run pydragon``.

By default, the script will assemble the dependencies on each invocation,
which may be inconvenient for a script. See `Environment Persistence
<#Environment-Persistence>`_ for a technique to persist the assembled
dependencies across invocations. One may inject ``PIP_RUN_MODE=persist``
in the shebang, but be aware that doing so breaks Windows portability.

.. [2] ``.PY`` must exist in the PATHEXT for Python scripts to be executable. See `this documentation <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables?view=powershell-7.3#path-information>`_ for more background.

Other Script Directives
-----------------------

``pip-run`` also recognizes a global ``__index_url__`` attribute. If present,
this value will supply ``--index-url`` to pip with the attribute value,
allowing a script to specify a custom package index:

.. code-block:: python

    #!/usr/bin/env python

    __requires__ = ['my_private_package']
    __index_url__ = 'https://my.private.index/'

    import my_private_package
    ...

Extracting Requirements
-----------------------

After having used ``pip-run`` to run scripts, it may be desirable to extract the requirements from the ``__requires__`` variable or ``# Requirements:`` section of a
script to install those more permanently. pip-run provides a routine to facilitate
this case::

    $ py -m pip_run.read-deps examples/pydragon
    requests beautifulsoup4 cowsay

On Unix, it is possible to pipe this result directly to pip::

    $ pip install $(py -m pip_run.read-deps examples/pydragon)

To generate a requirements.txt file, specify a newline separator::

    $ py -m pip_run.read-deps --separator newline examples/pydragon > requirements.txt

And since `pipenv <https://docs.pipenv.org/>`_ uses the same syntax,
the same technique works for pipenv::

    $ pipenv install $(python -m pip_run.read-deps script.py)

Interactive Interpreter
-----------------------

``pip-run`` also offers a painless way to run a Python interactive
interpreter in the context of certain dependencies::

    $ /clean-install/python -m pip-run boto
    >>> import boto
    >>>

Experiments and Testing
-----------------------

Because ``pip-run`` provides a single-command invocation, it
is great for experiments and rapid testing of various package
specifications.

Consider a scenario in which one wishes to create an environment
where two different versions of the same package are installed,
such as to replicate a broken real-world environment. Stack two
invocations of pip-run to get two different versions installed::

    $ pip-run keyring==21.8.0 -- -m pip-run keyring==22.0.0 -- -c "import importlib.metadata, pprint; pprint.pprint([dist._path for dist in importlib.metadata.distributions() if dist.metadata['name'] == 'keyring'])"
    [PosixPath('/var/folders/03/7l0ffypn50b83bp0bt07xcch00n8zm/T/pip-run-a3xvd267/keyring-22.0.0.dist-info'),
    PosixPath('/var/folders/03/7l0ffypn50b83bp0bt07xcch00n8zm/T/pip-run-1fdjsgfs/keyring-21.8.0.dist-info')]

.. todo: illustrate example here

IPython Inference
-----------------

If IPython is specified as one of the dependencies, the Python
interpreter will be launched via IPython (using ``-m IPython``)
for interactive mode. This behaviour may be toggled off by
setting the environment variable ``PIP_RUN_IPYTHON_MODE=ignore``.

How Does It Work
================

``pip-run`` effectively does the following:

- ``pip install -t $TMPDIR``
- ``PYTHONPATH=$TMPDIR python``
- cleanup

For specifics, see `pip_run.run()
<https://github.com/jaraco/pip-run/blob/master/pip_run/__init__.py#L9-L16>`_.


Environment Persistence
=======================

``pip-run`` honors the ``PIP_RUN_MODE`` variable. If unset or
set to ``ephemeral``, dependencies are installed to an ephemeral
temporary directory on each invocation (and deleted after).
Setting this variable to ``persist`` will instead create or re-use
a directory in the user's cache, only installing the dependencies if
the directory doesn't already exist. A separate cache is maintained
for each combination of requirements specified.

``persist`` mode can greatly improve startup performance at the
expense of staleness and accumulated cruft.

Without ``PIP_RUN_MODE=persist`` (or with ``=ephemeral``), ``pip-run`` will
re-install dependencies every time a script runs, silently adding to the
startup time while dependencies are installed into an ephemeral environment,
depending on how many dependencies there are and whether the dependencies have
been previously downloaded to the local pip cache. Use ``pip-run -v ...`` to
see the installation activity.

The location of the cache can be revealed with this command::

    py -c 'import importlib; print(importlib.import_module("pip_run.mode.persist").paths.user_cache_path)'


Limitations
===========

- Due to limitations with ``pip``, ``pip-run`` cannot run with "editable"
  (``-e``) requirements.

- ``pip-run`` uses a ``sitecustomize`` module to ensure that ``.pth`` files
  in the requirements are installed. As a result, any environment
  that has a ``sitecustomize`` module will find that module masked
  when running under ``pip-run``.

Comparison with pipx
====================

The `pipx project <https://pypi.org/project/pipx/>`_ is another mature
project with similar goals. Both projects expose a project and its
dependencies in ephemeral environments. The main difference is pipx
primarily exposes Python binaries (console scripts) from those
environments whereas pip-run exposes a Python context (including
runpy scripts).

.. list-table::
   :widths: 30 10 10
   :header-rows: 1

   * - Feature
     - pip-run
     - pipx
   * - user-mode operation
     - ✓
     - ✓
   * - invoke console scripts
     - ✓
     - ✓
   * - invoke runpy modules
     - ✓
     -
   * - run standalone scripts
     - ✓
     -
   * - interactive interpreter with deps
     - ✓
     -
   * - re-use existing environment
     - ✓
     -
   * - ephemeral environments
     - ✓
     - ✓
   * - persistent environments
     - ✓
     - ✓
   * - PEP 582 support
     -
     - ✓
   * - Specify optional dependencies
     - ✓
     -
   * - Python 2 support
     - ✓
     -

Comparison with virtualenvwrapper mktmpenv
==========================================

The `virtualenvwrapper project <https://pypi.org/project/virtualenvwrapper/>`_
attempts to address some of the use-cases that pip-run solves,
especially with the ``mktmpenv`` command, which destroys the
virtualenv after deactivation. The main difference is that ``pip-run``
is transient only for the invocation of a single command, while
``mktmpenv`` lasts for a session.

.. list-table::
   :widths: 40 10 10
   :header-rows: 1

   * - Feature
     - pip-run
     - mktmpenv
   * - create temporary package environment
     - ✓
     - ✓
   * - re-usable across python invocations
     - ✓
     - ✓
   * - portable
     - ✓
     -
   * - one-line invocation
     - ✓
     -
   * - multiple interpreters in session
     - ✓
     -
   * - run standalone scripts
     - ✓
     - ✓
   * - interactive interpreter with deps
     - ✓
     - ✓
   * - re-use existing environment
     - ✓
     -
   * - ephemeral environments
     - ✓
     - ✓
   * - persistent environments
     - ✓
     - ✓

Integration
===========

The author created this package with the intention of demonstrating
the capability before integrating it directly with pip in a command
such as ``pip run``. After proposing the change, the idea was largely
rejected in `pip 3971 <https://github.com/pypa/pip/issues/3971>`_.

If you would like to see this functionality made available in pip,
please upvote or comment in that ticket.

Versioning
==========

``pip-run`` uses semver, so you can use this library with
confidence about the stability of the interface, even
during periods of great flux.

Testing
=======

Invoke tests with ``tox``.

For Enterprise
==============

Available as part of the Tidelift Subscription.

This project and the maintainers of thousands of other packages are working with Tidelift to deliver one enterprise subscription that covers all of the open source you use.

`Learn more <https://tidelift.com/subscription/pkg/pypi-pip-run?utm_source=pypi-pip-run&utm_medium=referral&utm_campaign=github>`_.

Security Contact
================

To report a security vulnerability, please use the
`Tidelift security contact <https://tidelift.com/security>`_.
Tidelift will coordinate the fix and disclosure.
