import argparse
from typing import Any

from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TextColumn

from debate_simulator.hooks import HookRegistry
from debate_simulator.sdk import DebateSimulatorSDK
from debate_simulator.services.engine_helpers import enable_graceful_shutdown
from debate_simulator.shared.constants import ConfigFile

try:
    from main_display import print_final, print_header, print_result, print_round, print_topics
except ImportError:
    pass


def _get_default_pings() -> int:
    """Read max_pings from config, falling back to constant default."""
    try:
        import json
        from pathlib import Path

        config = json.loads(Path(ConfigFile.SETUP.value).read_text(encoding="utf-8"))
        return int(config.get("debate", {}).get("max_pings", 10))
    except (FileNotFoundError, ValueError, KeyError):
        return 6


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(description="AI Court Debate Simulator")
    parser.add_argument("--topic", type=int, help="Topic number (1-10)")
    parser.add_argument("--custom-topic", help="Custom debate topic")
    parser.add_argument("--pings", type=int, help="Number of debate pings")
    parser.add_argument("--config", default="config/setup.json", help="Config file path")
    parser.add_argument("--list-topics", action="store_true", help="List available topics")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser


def main(argv: list[str] | None = None, sdk: Any | None = None) -> None:
    """Run the terminal CLI using only the SDK."""
    parser = build_parser()
    args = parser.parse_args(argv)
    from rich.console import Console

    console = Console()
    enable_graceful_shutdown()
    hooks = _build_live_hooks(console, args) if sdk is None else None
    debate_sdk = sdk or DebateSimulatorSDK(hooks=hooks)
    if args.list_topics:
        print_topics(console, debate_sdk.list_topics())
        return
    topic = args.custom_topic or _topic_from_index(debate_sdk, args.topic)
    config: dict[str, Any] = {}
    if args.pings:
        config["pings"] = args.pings
    print_header(console, topic)
    result = debate_sdk.start_debate(topic, config=config)
    if hooks is None:
        print_result(console, result)


def _build_live_hooks(console: Any, args: Any) -> HookRegistry:
    hooks = HookRegistry()
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        console=console,
    )
    task_id = None

    def on_start(**kwargs: Any) -> None:
        nonlocal task_id
        task_id = progress.add_task("Debating", total=args.pings or _get_default_pings())
        progress.start()

    def on_round_end(round_model: Any = None, **kwargs: Any) -> None:
        nonlocal task_id
        if task_id is not None:
            progress.update(task_id, advance=1)
        if round_model is not None:
            print_round(console, round_model)

    def on_end(results: Any = None, **kwargs: Any) -> None:
        nonlocal task_id
        if task_id is not None:
            progress.stop()
        if results is not None:
            print_final(console, results)

    hooks.register_hook("on_debate_start", on_start)
    hooks.register_hook("on_round_end", on_round_end)
    hooks.register_hook("on_debate_end", on_end)
    return hooks


def _topic_from_index(sdk: Any, topic_index: int | None) -> str:
    topics = sdk.list_topics()
    if topic_index is None:
        return topics[0]
    return topics[topic_index - 1]


if __name__ == "__main__":
    main()
