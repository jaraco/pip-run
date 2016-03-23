rwt
===

/ruːt/

RWT (Run With This) provides on-demand dependency resolution.

- Allows declaration of dependencies at runtime.
- Downloads missing dependencies and makes their packages available for import.
- Installs packages to a special staging location such that they're not installed after the process exits.
- Keeps a cache of such packages for reuse.
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

The project is currently still experimental and liable
to undergo substantial revision. Do feel free to try
it out and give your feedback at the project page.

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

Interactive Interpreter
~~~~~~~~~~~~~~~~~~~~~~~

RWT also offers a painless way to run a Python interactive
interpreter in the context of certain dependencies::

    $ /clean-install/python -m rwt boto
    Loading requirements using boto
    >>> import boto
    >>>

Versioning
----------

RWT uses semver, so you can use this library with
confidence about the stability of the interface, even
during periods of great flux.

Testing
-------

Invoke tests with ``setup.py test``.
