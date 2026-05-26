import main as cli


class FakeRound:
    """Round payload for CLI rendering tests."""

    round_number = 1
    con_argument = "con says hello"
    pro_argument = "pro replies"
    penalties: list[object] = []
    judge_notes = type("Notes", (), {"con_notes": "con note", "pro_notes": "pro note"})()


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
        return type("Result", (), {"topic": topic, "winner": "pro", "rounds": [FakeRound()]})()


def test_cli_parser_accepts_expected_flags() -> None:
    """CLI parser accepts the required public flags."""
    args = cli.build_parser().parse_args(["--topic", "1", "--pings", "2", "--verbose"])

    assert args.topic == 1 and args.pings == 2 and args.verbose is True


def test_cli_list_topics_uses_sdk(capsys) -> None:
    """CLI list-topics path consumes the SDK."""
    cli.main(["--list-topics"], sdk=FakeSdk())

    assert "Topic A" in capsys.readouterr().out


def test_cli_prints_debate_transcript(capsys) -> None:
    """CLI prints Con and Pro debate turns from the SDK result."""
    cli.main(["--topic", "1"], sdk=FakeSdk())

    output = capsys.readouterr().out

    assert "con says hello" in output and "pro replies" in output


def test_cli_passes_config_path_to_default_sdk(monkeypatch, capsys, tmp_path) -> None:
    """The public --config flag controls the setup file loaded by the SDK."""
    config_path = tmp_path / "setup.json"
    captured: dict[str, object] = {}

    class CapturingSdk(FakeSdk):
        def __init__(self, **kwargs) -> None:
            super().__init__()
            captured.update(kwargs)

    monkeypatch.setattr(cli, "DebateSimulatorSDK", CapturingSdk)

    cli.main(["--topic", "1", "--config", str(config_path)])

    assert captured["setup_path"] == str(config_path)
