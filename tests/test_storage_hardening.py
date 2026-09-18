"""Unit tests for SQLite persistence and tamper-evident audit hash-chain."""

import unittest
import tempfile
import os
import sqlite3
from fde_workbench.storage.store import WorkbenchStore
from fde_workbench.domain.ontology import EntityTypeEnum
from fde_workbench.domain.entities import Organization, Facility
from fde_workbench.domain.relationships import Relationship, RelationTypeEnum


class TestStorageHardening(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.store = WorkbenchStore(db_path=self.temp_db.name)

    def tearDown(self):
        try:
            self.store._conn.close()
            if os.path.exists(self.temp_db.name):
                os.remove(self.temp_db.name)
        except Exception:
            pass

    def test_sqlite_persistence_across_instances(self):
        """Verify data written by store instance 1 survives and is readable by store instance 2."""
        org = Organization(id="org-persist-test", name="Persist Test Org", ruc="80099999-1")
        fac = Facility(id="fac-persist-test", name="Persist Test Facility", city="Villeta")
        self.store.add_entity(org)
        self.store.add_entity(fac)
        self.store.add_relationship(Relationship(
            id="rel-test-persist",
            relation_type=RelationTypeEnum.OPERATES,
            source_id=org.id,
            source_type=EntityTypeEnum.ORGANIZATION,
            target_id=fac.id,
            target_type=EntityTypeEnum.FACILITY,
        ))

        # Close first instance
        self.store._conn.close()

        # Open second instance pointing to the same file
        store2 = WorkbenchStore(db_path=self.temp_db.name)
        fetched_org = store2.get_entity("org-persist-test")
        fetched_fac = store2.get_entity("fac-persist-test")
        fetched_rel = store2.get_relationship("rel-test-persist")

        self.assertIsNotNone(fetched_org)
        self.assertEqual(fetched_org.name, "Persist Test Org")
        self.assertEqual(fetched_org.ruc, "80099999-1")
        self.assertIsNotNone(fetched_fac)
        self.assertIsNotNone(fetched_rel)
        self.assertEqual(fetched_rel.relation_type, RelationTypeEnum.OPERATES)
        store2._conn.close()

    def test_audit_hash_chain_validity(self):
        """Verify valid hash-chain verification when no tampering has occurred."""
        self.store.add_entity(Organization(id="org-1", name="Org 1"))
        self.store.add_entity(Facility(id="fac-1", name="Fac 1"))
        self.store.delete_entity("fac-1")

        result = self.store.verify_audit_chain()
        self.assertTrue(result["valid"])
        self.assertGreaterEqual(result["total_entries"], 3)
        self.assertIsNotNone(result["head_hash"])

    def test_audit_hash_chain_tamper_detection(self):
        """Verify that any tampering directly in the SQLite audit_log table is flagged."""
        self.store.add_entity(Organization(id="org-tamper-1", name="Org 1"))
        self.store.add_entity(Facility(id="fac-tamper-2", name="Fac 2"))
        self.store.add_entity(Facility(id="fac-tamper-3", name="Fac 3"))

        # Chain must be valid initially
        self.assertTrue(self.store.verify_audit_chain()["valid"])

        # Tamper directly with the SQLite database row for sequence 2
        with self.store._conn:
            cursor = self.store._conn.cursor()
            cursor.execute("""
                UPDATE audit_log
                SET details_json = '{"name":"FORGED_MODIFICATION","type":"facility"}'
                WHERE sequence = 2;
            """)

        # Now verify_audit_chain MUST detect tampering and flag sequence 2
        tamper_check = self.store.verify_audit_chain()
        self.assertFalse(tamper_check["valid"])
        self.assertEqual(tamper_check["corrupted_sequence"], 2)
        self.assertIn("Tampered entry_hash", tamper_check["reason"])


if __name__ == "__main__":
    unittest.main()
