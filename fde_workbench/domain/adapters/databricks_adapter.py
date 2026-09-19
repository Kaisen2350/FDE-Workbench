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
            "vendor_schema_url": "https://docs.databricks.com/en/generative-ai/agent-framework/create-agent.html",
        }

    def generate_pilot_deployment_plan(self, pilot: Any) -> Dict[str, Any]:
        """Generate Databricks Mosaic AI deployment architecture on the Lakehouse."""
        fn_name = "reconcile_customs_clearance_pack" if "customs" in pilot.pilot_id else "optimize_fluvial_convoy_draft"
        schema_name = "pilot_customs" if "customs" in pilot.pilot_id else "pilot_fluvial"
        return {
            "platform": self.platform_name,
            "platform_display_name": "Databricks Mosaic AI",
            "pilot_id": pilot.pilot_id,
            "customer": pilot.customer,
            "runtime_framework": "Databricks Mosaic AI Agent Framework + MLflow on Databricks Lakehouse",
            "model_deployment": "Databricks Model Serving: DBRX / Meta-Llama-3-70B-Instruct or Azure OpenAI endpoint",
            "architecture_pattern": "Lakehouse-native agent reading Delta Lake tables, executing Unity Catalog functions, logged to MLflow",
            "integration_steps": [
                f"1. Configure Unity Catalog catalog for {pilot.customer} (catalog 'aidesa_export', schema '{schema_name}')",
                f"2. Register Python tools as Unity Catalog SQL/Python user-defined functions with column-level permissions",
                f"3. Build Databricks Vector Search index over Delta table containing customs regulations and historical audits",
                f"4. Package agent using MLflow pyfunc with Databricks Review App enabled for {pilot.decision_owner} feedback",
                f"5. Deploy agent to Databricks Model Serving endpoint with autoscaling and token-based rate limits",
            ],
            "credentials_and_env": [
                "DATABRICKS_HOST=https://aidesa-workspace.cloud.databricks.com",
                "DATABRICKS_TOKEN=dapi-secrets://vault/databricks-token",
                "DATABRICKS_CATALOG=aidesa_export",
                f"DATABRICKS_SCHEMA={schema_name}",
            ],
            "human_in_loop_mechanism": f"Databricks Mosaic AI Review App + Lakehouse workflow gating. Mutations require row-level authorization approval from {pilot.decision_owner} in the operational Delta staging table.",
            "verification_command": "databricks clusters list --output JSON",
            "platform_manifest": {
                "platform": "Databricks Mosaic AI Agent Framework",
                "model_serving_endpoint": f"endpoint-{pilot.pilot_id}",
                "system_prompt": (
                    f"# OBJECTIVE: {pilot.decision}\n"
                    f"# OPERATIONAL CONTEXT: {pilot.workflow}\n"
                    f"# HUMAN GOVERNANCE: {pilot.human_approval_required}"
                ),
                "mlflow_experiment": f"/Shared/fde_pilots/{pilot.pilot_id}",
                "unity_catalog_tools": [
                    {
                        "catalog": "aidesa_export",
                        "schema": schema_name,
                        "function_name": fn_name,
                        "description": f"Unity Catalog registered operational tool for {pilot.decision}",
                        "read_only": False,
                    }
                ],
            },
        }

    def validate_deployment_plan_schema(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate deployment plan against Databricks Mosaic AI requirements."""
        result = super().validate_deployment_plan_schema(plan)
        errors = list(result.get("errors", []))

        creds = " ".join(plan.get("credentials_and_env", []))
        if "DATABRICKS" not in creds:
            errors.append("Databricks deployment plan must specify DATABRICKS_HOST or token")

        runtime = str(plan.get("runtime_framework", "")).lower()
        if "mosaic" not in runtime and "lakehouse" not in runtime:
            errors.append("Databricks deployment plan runtime_framework must reference Mosaic AI or Lakehouse")

        result["valid"] = len(errors) == 0
        result["errors"] = errors
        result["schema_doc"] = "Databricks Mosaic AI Deployment Plan Specification (Unity Catalog Tool Binding)"
        result["vendor_schema_url"] = "https://docs.databricks.com/en/generative-ai/agent-framework/create-agent.html"
        return result

