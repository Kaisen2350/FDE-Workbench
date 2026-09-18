"""Databricks Mosaic AI Agent Framework platform adapter stub."""

from typing import Dict, Any
from fde_workbench.domain.adapters.base import PlatformAdapter
from fde_workbench.domain.agent_specs import AgentSpecification


class DatabricksAdapter(PlatformAdapter):
    """Compiles platform-agnostic AgentSpecification into Databricks Mosaic AI Agent Framework manifest."""

    @property
    def platform_name(self) -> str:
        return "databricks_mosaic"

    def export_manifest(self, spec: AgentSpecification) -> Dict[str, Any]:
        uc_functions = []
        for tool in spec.tools:
            uc_functions.append({
                "catalog": "fde_paraguay_export",
                "schema": "tools",
                "function_name": tool.name,
                "description": tool.description,
                "read_only": tool.read_only,
            })

        return {
            "platform": "Databricks Mosaic AI Agent Framework",
            "model_serving_endpoint": f"endpoint-{spec.spec_id}",
            "unity_catalog_tools": uc_functions,
            "system_prompt": (
                f"# ENTERPRISE AGENT OBJECTIVE\n{spec.objective}\n\n"
                f"# OPERATIONAL CONTEXT\n{spec.context}\n\n"
                f"# DETERMINISTIC CONSTRAINTS\n{spec.reasoning_requirements}\n\n"
                f"# HUMAN APPROVAL REQUIREMENT\n{spec.human_approval_requirements}"
            ),
            "mlflow_experiment": f"/Shared/fde_agents/{spec.spec_id}",
            "eval_metrics": spec.evaluation_criteria,
            "target_kpis": spec.kpis,
        }
