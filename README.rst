.. image:: https://img.shields.io/pypi/v/pip-run.svg
   :target: https://pypi.org/project/pip-run

.. image:: https://img.shields.io/pypi/pyversions/pip-run.svg

.. image:: https://github.com/jaraco/pip-run/workflows/tests/badge.svg
   :target: https://github.com/jaraco/pip-run/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: Black

.. image:: https://readthedocs.org/projects/pip-run/badge/?version=latest
   :target: https://pip-run.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2022-informational
   :target: https://blog.jaraco.com/skeleton

.. image:: https://tidelift.com/badges/package/pypi/pip-run
   :target: https://tidelift.com/subscription/pkg/pypi-pip-run?utm_source=pypi-pip-run&utm_medium=readme

``pip-run`` provides on-demand temporary package installation
for a single interpreter run.

It replaces this series of commands (or their Windows equivalent)::

    $ virtualenv --python pythonX.X --system-site-packages $temp/env
    $ $temp/env/bin/pip install pkg1 pkg2 -r reqs.txt
    $ $temp/env/bin/python ...
    $ rm -rf $temp/env

With this single-line command::

    $ pythonX.X -m pip-run pkg1 pkg2 -r reqs.txt -- ...

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

``pip-run`` is a compliment to Pip and Virtualenv and Setuptools, intended to more
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

Invoke ``pip-run`` from the command-line using the console entry
script (simply ``pip-run``) or using the module executable (
``python -m pip-run``). This latter usage is particularly convenient
for testing a command across various Python versions.

Parameters following pip-run are passed directly to ``pip install``,
so ``pip-run numpy`` will install ``numpy`` (reporting any work done
during the install) and ``pip-run -q -r requirements.txt`` will quietly
install all the requirements listed in a file called requirements.txt.
Any `environment variables honored by pip
<https://pip.pypa.io/en/stable/user_guide/#environment-variables>`_
are also honored.

Following the parameters to ``pip install``, one may optionally
include a ``--`` after which any parameters will be passed
to a Python interpreter in the context.

Examples
========

The `examples folder in this project
<https://github.com/jaraco/pip-run/tree/master/examples>`_
includes some examples demonstrating
the power and usefulness of the project. Read the docs on those examples
for instructions.

In many of these examples, the option ``-q`` is passed to ``pip-run``
to suppress the output from pip.

Module Script Runner
--------------------

Perhaps the most powerful usage of ``pip-run`` is its ability to invoke
executable modules and packages via
`runpy <https://docs.python.org/3/library/runpy.html>`_ (aka
``python -m``)::

    $ pip-run -q pycowsay -- -m pycowsay "moove over, pip-run"

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

Interactive Interpreter
-----------------------

``pip-run`` also offers a painless way to run a Python interactive
interpreter in the context of certain dependencies::

    $ /clean-install/python -m pip-run -q boto
    >>> import boto
    >>>


Command Runner
--------------

Note that everything after the -- is passed to the python invocation,
so it's possible to have a one-liner that runs under a dependency
context::

    $ python -m pip-run -q requests -- -c "import requests; print(requests.get('https://pypi.org/project/pip-run').status_code)"
    200

As long as ``pip-run`` is installed in each of Python environments
on the system, this command can be readily repeated on the other
python environments by specifying the relevant interpreter::

    $ python2.7 -m pip-run ...

or on Windows::

    $ py -2.7 -m pip-run ...

Experiments and Testing
-----------------------

Because ``pip-run`` provides a single-command invocation, it
is great for experiments and rapid testing of various package
specifications.

Consider a scenario in which one wishes to create an environment
where two different versions of the same package are installed,
such as to replicate a broken real-world environment. Stack two
invocations of pip-run to get two different versions installed::

    $ pip-run -q keyring==21.8.0 -- -m pip-run -q keyring==22.0.0 -- -c "import importlib.metadata, pprint; pprint.pprint([dist._path for dist in importlib.metadata.distributions() if dist.metadata['name'] == 'keyring'])"
    [PosixPath('/var/folders/03/7l0ffypn50b83bp0bt07xcch00n8zm/T/pip-run-a3xvd267/keyring-22.0.0.dist-info'),
    PosixPath('/var/folders/03/7l0ffypn50b83bp0bt07xcch00n8zm/T/pip-run-1fdjsgfs/keyring-21.8.0.dist-info')]

.. todo: illustrate example here

Script Runner
-------------

Let's say you have a script that has a one-off purpose. It's either not
part of a library, where dependencies are normally declared, or it is
normally executed outside the context of that library. Still, that script
probably has dependencies, say on `requests
<https://pypi.org/project/requests>`_. Here's how you can use pip-run to
declare the dependencies and launch the script in a context where
those dependencies have been resolved.

First, add a ``__requires__`` directive at the head of the script:

.. code-block:: python

    #!/usr/bin/env python

    __requires__ = ['requests']

    import requests

    req = requests.get('https://pypi.org/project/pip-run')
    print(req.status_code)

Then, simply invoke that script with pip-run::

    $ python -m pip-run -q -- myscript.py
    200

The format for requirements must follow `PEP 508 <https://www.python.org/dev/peps/pep-0508/>`_.

``pip-run`` also recognizes a global ``__index_url__`` attribute. If present,
this value will supply ``--index-url`` to pip with the attribute value,
allowing a script to specify a custom package index:

.. code-block:: python

    #!/usr/bin/env python

    __requires__ = ['my_private_package']
    __index_url__ = 'https://my.private.index/'

    import my_private_package
    ...

Supplying parameters to Pip
---------------------------

If you've been using ``pip-run``, you may have defined some requirements
in the ``__requires__`` of a script, but now you wish to install those
to a more permanent environment. pip-run provides a routine to facilitate
this case::

    $ python -m pip_run.read-deps script.py
    my_dependency

If you're on Unix, you may pipe this result directly to pip::

    $ pip install $(python -m pip_run.read-deps script.py)

And since `pipenv <https://docs.pipenv.org/>`_ uses the same syntax,
the same technique works for pipenv::

    $ pipenv install $(python -m pip_run.read-deps script.py)

How Does It Work
================

``pip-run`` effectively does the following:

- ``pip install -t $TMPDIR``
- ``PYTHONPATH=$TMPDIR python``
- cleanup

For specifics, see `pip_run.run()
<https://github.com/jaraco/pip-run/blob/master/pip_run/__init__.py#L9-L16>`_.

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
     -
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
     -
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

The `mkvirtualenv project <https://pypi.org/project/mkvirtualenv/>`_
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
     -
     - ✓
   * - portable
     -
     - ✓
   * - one-line invocation
     - ✓
     -
   * - multiple interpreters in session
     - ✓
     -
   * - run standalone scripts
     -
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
     -
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
