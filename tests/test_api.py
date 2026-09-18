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


if __name__ == "__main__":
    unittest.main()
