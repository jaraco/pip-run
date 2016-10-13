/ruːt/

RWT (Run With This) provides on-demand dependency resolution.

.. image:: https://img.shields.io/pypi/v/rwt.svg
   :target: https://pypi.org/project/rwt

.. image:: https://img.shields.io/pypi/pyversions/rwt.svg

.. image:: https://img.shields.io/pypi/dm/rwt.svg

.. image:: https://img.shields.io/travis/jaraco/rwt/master.svg
   :target: http://travis-ci.org/jaraco/rwt

- Allows declaration of dependencies at runtime.
- Downloads missing dependencies and makes their packages available for import.
- Installs packages to a special staging location such that they're not installed after the process exits.
- Relies on pip to cache downloads of such packages for reuse.
- Supersedes installed packages when required.
- Re-uses the pip tool chain for package installation and pkg_resources for working set management.

RWT is not intended to solve production dependency management, but does aim to address the other, one-off scenarios around dependency management:

- build setup
- test runners
- just in time script running
- interactive development

RWT is a compliment to Pip and Virtualenv and Setuptools, intended to more
readily address the on-demand needs and supersede some
features like ``setup_requires``.

Status
------

The project is stable. Please try it in your day-to-day
workflow and give your feedback at the project page.

License is indicated in the project metadata (typically one or more
of the Trove classifiers). For more details, see `this explanation
<https://github.com/jaraco/skeleton/issues/1>`_.

Usage
-----

- as script launcher
- as runtime dependency context manager
- as interactive interpreter in dependency context
- as module launcher (akin to `python -m`)

Examples
--------

The ``examples`` folder in this project includes some examples demonstrating
the power and usefulness of the project. Read the docs on those examples
for instructions.

Script Runner
~~~~~~~~~~~~~

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

    $ python -m rwt -- myscript.py
    Loading requirements using requests
    200

Command Runner
~~~~~~~~~~~~~~

Note that everything after the -- is passed to the python invocation,
so it's possible to have a one-liner that runs under a dependency
context::

    $ python -m rwt requests -- -c "import requests; print(requests.get('https://pypi.io/project/rwt').status_code)"
    Loading requirements using requests
    200

Interactive Interpreter
~~~~~~~~~~~~~~~~~~~~~~~

RWT also offers a painless way to run a Python interactive
interpreter in the context of certain dependencies::

    $ /clean-install/python -m rwt boto
    Loading requirements using boto
    >>> import boto
    >>>

Replacing setup_requires
~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~

You can also replace tests_require. Consider a package that
runs tests using ``setup.py test`` and relies on the
``tests_require`` directive to resolve dependencies needed
during testing. Simply declare your dependencies in a
separate file, "test requirements.txt"::

    # test requirements.txt
    pytest

For compatibility, expose those same requirements as
tests_require in setup.py::

    with io.open('test requirements.txt') as tr:
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

    $ python -m rwt -r "test requirements.txt" -- setup.py test

While still supporting the old technique::

    $ python setup.py test

How Does It Work
----------------

RWT effectively does the following:

- ``pip install -t $TMPDIR``
- ``PYTHONPATH=$TMPDIR python``
- cleanup

For specifics, see ``rwt.run()``.

Versioning
----------

RWT uses semver, so you can use this library with
confidence about the stability of the interface, even
during periods of great flux.

Testing
-------

Invoke tests with ``setup.py test``.
