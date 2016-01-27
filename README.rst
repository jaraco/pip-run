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

Status
------

The project is currently still experimental and liable
to undergo substantial revision. Do feel free to try
it out and give your feedback at the project page.

Usage
-----

- as script launcher
- as runtime dependency context manager

Planned usage includes

- as interactive interpreter in dependency context
- as module launcher (akin to `python -m`)

Versioning
----------

RWT uses semver, so you can use this library with
confidence about the stability of the interface, even
during periods of great flux.

Testing
-------

Invoke tests with ``setup.py test``.
