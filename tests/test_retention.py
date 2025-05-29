import pytest

from pip_run import retention


@pytest.mark.usefixtures('retention_strategy')
def test_target_retention_context():
    """Verify a target exists or can be created."""
    with retention.strategy().context([]) as target:
        target.mkdir(exist_ok=True)
