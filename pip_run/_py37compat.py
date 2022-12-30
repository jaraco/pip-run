try:
    from importlib import metadata  # type: ignore
except ImportError:  # pragma: no cover
    import importlib_metadata as metadata  # type: ignore


metadata = metadata
