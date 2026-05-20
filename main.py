import argparse
from typing import Any

from rich.console import Console
from rich.panel import Panel

from debate_simulator.sdk import DebateSimulatorSDK


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=int)
    parser.add_argument("--custom-topic")
    parser.add_argument("--pings", type=int)
    parser.add_argument("--config", default="config/setup.json")
    parser.add_argument("--list-topics", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    return parser


def main(argv: list[str] | None = None, sdk: Any | None = None) -> None:
    """Run the terminal CLI using only the SDK."""
    parser = build_parser()
    args = parser.parse_args(argv)
    console = Console()
    debate_sdk = sdk or DebateSimulatorSDK()
    if args.list_topics:
        for index, topic in enumerate(debate_sdk.list_topics(), start=1):
            console.print(f"{index}. {topic}")
        return
    topic = args.custom_topic or _topic_from_index(debate_sdk, args.topic)
    config = {"pings": args.pings} if args.pings else None
    result = debate_sdk.start_debate(topic, config=config)
    _print_result(console, result)


def _topic_from_index(sdk: Any, topic_index: int | None) -> str:
    topics = sdk.list_topics()
    if topic_index is None:
        return topics[0]
    return topics[topic_index - 1]


def _print_result(console: Console, result: Any) -> None:
    console.rule(str(result.topic))
    for round_model in result.rounds:
        console.print(f"[bold]Ping {round_model.round_number}[/bold]")
        console.print(Panel(round_model.con_argument, title="Con", border_style="red"))
        console.print(Panel(round_model.pro_argument, title="Pro", border_style="green"))
        _print_judge_notes(console, round_model.judge_notes)
        _print_penalties(console, round_model.penalties)
    console.rule("Final")
    console.print(f"[bold]Winner:[/bold] {result.winner}")


def _print_judge_notes(console: Console, judge_notes: Any) -> None:
    pro_notes = getattr(judge_notes, "pro_notes", "")
    con_notes = getattr(judge_notes, "con_notes", "")
    if pro_notes or con_notes:
        console.print(Panel(f"Con: {con_notes}\nPro: {pro_notes}", title="Judge Notes"))


def _print_penalties(console: Console, penalties: list[Any]) -> None:
    if not penalties:
        return
    lines = [f"{penalty.agent}: {penalty.type.value} ({penalty.points}) {penalty.reason}" for penalty in penalties]
    console.print(Panel("\n".join(lines), title="Penalties", border_style="yellow"))


if __name__ == "__main__":
    main()
