"""Base interface for enterprise AI platform adapters."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from fde_workbench.domain.agent_specs import AgentSpecification


class PlatformAdapter(ABC):
    """Abstract base class for platform-specific compilation of agent specifications."""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """The enterprise platform identifier (e.g. 'gemini_enterprise', 'openai', etc.)."""
        pass

    @abstractmethod
    def export_manifest(self, spec: AgentSpecification) -> Dict[str, Any]:
        """Compile a platform-agnostic specification into a platform-compliant configuration manifest."""
        pass

    def validate_compatibility(self, spec: AgentSpecification) -> Dict[str, Any]:
        """Check whether the agent specification satisfies platform-specific requirements."""
        missing_fields: List[str] = []
        if not spec.objective:
            missing_fields.append("objective")
        if not spec.tools:
            missing_fields.append("tools")
        return {
            "platform": self.platform_name,
            "compatible": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "tool_count": len(spec.tools),
            "human_in_loop_enforced": bool(spec.human_approval_requirements),
        }
