from debate_simulator.shared.version import VERSION
from debate_simulator.skills.base_skill import BaseSkill, SkillResult
from debate_simulator.skills.router_skill import RouterSkill

__version__ = VERSION
__all__ = ["BaseSkill", "RouterSkill", "SkillResult", "__version__"]
