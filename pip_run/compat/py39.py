import sys

ignore_cleanup_errors = (
    dict(ignore_cleanup_errors=True) if sys.version_info >= (3, 10) else {}
)
