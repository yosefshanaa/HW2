from enum import Enum


class AgentRole(str, Enum):
    """Agent roles used by the debate simulator."""

    JUDGE = "judge"
    PRO = "pro"
    CON = "con"


class Stance(str, Enum):
    """Debater stances assigned for a topic."""

    PRO = "pro"
    CON = "con"


class StanceCue(str, Enum):
    """Text cues used by basic stance validation."""

    FOR = "for"
    AGAINST = "against"


class PenaltyType(str, Enum):
    """Penalty categories enforced by the judge and process manager."""

    DISRESPECT = "disrespect"
    IGNORE_REBUTTAL = "ignore_rebuttal"
    STANCE_CONTRADICTION = "stance_contradiction"
    EXCEED_LINES = "exceed_lines"
    EXCEED_TIME = "exceed_time"


class SessionState(str, Enum):
    """Lifecycle states for a debate session."""

    INIT = "init"
    RESEARCH = "research"
    DEBATE = "debate"
    SCORING = "scoring"
    FINISHED = "finished"


class ScoreDimension(str, Enum):
    """Weighted score dimensions for final evaluation."""

    ARGUMENT_STRENGTH = "argument_strength"
    REBUTTAL_EFFECTIVENESS = "rebuttal_effectiveness"
    EVIDENCE_RESEARCH = "evidence_research"
    RHETORICAL_QUALITY = "rhetorical_quality"
    COMPLIANCE = "compliance"


class LogLevel(str, Enum):
    """Supported logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ConfigFile(str, Enum):
    """Project configuration file locations."""

    SETUP = "config/setup.json"
    RATE_LIMITS = "config/rate_limits.json"


class TimeWindowSeconds(int, Enum):
    """Named time windows used by rate limiting."""

    MINUTE = 60
    HOUR = 3600


class ServiceName(str, Enum):
    """External service names used by the API gatekeeper."""

    DEFAULT = "default"


__all__ = [
    "AgentRole",
    "ConfigFile",
    "LogLevel",
    "PenaltyType",
    "ScoreDimension",
    "ServiceName",
    "SessionState",
    "Stance",
    "StanceCue",
    "TimeWindowSeconds",
]
