"""Databricks Mosaic AI Agent Framework platform adapter stub."""

from typing import Dict, Any, List
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

    def validate_manifest_schema(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates against Databricks Mosaic AI Agent Framework and Unity Catalog tool binding schema.
        Spec: https://docs.databricks.com/en/generative-ai/agent-framework/create-agent.html
        """
        errors: List[str] = []
        if manifest.get("platform") != "Databricks Mosaic AI Agent Framework":
            errors.append("Invalid platform header")

        if not manifest.get("model_serving_endpoint"):
            errors.append("model_serving_endpoint is required")
        if not manifest.get("system_prompt"):
            errors.append("system_prompt is required")
        if not manifest.get("mlflow_experiment"):
            errors.append("mlflow_experiment path is required")

        uc_tools = manifest.get("unity_catalog_tools", [])
        if not isinstance(uc_tools, list) or len(uc_tools) == 0:
            errors.append("unity_catalog_tools must be a non-empty list")
        else:
            for i, tool in enumerate(uc_tools):
                if not tool.get("catalog") or not tool.get("schema") or not tool.get("function_name"):
                    errors.append(f"unity_catalog_tools[{i}] must specify catalog, schema, and function_name")
                if not tool.get("description"):
                    errors.append(f"unity_catalog_tools[{i}] missing description")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "schema_doc": "Databricks Mosaic AI Agent Framework & Unity Catalog Tool Specification",
        }
