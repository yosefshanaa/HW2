from debate_simulator.agents.judge_helpers import (
    analytical_note,
    average_round_scores,
    detect_repetition,
    fallback_round_data,
    map_penalties,
)
from debate_simulator.shared.constants import PenaltyPoints, PenaltyType


def test_detect_repetition_no_history() -> None:
    pro, con = detect_repetition("hello", "world", [], [])
    assert pro == [] and con == []


def test_detect_repetition_pro_repetitive() -> None:
    text = "climate change is real and requires action now"
    pro, con = detect_repetition(text, "unrelated", [text, "older argument"], [])
    assert pro == ["repetition"] and con == []


def test_detect_repetition_con_repetitive() -> None:
    text = "the economy needs reform and investment today"
    pro, con = detect_repetition("unrelated", text, [], [text, "older argument"])
    assert pro == [] and con == ["repetition"]


def test_detect_repetition_both_repetitive() -> None:
    pro_text = "pro argument about climate change is happening"
    con_text = "con argument about climate change is happening"
    pro, con = detect_repetition(pro_text, con_text, [pro_text, "old"], [con_text, "old"])
    assert len(pro) > 0 and len(con) > 0


def test_analytical_note_addresses_opponent() -> None:
    note = analytical_note("Pro", "pro addresses con and data evidence", "con")
    assert "addressed the opponent" in note


def test_analytical_note_no_overlap() -> None:
    note = analytical_note("Pro", "pro makes independent point", "con")
    assert "needs a more direct rebuttal" in note


def test_analytical_note_with_evidence() -> None:
    note = analytical_note("Pro", "pro uses because evidence", "con")
    assert "some supporting evidence" in note


def test_analytical_note_without_evidence() -> None:
    note = analytical_note("Pro", "pro argues strongly", "con")
    assert "no supporting evidence" in note


def test_fallback_round_data_keys() -> None:
    data = fallback_round_data("pro arg", "con arg")
    assert "pro_notes" in data and "con_notes" in data
    assert "pro_speaker_score" in data and "con_speaker_score" in data


def test_fallback_round_data_penalty_lists_empty() -> None:
    data = fallback_round_data("pro", "con")
    assert data["pro_penalties"] == [] and data["con_penalties"] == []


def test_average_round_scores_empty() -> None:
    scores = average_round_scores([], [])
    assert "pro" in scores and "con" in scores


def test_average_round_scores_with_values() -> None:
    scores = average_round_scores([80.0, 90.0], [70.0, 80.0])
    assert scores["pro"].total == 85.0
    assert scores["con"].total == 75.0


def test_map_penalties_valid_type() -> None:
    penalties = map_penalties("pro", ["repetition", "ignore_rebuttal"])
    assert len(penalties) == 2
    assert penalties[0].agent == "pro"


def test_map_penalties_invalid_type_skipped() -> None:
    penalties = map_penalties("con", ["invalid_penalty", "disrespect"])
    assert len(penalties) == 1
    assert penalties[0].type == PenaltyType.DISRESPECT


def test_map_penalties_stance_contradiction_heavy() -> None:
    penalties = map_penalties("pro", ["stance_contradiction"])
    assert penalties[0].points == PenaltyPoints.STANCE_CONTRADICTION.value


def test_map_penalties_accepts_uppercase_llm_names() -> None:
    penalties = map_penalties("pro", ["STANCE_CONTRADICTION", "IGNORE_REBUTTAL"])
    assert [p.type for p in penalties] == [
        PenaltyType.STANCE_CONTRADICTION,
        PenaltyType.IGNORE_REBUTTAL,
    ]


def test_map_penalties_empty_list() -> None:
    assert map_penalties("pro", []) == []


def test_map_penalties_uses_penalty_points() -> None:
    penalties = map_penalties("pro", ["exceed_time"])
    assert penalties[0].points == PenaltyPoints.EXCEED_TIME.value
