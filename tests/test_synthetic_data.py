"""Unit tests verifying synthetic Paraguayan export company (AIDESA)."""

import unittest
from fde_workbench.storage.store import WorkbenchStore
from fde_workbench.domain.ontology import EntityTypeEnum
from fde_workbench.synthetic.generator import seed_synthetic_company


class TestSyntheticData(unittest.TestCase):

    def setUp(self):
        self.store = WorkbenchStore()
        self.summary = seed_synthetic_company(self.store)

    def test_synthetic_company_constraints(self):
        # 1. 250 employees
        roles = self.store.list_entities(entity_type=EntityTypeEnum.EMPLOYEE_ROLE)
        total_headcount = sum(getattr(r, "headcount_in_role", 0) for r in roles)
        self.assertEqual(total_headcount, 250)
        self.assertEqual(self.summary["headcount"], 250)

        # 2. 2 facilities
        facilities = self.store.list_entities(entity_type=EntityTypeEnum.FACILITY)
        self.assertEqual(len(facilities), 2)
        fac_ids = {f.id for f in facilities}
        self.assertIn("fac-villeta", fac_ids)
        self.assertIn("fac-hernandarias", fac_ids)

        # 3. Approximately 80 suppliers (exactly 80)
        suppliers = self.store.list_entities(entity_type=EntityTypeEnum.SUPPLIER)
        self.assertEqual(len(suppliers), 80)

        # 4. Approximately 25 customers (exactly 25)
        customers = self.store.list_entities(entity_type=EntityTypeEnum.CUSTOMER)
        self.assertEqual(len(customers), 25)

        # 5. Exports to Brazil and Argentina
        customer_countries = {c.country for c in customers}
        self.assertIn("Brazil", customer_countries)
        self.assertIn("Argentina", customer_countries)

        # 6. Events and Decisions
        self.assertTrue(len(self.store.list_events()) >= 4)
        self.assertTrue(len(self.store.list_decisions()) >= 2)

        # 7. AI Opportunities & Agent Specs
        self.assertTrue(len(self.store.list_opportunities()) >= 3)
        self.assertTrue(len(self.store.list_agent_specs()) >= 2)

        # 8. KPIs
        self.assertTrue(len(self.store.list_kpis()) >= 5)


if __name__ == "__main__":
    unittest.main()
