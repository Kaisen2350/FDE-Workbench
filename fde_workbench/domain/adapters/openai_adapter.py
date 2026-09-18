"""OpenAI Assistants / Function Calling platform adapter stub."""

from typing import Dict, Any
from fde_workbench.domain.adapters.base import PlatformAdapter
from fde_workbench.domain.agent_specs import AgentSpecification


class OpenAIAdapter(PlatformAdapter):
    """Compiles platform-agnostic AgentSpecification into OpenAI Assistant API manifest."""

    @property
    def platform_name(self) -> str:
        return "openai"

    def export_manifest(self, spec: AgentSpecification) -> Dict[str, Any]:
        tools = []
        for tool in spec.tools:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema or {"type": "object", "properties": {}},
                    "strict": True,
                },
            })

        return {
            "platform": "OpenAI Assistants API",
            "name": spec.title,
            "description": spec.objective,
            "instructions": (
                f"OBJECTIVE: {spec.objective}\n\n"
                f"OPERATIONAL CONTEXT:\n{spec.context}\n\n"
                f"REASONING PROTOCOL:\n{spec.reasoning_requirements}\n\n"
                f"HUMAN APPROVAL REQUIREMENTS:\n{spec.human_approval_requirements}"
            ),
            "tools": tools,
            "metadata": {
                "spec_id": spec.spec_id,
                "version": spec.version,
                "entities": [e.value for e in spec.entities],
                "allowed_actions": spec.actions,
                "kpis": spec.kpis,
            },
        }
