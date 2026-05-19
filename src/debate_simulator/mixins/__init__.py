from debate_simulator.mixins.logging_mixin import LoggingMixin
from debate_simulator.mixins.skill_registry_mixin import SkillRegistryMixin
from debate_simulator.mixins.timeout_mixin import TimeoutMixin
from debate_simulator.shared.version import VERSION

__version__ = VERSION
__all__ = ["LoggingMixin", "SkillRegistryMixin", "TimeoutMixin", "__version__"]
