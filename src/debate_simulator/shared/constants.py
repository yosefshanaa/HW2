from enum import Enum


class AgentRole(str, Enum):
    JUDGE = "judge"
    PRO = "pro"
    CON = "con"


class Stance(str, Enum):
    PRO = "pro"
    CON = "con"


class StanceCue(str, Enum):
    FOR = "for"
    AGAINST = "against"


class PenaltyType(str, Enum):
    DISRESPECT = "disrespect"
    IGNORE_REBUTTAL = "ignore_rebuttal"
    STANCE_CONTRADICTION = "stance_contradiction"
    EXCEED_LINES = "exceed_lines"
    EXCEED_WORDS = "exceed_words"
    EXCEED_TIME = "exceed_time"
    REPETITION = "repetition"


class SessionState(str, Enum):
    INIT = "init"
    RESEARCH = "research"
    DEBATE = "debate"
    SCORING = "scoring"
    FINISHED = "finished"


class ScoreDimension(str, Enum):
    ARGUMENT_STRENGTH = "argument_strength"
    REBUTTAL_EFFECTIVENESS = "rebuttal_effectiveness"
    EVIDENCE_RESEARCH = "evidence_research"
    RHETORICAL_QUALITY = "rhetorical_quality"
    COMPLIANCE = "compliance"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ConfigFile(str, Enum):
    SETUP = "config/setup.json"
    RATE_LIMITS = "config/rate_limits.json"


class TimeWindowSeconds(int, Enum):
    MINUTE = 60
    HOUR = 3600


class ServiceName(str, Enum):
    DEFAULT = "default"


class PenaltyPoints(int, Enum):
    DISRESPECT = -5
    IGNORE_REBUTTAL = -10
    STANCE_CONTRADICTION = -15
    EXCEED_LINES = -5
    EXCEED_WORDS = -5
    EXCEED_TIME = -10
    REPETITION = -10
    DEFAULT = -5


class FallbackText(str, Enum):
    AGENT_TIMEOUT = "Agent timed out"
    AGENT_CRASH = "Agent crashed"


class FifoDefault(float, Enum):
    READ_TIMEOUT_SECONDS = 1.0


class EnvPlaceholder(str, Enum):
    OPENAI_API_KEY = "your_api_key_here"


class ScoreDefault(float, Enum):
    SPEAKER_MIN = 50.0
    SPEAKER_MAX = 100.0
    FALLBACK_ROUND_SCORE = 65.0
    DEFAULT_TOTAL = 60.0
    DEFAULT_SPEAKER_SCORE = 70.0
    JITTER_RANGE = 2.5
    TIE_MARGIN = 2.0


class RepetitionThreshold(float, Enum):
    JUDGE_BIGRAM_OVERLAP = 0.55
    DEBATER_BIGRAM_OVERLAP = 0.35


class ContextWindow(int, Enum):
    JUDGE_HISTORY_ROUNDS = 4


class DebaterThreshold(int, Enum):
    MIN_SOURCE_LENGTH = 6
    MIN_SOURCE_EXTRACT = 4


__all__ = [
    "AgentRole", "ConfigFile", "ContextWindow", "DebaterThreshold", "EnvPlaceholder",
    "FallbackText", "FifoDefault", "LogLevel", "PenaltyPoints", "PenaltyType",
    "RepetitionThreshold", "ScoreDefault", "ScoreDimension", "ServiceName",
    "SessionState", "Stance", "StanceCue", "TimeWindowSeconds",
]
