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

Testing
-------

Invoke tests with ``setup.py test``.
