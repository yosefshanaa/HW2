from debate_simulator.services.debate_engine import DebateEngine
from debate_simulator.services.debater_service import DebaterService
from debate_simulator.services.judge_service import JudgeService
from debate_simulator.services.scoring_service import ScoringService
from debate_simulator.shared.version import VERSION

__version__ = VERSION
__all__ = ["DebateEngine", "DebaterService", "JudgeService", "ScoringService", "__version__"]
