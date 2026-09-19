"""Unit tests for Source Evidence abstraction, provenance tracking, and persistence."""

import unittest
from datetime import datetime
from fde_workbench.domain.provenance import ProvenanceType
from fde_workbench.domain.evidence import EvidenceRecord, EvidenceSourceType
from fde_workbench.domain.events import OperationalEventRecord, EventSeverity, EventStatus
from fde_workbench.domain.ontology import EntityTypeEnum
from fde_workbench.storage.store import WorkbenchStore
from fde_workbench.storage.snapshot import export_store_to_dict, import_store_from_dict


class TestEvidence(unittest.TestCase):

    def setUp(self):
        # Use an in-memory SQLite database for test isolation
        self.store = WorkbenchStore(db_path=":memory:")

    def test_evidence_creation_and_attributes(self):
        evidence = EvidenceRecord(
            id="evi-test-001",
            source="PREFECTURA_NAVAL_GAUGE",
            source_type=EvidenceSourceType.TELEMETRY_STREAM,
            timestamp=datetime.utcnow(),
            confidence=0.98,
            provenance=ProvenanceType.PUBLIC_SOURCE,
            extracted_claim="Paraguay River water level at Paso Queso gauge measured 8.4 ft, below 10.0 ft threshold.",
            raw_payload_snippet="GAUGE_ID: PQ-1590 | LEVEL_FT: 8.42 | STATUS: RESTRICTED",
            references_entity_ids=["fac-villeta", "ship-001"],
            references_event_ids=["evt-001"],
            references_decision_ids=["dec-001"],
        )
        self.assertEqual(evidence.id, "evi-test-001")
        self.assertEqual(evidence.source_type, EvidenceSourceType.TELEMETRY_STREAM)
        self.assertEqual(evidence.provenance, ProvenanceType.PUBLIC_SOURCE)
        self.assertAlmostEqual(evidence.confidence, 0.98)

    def test_evidence_sqlite_store_crud(self):
        evidence = EvidenceRecord(
            id="evi-test-002",
            source="SAP_B1_WEIGHBRIDGE_LOG",
            source_type=EvidenceSourceType.ERP_RECORD,
            confidence=0.95,
            provenance=ProvenanceType.CUSTOMER_PROVIDED,
            extracted_claim="Weighbridge grain assay ticket recorded 15.7% moisture against 14.0% contract threshold.",
            references_entity_ids=["mat-soybean"],
        )
        saved = self.store.add_evidence(evidence)
        self.assertEqual(saved.id, "evi-test-002")

        fetched = self.store.get_evidence("evi-test-002")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.extracted_claim, evidence.extracted_claim)
        self.assertEqual(fetched.provenance, ProvenanceType.CUSTOMER_PROVIDED)

        # Listing and filtering
        all_evi = self.store.list_evidence()
        self.assertEqual(len(all_evi), 1)

        erp_evi = self.store.list_evidence(source_type=EvidenceSourceType.ERP_RECORD)
        self.assertEqual(len(erp_evi), 1)

        cust_evi = self.store.list_evidence(provenance=ProvenanceType.CUSTOMER_PROVIDED)
        self.assertEqual(len(cust_evi), 1)

        synth_evi = self.store.list_evidence(provenance=ProvenanceType.SYNTHETIC)
        self.assertEqual(len(synth_evi), 0)

        # Count
        self.assertEqual(self.store.count_evidence(), 1)
        self.assertEqual(self.store.count_evidence(source_type=EvidenceSourceType.ERP_RECORD), 1)

        # Audit log verification
        audit = self.store.get_audit_trail(limit=5)
        self.assertTrue(any(a["action"] == "RECORD_EVIDENCE" for a in audit))
        chain_status = self.store.verify_audit_chain()
        self.assertTrue(chain_status["valid"])

        # Delete
        self.assertTrue(self.store.delete_evidence("evi-test-002"))
        self.assertEqual(self.store.count_evidence(), 0)

    def test_evidence_supported_event_flow(self):
        evidence = EvidenceRecord(
            id="evi-test-003",
            source="VUE_PORTAL_RECEIPT",
            source_type=EvidenceSourceType.CUSTOMS_DOCUMENT,
            confidence=0.99,
            provenance=ProvenanceType.PUBLIC_SOURCE,
            extracted_claim="Customs transit clearance MIC/DTA rejected due to missing carrier tax stamp.",
        )
        self.store.add_evidence(evidence)

        # Create operational event grounded in this evidence
        event = OperationalEventRecord(
            id="evt-test-003",
            entity_id="cdec-001",
            entity_type=EntityTypeEnum.CUSTOMS_DECLARATION,
            event_type="customs_document_missing",
            source="VUE_PORTAL",
            provenance=ProvenanceType.PUBLIC_SOURCE,
            evidence_ids=[evidence.id],
            operational_impact="Truck convoy halted at border bridge awaiting re-filing.",
            financial_impact=4200.0,
            required_decision="EXPEDITE_CUSTOMS",
        )
        self.store.add_event(event)

        fetched_evt = self.store.get_event("evt-test-003")
        self.assertIn(evidence.id, fetched_evt.evidence_ids)
        self.assertEqual(fetched_evt.provenance, ProvenanceType.PUBLIC_SOURCE)

    def test_snapshot_export_import_with_evidence(self):
        evidence = EvidenceRecord(
            id="evi-snapshot-01",
            source="INTERVIEW_TRANSCRIPT",
            source_type=EvidenceSourceType.INTERVIEW_STATEMENT,
            confidence=0.85,
            provenance=ProvenanceType.CUSTOMER_OBSERVED,
            extracted_claim="Logistics director stated that weekend river draft alerts take 6 hours to propagate to pilots.",
        )
        self.store.add_evidence(evidence)

        snapshot_dict = export_store_to_dict(self.store)
        self.assertIn("evidence", snapshot_dict)
        self.assertEqual(len(snapshot_dict["evidence"]), 1)

        # Import into fresh store
        new_store = WorkbenchStore(db_path=":memory:")
        import_store_from_dict(new_store, snapshot_dict)
        self.assertEqual(new_store.count_evidence(), 1)
        imported_evi = new_store.get_evidence("evi-snapshot-01")
        self.assertIsNotNone(imported_evi)
        self.assertEqual(imported_evi.provenance, ProvenanceType.CUSTOMER_OBSERVED)


if __name__ == "__main__":
    unittest.main()
