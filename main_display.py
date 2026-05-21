"""Rich terminal display helpers for the debate CLI."""

from __future__ import annotations

from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel


def print_round(console: Console, round_model: Any) -> None:
    """Render one debate round with pro/con panels and judge notes."""
    console.print(f"\n[bold cyan]── Round {round_model.round_number} ──[/bold cyan]")
    console.print(Panel(round_model.con_argument, title="Con", border_style="red", padding=(0, 2)))
    console.print(
        Panel(round_model.pro_argument, title="Pro", border_style="green", padding=(0, 2))
    )
    _print_judge_notes(console, round_model.judge_notes)
    _print_penalties(console, round_model.penalties)


def print_result(console: Console, result: Any) -> None:
    """Print a full debate result after the fact."""
    console.rule(str(result.topic))
    for round_model in result.rounds:
        print_round(console, round_model)
    print_final(console, result)


def print_header(console: Console, topic: str) -> None:
    """Print the debate header panel."""
    console.print(
        Panel(
            f"[bold]{topic}[/bold]",
            title="AI Court Debate Simulator",
            border_style="cyan",
            box=box.DOUBLE,
        )
    )


def print_final(console: Console, result: Any) -> None:
    """Print the final scores and winner announcement."""
    console.rule("[bold]Final Scores[/bold]")
    _print_scores(console, getattr(result, "final_scores", {}))
    winner_color = {"pro": "green", "con": "red", "tie": "yellow"}.get(result.winner, "white")
    console.print(f"\n[bold {winner_color}]Winner: {result.winner.upper()}[/bold {winner_color}]")


def print_topics(console: Console, topics: list[str]) -> None:
    """Print the numbered topic list."""
    console.print("[bold]Available Topics:[/bold]\n")
    for index, topic in enumerate(topics, start=1):
        console.print(f"  [cyan]{index:2d}.[/cyan] {topic}")


def _print_judge_notes(console: Console, judge_notes: Any) -> None:
    pro_notes = getattr(judge_notes, "pro_notes", "")
    con_notes = getattr(judge_notes, "con_notes", "")
    if pro_notes or con_notes:
        console.print(
            Panel(
                f"[red]Con:[/red] {con_notes}\n[green]Pro:[/green] {pro_notes}",
                title="Judge Notes",
                border_style="blue",
            )
        )


def _print_penalties(console: Console, penalties: list[Any]) -> None:
    if not penalties:
        return
    lines = [
        f"{penalty.agent}: {penalty.type.value} ({penalty.points}) {penalty.reason}"
        for penalty in penalties
    ]
    console.print(Panel("\n".join(lines), title="Penalties", border_style="yellow"))


def _print_scores(console: Console, scores: dict[str, Any]) -> None:
    if not scores:
        return
    lines = []
    for side in ["con", "pro"]:
        score = scores.get(side)
        if score is not None:
            color = "red" if side == "con" else "green"
            lines.append(f"[{color}]{side.title()}: {getattr(score, 'total', 0):.1f}%[/{color}]")
    console.print(Panel("\n".join(lines), title="Scores", border_style="cyan"))


__all__ = ["print_final", "print_header", "print_result", "print_round", "print_topics"]
