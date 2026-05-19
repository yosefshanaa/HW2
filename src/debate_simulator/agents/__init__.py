from debate_simulator.agents.base_agent import BaseAgent
from debate_simulator.agents.debater_agent import ConDebaterAgent, DebaterAgent, ProDebaterAgent
from debate_simulator.agents.judge_agent import JudgeAgent
from debate_simulator.shared.version import VERSION

__version__ = VERSION
__all__ = [
    "BaseAgent",
    "ConDebaterAgent",
    "DebaterAgent",
    "JudgeAgent",
    "ProDebaterAgent",
    "__version__",
]
