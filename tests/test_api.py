"""Unit tests for FastAPI REST API endpoints."""

import unittest
from fastapi.testclient import TestClient
from fde_workbench.api.app import app, store
from fde_workbench.synthetic.generator import seed_synthetic_company


class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed_synthetic_company(store)
        cls.client = TestClient(app)

    def test_get_ontology(self):
        res = self.client.get("/api/ontology")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("metadata", data)
        self.assertEqual(len(data["metadata"]["entity_types"]), 24)
        self.assertIn("critical_path_narrative", data)
        self.assertEqual(len(data["critical_path_narrative"]), 6)

    def test_verify_audit_trail(self):
        res = self.client.get("/api/audit/verify")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["valid"])
        self.assertGreater(data["total_entries"], 0)
        self.assertIn("head_hash", data)

    def test_list_entities(self):
        res = self.client.get("/api/entities?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total_overall"], 100)
        self.assertEqual(len(data["entities"]), 10)

    def test_filter_entities_by_type(self):
        res = self.client.get("/api/entities?type=facility")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["entities"]), 2)

    def test_get_entity_detail(self):
        res = self.client.get("/api/entities/org-aidesa")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["entity"]["id"], "org-aidesa")
        self.assertTrue(len(data["outgoing_relationships"]) > 0)

    def test_list_relationships(self):
        res = self.client.get("/api/relationships?limit=20")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["relationships"]), 20)

    def test_list_events(self):
        res = self.client.get("/api/events")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data["events"]) >= 4)

    def test_list_decisions(self):
        res = self.client.get("/api/decisions")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data["decisions"]) >= 2)
        # Check pipeline stages included
        dec = data["decisions"][0]
        self.assertIn("pipeline_stages", dec)
        self.assertEqual(len(dec["pipeline_stages"]), 5)

    def test_list_workflows(self):
        res = self.client.get("/api/workflows")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data["workflows"]) >= 2)

    def test_list_opportunities(self):
        res = self.client.get("/api/opportunities")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data["opportunities"]) >= 3)

    def test_list_agent_specs_and_compile(self):
        res = self.client.get("/api/agent-specs")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data["agent_specifications"]) >= 2)
        spec_id = data["agent_specifications"][0]["spec_id"]

        # Compile for Gemini
        res_gemini = self.client.get(f"/api/agent-specs/{spec_id}/export/gemini")
        self.assertEqual(res_gemini.status_code, 200)
        self.assertIn("agent_resource", res_gemini.json()["manifest"])

        # Compile for OpenAI
        res_openai = self.client.get(f"/api/agent-specs/{spec_id}/export/openai")
        self.assertEqual(res_openai.status_code, 200)
        self.assertIn("tools", res_openai.json()["manifest"])

    def test_get_kpis(self):
        res = self.client.get("/api/kpis")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data["kpis"]) >= 5)

    def test_get_company(self):
        res = self.client.get("/api/company")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["headcount"], 250)
        self.assertEqual(len(data["facilities"]), 2)
        self.assertEqual(data["supplier_count"], 80)
        self.assertEqual(data["customer_count"], 25)

    def test_snapshot_export(self):
        res = self.client.get("/api/snapshot/export")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("entities", data)
        self.assertIn("relationships", data)

    def test_ui_index(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Paraguay Export Economy", res.text)

    def test_list_and_get_evidence(self):
        res = self.client.get("/api/evidence")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["total"] >= 5)
        first_id = data["evidence"][0]["id"]

        res_detail = self.client.get(f"/api/evidence/{first_id}")
        self.assertEqual(res_detail.status_code, 200)
        self.assertEqual(res_detail.json()["evidence"]["id"], first_id)

    def test_get_discovery_intake(self):
        res = self.client.get("/api/discovery/intake")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("company_profile", data)
        self.assertIn("critical_workflows", data)
        self.assertIn("known_bottlenecks", data)

    def test_gemini_python_scaffold_endpoint(self):
        specs_res = self.client.get("/api/agent-specs")
        spec_id = specs_res.json()["agent_specifications"][0]["spec_id"]

        res = self.client.get(f"/api/agent-specs/{spec_id}/scaffold/gemini")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("python_scaffold", data)
        self.assertIn("google.genai", data["python_scaffold"])

    def test_get_critical_path_endpoint(self):
        res = self.client.get("/api/ontology/critical-path")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("narrative", data)
        self.assertIn("critical_entity_types", data)
        self.assertIn("spine", data)
        self.assertIn("entities", data)
        self.assertGreater(len(data["entities"]), 0)

    def test_filter_entities_critical_path(self):
        res_all = self.client.get("/api/entities")
        total_all = res_all.json()["count"]

        res_crit = self.client.get("/api/entities?critical_path=true")
        self.assertEqual(res_crit.status_code, 200)
        data_crit = res_crit.json()
        self.assertTrue(data_crit["critical_path_filtered"])
        self.assertLess(data_crit["count"], total_all)
        # Verify all returned entities belong to critical path types
        crit_types = {"order", "shipment", "customs_declaration", "operational_event", "decision"}
        for ent in data_crit["entities"]:
            self.assertIn(ent["entity_type"], crit_types)

    def test_escalate_decision_endpoint(self):
        decisions_res = self.client.get("/api/decisions")
        dec_id = decisions_res.json()["decisions"][0]["decision_id"]

        res = self.client.post(f"/api/decisions/{dec_id}/escalate", json={
            "escalated_to": "role-managing-director",
            "reason": "Test executive escalation",
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ESCALATED")
        self.assertEqual(data["decision"]["status"], "ESCALATED")
        self.assertEqual(data["decision"]["escalation_target_role"], "role-managing-director")

    def test_check_decision_escalations_endpoint(self):
        res = self.client.post("/api/decisions/check-escalations")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("escalated_count", data)
        self.assertGreaterEqual(data["escalated_count"], 1)
        self.assertEqual(data["trigger_model"], "on_demand_or_scheduled_sweep")
        self.assertIn("dec-2026-005-escalated", [d["decision_id"] for d in data["escalated_decisions"]])


if __name__ == "__main__":
    unittest.main()

