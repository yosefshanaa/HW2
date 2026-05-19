import argparse
from typing import Any

from rich.console import Console

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
    console.print(f"Winner: {result.winner}")


def _topic_from_index(sdk: Any, topic_index: int | None) -> str:
    topics = sdk.list_topics()
    if topic_index is None:
        return topics[0]
    return topics[topic_index - 1]


if __name__ == "__main__":
    main()
