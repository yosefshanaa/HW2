def main() -> None:
    """Run the debate simulator CLI."""
    import sys

    from main import main as _cli

    _cli(sys.argv[1:])


if __name__ == "__main__":
    main()
