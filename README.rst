.. image:: https://img.shields.io/pypi/v/rwt.svg
   :target: https://pypi.org/project/rwt

.. image:: https://img.shields.io/pypi/pyversions/rwt.svg

.. image:: https://img.shields.io/travis/jaraco/rwt/master.svg
   :target: https://travis-ci.org/jaraco/rwt

.. image:: https://img.shields.io/appveyor/ci/jaraco/rwt/master.svg
   :target: https://ci.appveyor.com/project/jaraco/rwt/branch/master

.. image:: https://readthedocs.org/projects/rwt/badge/?version=latest
   :target: https://rwt.readthedocs.io/en/latest/?badge=latest

/ruːt/

RWT (Run With This) provides on-demand dependency resolution,
making packages available for the duration of an interpreter
session.

- Allows declaration of dependencies at runtime.
- Downloads missing dependencies and makes their packages available for import.
- Installs packages to a special staging location such that they're not installed after the process exits.
- Relies on pip to cache downloads of such packages for reuse.
- Supersedes installed packages when required.
- Relies on packages already satisfied [1]_.
- Re-uses the pip tool chain for package installation.

RWT is not intended to solve production dependency management, but does aim to address the other, one-off scenarios around dependency management:

- build setup
- test runners
- just in time script running
- interactive development

RWT is a compliment to Pip and Virtualenv and Setuptools, intended to more
readily address the on-demand needs and supersede some
features like ``setup_requires``.

.. [1] Except when a requirements file is used.

Usage
=====

- as script launcher
- as runtime dependency context manager
- as interactive interpreter in dependency context
- as module launcher (akin to `python -m`)

Invoke ``rwt`` from the command-line using the console entry
script (simply ``rwt``) or using the module executable (
``python -m rwt``).

Parameters following rwt are passed directly to ``pip install``,
so ``rwt numpy`` will install ``numpy`` (reporting any work done
during the install) and ``rwt -q -r requirements.txt`` will quietly
install all the requirements listed in a file called requirements.txt.

Following the parameters to ``pip install``, one may optionally
include a ``--`` after which any parameters will be passed
to a Python interpreter in the context.

Examples
========

The ``examples`` folder in this project includes some examples demonstrating
the power and usefulness of the project. Read the docs on those examples
for instructions.

In many of these examples, the option ``-q`` is passed to ``rwt``
to suppress the output from pip.

Interactive Interpreter
-----------------------

RWT also offers a painless way to run a Python interactive
interpreter in the context of certain dependencies::

    $ /clean-install/python -m rwt -q boto
    >>> import boto
    >>>


Command Runner
--------------

Note that everything after the -- is passed to the python invocation,
so it's possible to have a one-liner that runs under a dependency
context::

    $ python -m rwt -q requests -- -c "import requests; print(requests.get('https://pypi.org/project/rwt').status_code)"
    200

Script Runner
-------------

Let's say you have a script that has a one-off purpose. It's either not
part of a library, where dependencies are normally declared, or it is
normally executed outside the context of that library. Still, that script
probably has dependencies, say on `requests
<https://pypi.org/project/requests>`_. Here's how you can use rwt to
declare the dependencies and launch the script in a context where
those dependencies have been resolved.

First, add a ``__requires__`` directive at the head of the script::

    #!/usr/bin/env python

    __requires__ = ['requests']

    import requests

    req = requests.get('https://pypi.org/project/rwt')
    print(req.status_code)

Then, simply invoke that script with rwt::

    $ python -m rwt -q -- myscript.py
    200

The format for requirements must follow `PEP 508 <https://www.python.org/dev/peps/pep-0508/>`_.

Note that URLs specifiers are not supported by pip, but ``rwt`` supports a
global ``__dependency_links__`` attribute which can be used, for example, to
install requirement from a project VCS URL::

    #!/usr/bin/env python

    __requires__ = ['foo==0.42']
    __dependency_links__ = ['git+ssh://git@example.com/repo.git#egg=foo-0.42']

    [...]

``rwt`` also recognizes a global ``__index_url__`` attribute. If present,
this value will supply ``--index-url`` to pip with the attribute value,
allowing a script to specify a custom package index::

    #!/usr/bin/env python

    __requires__ = ['my_private_package']
    __index_url__ = 'https://my.private.index/'

    import my_private_package
    ...

Replacing setup_requires
------------------------

Following the script example, you can make your setup.py file
compatible with ``rwt`` by declaring your depenedencies in
the ``__requires__`` directive::

    #!/usr/bin/env python

    __requires__ = ['setuptools', 'setuptools_scm']

    import setuptools

    setuptools.setup(
        ...
        setup_requires=__requires__,
    )

When invoked with rwt, the dependencies will be assured before
the script is run, or if run with setuptools, the dependencies
will be loaded using the older technique, so the script is
backward compatible.

Replacing tests_require
-----------------------

Although this example is included for completeness,
because the technique is somewhat clumsy, the
author currently recommends using ``tox`` for running
tests except in extremely lean environments.

You can also replace tests_require. Consider a package that
runs tests using ``setup.py test`` and relies on the
``tests_require`` directive to resolve dependencies needed
during testing. Simply declare your dependencies in a
separate file, e.g. "tests/requirements.txt"::

    cat > tests/requiremenst.txt
    pytest

For compatibility, expose those same requirements as
tests_require in setup.py::

    with io.open('tests/requirements.txt') as tr:
        tests_require = [
        	line.rstrip()
        	for line in tr
        	if re.match('\w+', line)
        ]

    setuptools.setup(
        ...
        tests_require=tests_require,
    )

Then invoke tests with rwt::

    $ python -m rwt -r tests/requirements.txt -- setup.py test

While still supporting the old technique::

    $ python setup.py test

Supplying parameters to Pip
---------------------------

If you've been using ``rwt``, you may have defined some requirements
in the ``__requires__`` of a script, but now you wish to install those
to a more permanent environment. rwt provides a routine to facilitate
this case:

    $ python -m rwt.read-deps script.py
    my_dependency

If you're on Unix, you may pipe this result directly to pip:

    $ pip install $(python -m rwt.read-deps script.py)

And since `pipenv <https://docs.pipenv.org/>`_ uses the same syntax,
the same technique works for pipenv:

    $ pipenv install $(python -m rwt.read-deps script.py)

How Does It Work
================

RWT effectively does the following:

- ``pip install -t $TMPDIR``
- ``PYTHONPATH=$TMPDIR python``
- cleanup

For specifics, see `rwt.run()
<https://github.com/jaraco/rwt/blob/master/rwt/__init__.py#L9-L16>`_.

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

RWT uses semver, so you can use this library with
confidence about the stability of the interface, even
during periods of great flux.

Testing
=======

Invoke tests with ``tox``.
