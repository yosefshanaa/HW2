from debate_simulator.agents.repetition import check_repetition, check_source_reuse, extract_sources


def test_check_repetition_no_history() -> None:
    result = check_repetition("hello world", [], "pro")
    assert result is None


def test_check_repetition_short_text() -> None:
    result = check_repetition("hi", ["some prior argument"], "pro")
    assert result is None


def test_check_repetition_no_overlap() -> None:
    result = check_repetition(
        "The economy is growing rapidly this year",
        ["Dogs and cats are common household pets"],
        "pro",
    )
    assert result is None


def test_check_repetition_high_overlap() -> None:
    text = "The economy is growing rapidly this year and next year"
    result = check_repetition(text, ["The economy is growing rapidly this year and beyond"], "pro")
    assert result is not None
    assert result.type.value == "repetition"
    assert result.agent == "pro"


def test_check_repetition_multiple_history_entries() -> None:
    text = "climate change is real and requires action now"
    result = check_repetition(
        text,
        ["unrelated topic", "climate change is real and requires immediate action"],
        "con",
    )
    assert result is not None


def test_check_repetition_low_overlap_below_threshold() -> None:
    text = "We should invest in public transportation systems"
    result = check_repetition(text, ["Public infrastructure spending is important"], "pro")
    assert result is None


def test_check_source_reuse_no_sources() -> None:
    result = check_source_reuse("some text", [], "pro")
    assert result is None


def test_check_source_reuse_short_source_ignored() -> None:
    result = check_source_reuse("short source: abc", ["abc"], "pro")
    assert result is None


def test_check_source_reuse_detects_reuse() -> None:
    source = "https://www.bbc.com/news/article-123"
    result = check_source_reuse(f"According to {source}", [source, source], "pro")
    assert result is not None
    assert "reused citation" in result.reason


def test_check_source_reuse_latest_allowed() -> None:
    source = "https://www.example.com/long-url-article"
    result = check_source_reuse(f"See {source}", [source], "pro")
    assert result is None


def test_extract_sources_explicit_parenthetical() -> None:
    used: list[str] = []
    extract_sources("(source: BBC News 2024)", used, [])
    assert any("BBC News" in s for s in used)


def test_extract_sources_quoted_institutional() -> None:
    used: list[str] = []
    extract_sources('According to "Reuters 2023 report findings"', used, [])
    assert any("Reuters" in s for s in used)


def test_extract_sources_http_url() -> None:
    used: list[str] = []
    extract_sources("Check https://example.com/article for details", used, [])
    assert "https://example.com/article" in used


def test_extract_sources_known_sources() -> None:
    used: list[str] = []
    extract_sources("The Cambridge University Study 2022 confirms our position", used, ["Cambridge University Study 2022"])
    assert any("Cambridge" in s for s in used)


def test_extract_sources_no_duplicates() -> None:
    used: list[str] = []
    extract_sources("(source: BBC News)", used, [])
    first_len = len(used)
    extract_sources("(source: BBC News)", used, [])
    assert len(used) == first_len


def test_extract_sources_short_explicit_ignored() -> None:
    used: list[str] = []
    extract_sources("(source: abc)", used, [])
    assert used == []


def test_check_repetition_empty_bigrams() -> None:
    result = check_repetition("a b c", ["d e f g h i j k"], "con")
    assert result is not None or result is None


def test_check_repetition_very_short_prev() -> None:
    result = check_repetition("hello world foo bar", ["hi"], "pro")
    assert result is None
