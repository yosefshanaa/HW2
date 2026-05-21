"""Bigram-overlap repetition and source-reuse detection for debater agents."""

from __future__ import annotations

import re

from debate_simulator.models.debate import Penalty
from debate_simulator.shared.constants import (
    DebaterThreshold,
    PenaltyPoints,
    PenaltyType,
    RepetitionThreshold,
)

_OVERLAP_THRESHOLD = RepetitionThreshold.DEBATER_BIGRAM_OVERLAP.value
_MIN_SOURCE_LEN = DebaterThreshold.MIN_SOURCE_LENGTH.value
_MIN_EXTRACT_LEN = DebaterThreshold.MIN_SOURCE_EXTRACT.value
_EXPLICIT_SOURCE_RE = re.compile(r"\(source:\s*([^)]+)\)", re.IGNORECASE)
_QUOTED_SOURCE_RE = re.compile(
    r'"([A-Z][^"]*(?:\d{4}|University|Institute|Journal|ESPN|BBC|Reuters|FIFA|Uefa|Forbes|Deloitte)[^"]*)"'
)


def check_repetition(text: str, previous_arguments: list[str], agent: str) -> Penalty | None:
    """Detect if *text* reuses phrases from any prior argument via bigram overlap."""
    if not previous_arguments:
        return None
    words = text.lower().split()
    if len(words) < 3:
        return None
    current_bigrams = set(zip(words, words[1:], strict=False))
    if not current_bigrams:
        return None
    for prev in previous_arguments:
        prev_words = prev.lower().split()
        if len(prev_words) < 3:
            continue
        prev_bigrams = set(zip(prev_words, prev_words[1:], strict=False))
        union = len(current_bigrams | prev_bigrams)
        if union == 0:
            continue
        overlap = len(current_bigrams & prev_bigrams) / union
        if overlap > _OVERLAP_THRESHOLD:
            return Penalty(
                type=PenaltyType.REPETITION,
                points=PenaltyPoints.REPETITION.value,
                reason=f"argument bigram overlap {overlap:.0%} with a prior round",
                agent=agent,
            )
    return None


def check_source_reuse(text: str, used_sources: list[str], agent: str) -> Penalty | None:
    """Penalize if a previously used explicit citation appears again in *text*."""
    for source in used_sources[:-1]:
        if len(source) < _MIN_SOURCE_LEN:
            continue
        if source in text:
            return Penalty(
                type=PenaltyType.REPETITION,
                points=PenaltyPoints.REPETITION.value,
                reason=f"reused citation: {source[:60]}",
                agent=agent,
            )
    return None


def extract_sources(text: str, used_sources: list[str], known_sources: list[str]) -> None:
    """Extract explicitly cited sources from *text* and append new ones to *used_sources*."""
    for match in _EXPLICIT_SOURCE_RE.findall(text):
        cleaned = match.strip()
        if len(cleaned) >= _MIN_EXTRACT_LEN and cleaned not in used_sources:
            used_sources.append(cleaned)
    for match in _QUOTED_SOURCE_RE.findall(text):
        if match not in used_sources:
            used_sources.append(match)
    for word in text.split():
        if word.startswith("http") and word not in used_sources:
            used_sources.append(word)
    for source in known_sources:
        if len(source) >= _MIN_SOURCE_LEN and source in text and source not in used_sources:
            used_sources.append(source)


__all__ = ["check_repetition", "check_source_reuse", "extract_sources"]
