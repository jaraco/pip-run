import importlib
import os


def strategy():
    strategy = os.environ.get('PIP_RUN_RETENTION_STRATEGY') or 'destroy'
    return importlib.import_module(f'.{strategy}', package=__package__)
