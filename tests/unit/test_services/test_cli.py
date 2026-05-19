from main import build_parser, main


class FakeSdk:
    """SDK test double for CLI."""

    def __init__(self) -> None:
        """Create CLI call records."""
        self.started: list[str] = []

    def list_topics(self) -> list[str]:
        """Return deterministic topics."""
        return ["Topic A"]

    def start_debate(self, topic: str, config=None):
        """Record a debate start."""
        self.started.append(topic)
        return type("Result", (), {"winner": "tie"})()


def test_cli_parser_accepts_expected_flags() -> None:
    """CLI parser accepts the required public flags."""
    args = build_parser().parse_args(["--topic", "1", "--pings", "2", "--verbose"])

    assert args.topic == 1 and args.pings == 2 and args.verbose is True


def test_cli_list_topics_uses_sdk(capsys) -> None:
    """CLI list-topics path consumes the SDK."""
    main(["--list-topics"], sdk=FakeSdk())

    assert "Topic A" in capsys.readouterr().out
