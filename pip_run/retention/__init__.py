import functools
import importlib
import json
import os
import re


class Strategy(str):
    params: dict[str, str]

    @classmethod
    def resolve(cls, spec):
        """
        Resolve a strategy spec to a strategy name and context params.

        >>> Strategy.resolve('destroy')
        'destroy'
        >>> Strategy.resolve('persist').params
        {}
        >>> Strategy.resolve('persist {"max-age": 86400}').params
        {'max_age': 86400}
        >>> Strategy.resolve('persist {"max age": 86400, "other": true}').params
        {'max_age': 86400, 'other': True}
        """
        name, sep, rest = spec.partition(' ')
        strat = cls(name)
        doc = json.loads(rest.strip() or '{}')
        strat.params = {make_var(name): value for name, value in doc.items()}
        return strat


def make_var(name):
    return re.sub(r'[ -]+', '_', name.strip())


def strategy():
    spec = os.environ.get('PIP_RUN_RETENTION_STRATEGY') or 'destroy'
    strat = Strategy.resolve(spec)
    module = importlib.import_module(f'.{strat}', package=__package__)
    return functools.partial(module.context, **strat.params)
