import argparse
from typing import Any

from rich.console import Console
from rich.panel import Panel

from debate_simulator.hooks import HookRegistry
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
    hooks = _build_live_hooks(console) if sdk is None else None
    debate_sdk = sdk or DebateSimulatorSDK(hooks=hooks)
    if args.list_topics:
        for index, topic in enumerate(debate_sdk.list_topics(), start=1):
            console.print(f"{index}. {topic}")
        return
    topic = args.custom_topic or _topic_from_index(debate_sdk, args.topic)
    config = {"pings": args.pings} if args.pings else None
    result = debate_sdk.start_debate(topic, config=config)
    if hooks is None:
        _print_result(console, result)


def _build_live_hooks(console: Console) -> HookRegistry:
    hooks = HookRegistry()
    hooks.register_hook("on_debate_start", lambda topic: console.rule(str(topic)))
    hooks.register_hook("on_round_end", lambda round_model, **_: _print_round(console, round_model))
    hooks.register_hook("on_debate_end", lambda results: _print_final(console, results))
    return hooks


def _topic_from_index(sdk: Any, topic_index: int | None) -> str:
    topics = sdk.list_topics()
    if topic_index is None:
        return topics[0]
    return topics[topic_index - 1]


def _print_result(console: Console, result: Any) -> None:
    console.rule(str(result.topic))
    for round_model in result.rounds:
        _print_round(console, round_model)
    _print_final(console, result)


def _print_round(console: Console, round_model: Any) -> None:
    console.print(f"[bold]Ping {round_model.round_number}[/bold]")
    console.print(Panel(round_model.con_argument, title="Con", border_style="red"))
    console.print(Panel(round_model.pro_argument, title="Pro", border_style="green"))
    _print_judge_notes(console, round_model.judge_notes)
    _print_penalties(console, round_model.penalties)


def _print_final(console: Console, result: Any) -> None:
    console.rule("Final")
    _print_scores(console, getattr(result, "final_scores", {}))
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


def _print_scores(console: Console, scores: dict[str, Any]) -> None:
    if not scores:
        return
    lines = []
    for side in ["con", "pro"]:
        score = scores.get(side)
        if score is not None:
            lines.append(f"{side.title()}: {getattr(score, 'total', 0):.1f}%")
    console.print(Panel("\n".join(lines), title="Scores"))


if __name__ == "__main__":
    main()
