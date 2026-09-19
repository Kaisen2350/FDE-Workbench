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

    def test_all_adapters_deployment_plan_schema_validation(self):
        """Verify that validate_deployment_plan_schema validates plans for all 4 platforms."""
        from fde_workbench.domain.pilots import PilotSpecification, PilotEconomicModel
        mock_pilot = PilotSpecification(
            pilot_id="test-pilot-01",
            opportunity_id="opp-test",
            agent_spec_id="test-agent",
            title="Test Customs Clearance Pilot",
            customer="Agro-Industrial del Este S.A. (AIDESA)",
            workflow="Customs clearance",
            decision="Authorize dispatch",
            decision_owner="Head of Customs",
            baseline_kpi={"error_rate": 5.0},
            target_kpi={"error_rate": 1.0},
            measurement_method="Audit logs",
            data_sources=["SAP B1"],
            required_integrations=["SAP B1 API"],
            trigger="Truck ready",
            inputs=["Invoice"],
            context="Cross border export",
            recommended_action="Pre-validate clearance",
            human_approval_required="Operator must sign off",
            authorized_actions=["Generate pack"],
            supported_platforms=["gemini_enterprise", "microsoft_azure_ai_foundry", "openai_assistants", "databricks_mosaic_ai"],
            selected_platform="gemini_enterprise",
            pilot_duration="30 days",
            pilot_scope="100 trucks",
            failure_modes=["OCR failure"],
            rollback_condition="Pause on 2 failures",
            safety_constraints=["Read-only"],
            acceptance_criteria=["Zero error"],
            economic_model=PilotEconomicModel(
                annual_decision_volume=1000,
                manual_effort_minutes_per_decision=15.0,
                current_error_or_exception_rate=0.05,
                cost_per_exception_usd=500.0,
                target_manual_effort_minutes=3.0,
                target_exception_rate=0.01,
            ),
            implementation_effort="2 weeks",
            deployment_dependencies=["API key"],
            expansion_path="Scale to other ports and customs posts",
        )

        for p_name in ["gemini", "microsoft", "openai", "databricks"]:
            adapter = ADAPTERS[p_name]
            plan = adapter.generate_pilot_deployment_plan(mock_pilot)
            val = adapter.validate_deployment_plan_schema(plan)
            self.assertTrue(val["valid"], f"Plan validation failed for {p_name}: {val.get('errors')}")
            self.assertEqual(len(val["errors"]), 0)
            self.assertIn("vendor_schema_status", val)
            self.assertIn("infrastructure_schema_status", val)
            self.assertIn("platform_manifest", plan)

        # Test broken plan
        broken_plan = {"platform": "invalid_platform"}
        bad_val = ADAPTERS["gemini"].validate_deployment_plan_schema(broken_plan)
        self.assertFalse(bad_val["valid"])
        self.assertGreaterEqual(len(bad_val["errors"]), 3)

    def test_canonical_public_vendor_schemas_verification(self):
        """
        Verify that each adapter validates against canonical schemas pulled directly
        from official vendor public documentation, and detects real-world schema violations.
        """
        # --- 1. Google Cloud Vertex AI FunctionDeclaration ---
        # Spec: https://cloud.google.com/vertex-ai/docs/reference/rest/v1beta1/Tool#FunctionDeclaration
        gemini = ADAPTERS["gemini"]
        canonical_vertex_manifest = {
            "platform": "Google Cloud Vertex AI / Gemini Enterprise",
            "spec_version": "v1beta",
            "agent_resource": {
                "display_name": "VertexAICanonicalAgent",
                "instruction": {"system_instruction": {"parts": [{"text": "You are a customs officer"}]}},
                "tools": [
                    {
                        "function_declarations": [
                            {
                                "name": "get_current_weather",
                                "description": "Get current weather in given location",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "location": {"type": "string", "description": "City and state"}
                                    },
                                    "required": ["location"]
                                }
                            }
                        ]
                    }
                ]
            }
        }
        val_gemini = gemini.validate_manifest_schema(canonical_vertex_manifest)
        self.assertTrue(val_gemini["valid"], f"Canonical Vertex AI manifest failed: {val_gemini.get('errors')}")

        # Negative test: Name violates Vertex AI naming regex '^[a-zA-Z0-9_-]{1,64}$'
        bad_vertex = dict(canonical_vertex_manifest)
        bad_vertex["agent_resource"]["tools"][0]["function_declarations"][0]["name"] = "invalid name with spaces!"
        self.assertFalse(gemini.validate_manifest_schema(bad_vertex)["valid"])

        # --- 2. OpenAI Assistants API v2 Strict Function Calling ---
        # Spec: https://platform.openai.com/docs/api-reference/assistants/createAssistant#assistants-createassistant-tools
        openai_adapter = ADAPTERS["openai"]
        canonical_openai_manifest = {
            "platform": "OpenAI Assistants API",
            "name": "OpenAICanonicalAssistant",
            "instructions": "You are a helpful assistant.",
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Determine weather in my location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {"type": "string", "description": "The city and state"}
                            },
                            "required": ["location"],
                            "additionalProperties": False
                        },
                        "strict": True
                    }
                }
            ]
        }
        val_openai = openai_adapter.validate_manifest_schema(canonical_openai_manifest)
        self.assertTrue(val_openai["valid"], f"Canonical OpenAI manifest failed: {val_openai.get('errors')}")

        # Negative test: strict: true requires additionalProperties: False
        bad_openai = dict(canonical_openai_manifest)
        bad_openai["tools"][0]["function"]["parameters"]["additionalProperties"] = True
        self.assertFalse(openai_adapter.validate_manifest_schema(bad_openai)["valid"])

        # --- 3. Microsoft Semantic Kernel Plugin Manifest ---
        # Spec: https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/
        ms_adapter = ADAPTERS["microsoft"]
        canonical_ms_manifest = {
            "platform": "Microsoft Azure AI Foundry / Semantic Kernel",
            "agent_definition": {
                "id": "sk-agent-001",
                "displayName": "SemanticKernelCanonicalAgent",
                "promptTemplate": "<system>You are a foreign trade specialist</system>",
                "plugins": [
                    {
                        "plugin_name": "WeatherPlugin",
                        "description": "Provides weather telemetry for barge convoys",
                        "schema": {"type": "object", "properties": {"lat": {"type": "number"}}},
                        "execution_policy": "RequiresConsent"
                    }
                ]
            }
        }
        val_ms = ms_adapter.validate_manifest_schema(canonical_ms_manifest)
        self.assertTrue(val_ms["valid"], f"Canonical Semantic Kernel manifest failed: {val_ms.get('errors')}")

        # Negative test: invalid execution policy
        bad_ms = dict(canonical_ms_manifest)
        bad_ms["agent_definition"]["plugins"][0]["execution_policy"] = "UncontrolledExecution"
        self.assertFalse(ms_adapter.validate_manifest_schema(bad_ms)["valid"])

        # --- 4. Databricks Mosaic AI & Unity Catalog Tool Binding ---
        # Spec: https://docs.databricks.com/en/generative-ai/agent-framework/create-agent.html
        db_adapter = ADAPTERS["databricks"]
        canonical_db_manifest = {
            "platform": "Databricks Mosaic AI Agent Framework",
            "model_serving_endpoint": "endpoint-dbrx-customs",
            "system_prompt": "You are a Databricks Lakehouse agent.",
            "mlflow_experiment": "/Shared/fde_pilots/customs_agent",
            "unity_catalog_tools": [
                {
                    "catalog": "main_catalog",
                    "schema": "customs_schema",
                    "function_name": "check_tariff_code",
                    "description": "SQL UDF in Unity Catalog checking Mercosur NCM tariffs",
                    "read_only": True
                }
            ]
        }
        val_db = db_adapter.validate_manifest_schema(canonical_db_manifest)
        self.assertTrue(val_db["valid"], f"Canonical Databricks manifest failed: {val_db.get('errors')}")

        # Negative test: missing 3-tier catalog namespace
        bad_db = dict(canonical_db_manifest)
        bad_db["unity_catalog_tools"][0]["catalog"] = ""
        self.assertFalse(db_adapter.validate_manifest_schema(bad_db)["valid"])


if __name__ == "__main__":

    unittest.main()
