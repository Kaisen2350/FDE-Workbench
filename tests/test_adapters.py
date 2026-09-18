"""Unit tests for platform-agnostic agent specifications and schema-validated enterprise adapters."""

import unittest
from fde_workbench.domain.agent_specs import AgentSpecification, ToolDefinition
from fde_workbench.domain.ontology import EntityTypeEnum
from fde_workbench.domain.adapters import ADAPTERS


class TestAdapters(unittest.TestCase):

    def setUp(self):
        self.spec = AgentSpecification(
            spec_id="test-agent-spec",
            title="Customs Auto-Reconciliation Agent",
            objective="Reconcile VUE with ERP export invoices",
            trigger="On shipment ready",
            inputs=["SAP B1 Invoice", "VUE JSON"],
            entities=[EntityTypeEnum.SHIPMENT, EntityTypeEnum.CUSTOMS_DECLARATION],
            context="Mercosur cross-border trade",
            tools=[
                ToolDefinition(
                    name="query_vue",
                    description="Query customs VUE portal",
                    input_schema={"type": "object", "properties": {"decl_id": {"type": "string"}}},
                    read_only=True,
                )
            ],
            reasoning_requirements="Deterministic matching",
            human_approval_requirements="Customs broker sign-off",
            actions=["Issue Green Gate Pass", "Flag Discrepancy"],
            failure_modes=["API timeout"],
            evaluation_criteria=["100% NCM precision"],
            kpis=["Customs Dwell Hours"],
        )

    def test_all_enterprise_adapters_compile(self):
        platforms = ["gemini", "openai", "microsoft", "databricks"]
        for p in platforms:
            self.assertIn(p, ADAPTERS)
            adapter = ADAPTERS[p]
            manifest = adapter.export_manifest(self.spec)
            self.assertIsInstance(manifest, dict)
            self.assertIn("platform", manifest)

            compat = adapter.validate_compatibility(self.spec)
            self.assertTrue(compat["compatible"])
            self.assertTrue(compat["human_in_loop_enforced"])

    def test_gemini_vertex_schema_validation(self):
        adapter = ADAPTERS["gemini"]
        manifest = adapter.export_manifest(self.spec)
        val = adapter.validate_manifest_schema(manifest)
        self.assertTrue(val["valid"], f"Gemini schema errors: {val.get('errors')}")
        self.assertIn("Vertex AI", val["schema_doc"])

        # Test corrupt schema detection
        bad_manifest = dict(manifest)
        bad_manifest["agent_resource"] = {
            "display_name": "",
            "tools": [{"function_declarations": [{"name": "invalid name with spaces", "description": ""}]}]
        }
        bad_val = adapter.validate_manifest_schema(bad_manifest)
        self.assertFalse(bad_val["valid"])
        self.assertTrue(len(bad_val["errors"]) >= 2)

    def test_openai_assistants_schema_validation(self):
        adapter = ADAPTERS["openai"]
        manifest = adapter.export_manifest(self.spec)
        val = adapter.validate_manifest_schema(manifest)
        self.assertTrue(val["valid"], f"OpenAI schema errors: {val.get('errors')}")
        self.assertIn("OpenAI", val["schema_doc"])

        # Test corrupt schema detection
        bad_manifest = dict(manifest)
        bad_manifest["tools"] = [{"type": "wrong_type", "function": {"name": "bad"}}]
        bad_val = adapter.validate_manifest_schema(bad_manifest)
        self.assertFalse(bad_val["valid"])
        self.assertIn("must be 'function'", bad_val["errors"][0])

    def test_microsoft_semantic_kernel_schema_validation(self):
        adapter = ADAPTERS["microsoft"]
        manifest = adapter.export_manifest(self.spec)
        val = adapter.validate_manifest_schema(manifest)
        self.assertTrue(val["valid"], f"Microsoft schema errors: {val.get('errors')}")
        self.assertIn("Semantic Kernel", val["schema_doc"])

        # Test corrupt schema detection
        bad_manifest = dict(manifest)
        bad_manifest["agent_definition"] = {"id": "", "plugins": [{"plugin_name": ""}]}
        bad_val = adapter.validate_manifest_schema(bad_manifest)
        self.assertFalse(bad_val["valid"])

    def test_databricks_mosaic_schema_validation(self):
        adapter = ADAPTERS["databricks"]
        manifest = adapter.export_manifest(self.spec)
        val = adapter.validate_manifest_schema(manifest)
        self.assertTrue(val["valid"], f"Databricks schema errors: {val.get('errors')}")
        self.assertIn("Mosaic AI", val["schema_doc"])

        # Test corrupt schema detection
        bad_manifest = dict(manifest)
        bad_manifest["model_serving_endpoint"] = ""
        bad_val = adapter.validate_manifest_schema(bad_manifest)
        self.assertFalse(bad_val["valid"])


if __name__ == "__main__":
    unittest.main()
