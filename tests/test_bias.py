"""Run N debates and tally Pro/Con wins to check for systematic bias."""


def main(n: int = 5, topic: int | None = None) -> None:
    from debate_simulator.sdk import DebateSimulatorSDK

    sdk = DebateSimulatorSDK()
    topics = sdk.list_topics()
    topic_str = topics[(topic or 1) - 1]
    results = {"pro": 0, "con": 0, "details": []}

    for i in range(n):
        print(f"\n--- Debate {i + 1}/{n} ---")
        result = sdk.start_debate(topic_str)
        w = result.winner
        results[w] += 1
        pro = result.final_scores["pro"].total
        con = result.final_scores["con"].total
        gap = pro - con
        results["details"].append({"debate": i + 1, "winner": w, "pro": _r(pro, 1), "con": _r(con, 1), "gap": _r(gap, 1)})
        print(f"  Winner: {w.upper():6s}  Pro={pro:.1f}  Con={con:.1f}  Gap={gap:+.1f}")

    print(f"\n{'='*50}")
    total = n
    print(f"Results from {total} debates on: {topic_str}")
    print(f"  Pro wins: {results['pro']}/{total} ({results['pro']/total*100:.0f}%)")
    print(f"  Con wins: {results['con']}/{total} ({results['con']/total*100:.0f}%)")
    avg_gap = sum(d["gap"] for d in results["details"]) / total
    print(f"  Avg score gap (Pro - Con): {avg_gap:+.2f}")
    print(f"{'='*50}")


def _r(v: float, n: int = 1) -> float:
    return round(v, n)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run N debates and report win statistics")
    parser.add_argument("-n", type=int, default=5, help="Number of debates to run")
    parser.add_argument("--topic", type=int, default=None, help="Topic number (1-10)")
    parser.add_argument("--list-topics", action="store_true", help="List available topics")
    args = parser.parse_args()

    if args.list_topics:
        from debate_simulator.sdk import DebateSimulatorSDK
        for i, t in enumerate(DebateSimulatorSDK().list_topics(), 1):
            print(f"  {i}. {t}")
    else:
        main(n=args.n, topic=args.topic)
