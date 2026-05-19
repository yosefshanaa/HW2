from debate_simulator import __version__
from debate_simulator.shared.version import VERSION


def test_package_version_is_1_00() -> None:
    """Package exports the required assignment version."""
    assert VERSION == "1.00"
    assert __version__ == "1.00"
