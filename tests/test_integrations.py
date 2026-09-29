"""Unit tests for Messy Enterprise TMS Integration Connector."""

import unittest
from fde_workbench.integrations.legacy_connector import LegacyTMSConnector, MESSY_TMS_SAMPLE_CSV
from fde_workbench.domain.provenance import ProvenanceType


class TestIntegrations(unittest.TestCase):

    def test_mercosur_number_parsing(self):
        connector = LegacyTMSConnector()
        self.assertEqual(connector.parse_mercosur_number('"42.350,00"'), 42350.0)
        self.assertEqual(connector.parse_mercosur_number('12,4%'), 12.4)
        self.assertEqual(connector.parse_mercosur_number('"39.120,50"'), 39120.50)
        self.assertEqual(connector.parse_mercosur_number(''), 0.0)

    def test_latin_date_parsing(self):
        connector = LegacyTMSConnector()
        self.assertEqual(connector.parse_latin_date("23/09/2026"), "2026-09-23")
        self.assertEqual(connector.parse_latin_date("04/07/2026"), "2026-07-04")

    def test_messy_csv_normalization_and_anomalies(self):
        connector = LegacyTMSConnector()
        shipments, carriers, evidence, report = connector.process_csv_stream(MESSY_TMS_SAMPLE_CSV)

        self.assertEqual(report.total_raw_rows, 4)
        self.assertEqual(report.normalized_shipments, 4)
        self.assertEqual(report.evidence_records_created, 4)
        self.assertGreaterEqual(report.anomalies_detected, 2)  # Missing plate, high moisture

        # Check explicit provenance: default is SYNTHETIC for reference fixture
        for s in shipments:
            self.assertEqual(s.provenance, ProvenanceType.SYNTHETIC)
            self.assertIn("net_weight_kg", s.attributes)
            self.assertGreater(s.attributes["net_weight_kg"], 0)

        for e in evidence:
            self.assertEqual(e.provenance, ProvenanceType.SYNTHETIC)
            self.assertEqual(len(e.references_entity_ids), 2)

    def test_live_production_provenance_override(self):
        """In live on-site deployments, connector stamps ProvenanceType.CUSTOMER_OBSERVED."""
        connector = LegacyTMSConnector()
        shipments, carriers, evidence, report = connector.process_csv_stream(
            MESSY_TMS_SAMPLE_CSV, provenance=ProvenanceType.CUSTOMER_OBSERVED
        )
        for s in shipments:
            self.assertEqual(s.provenance, ProvenanceType.CUSTOMER_OBSERVED)
        for e in evidence:
            self.assertEqual(e.provenance, ProvenanceType.CUSTOMER_OBSERVED)


if __name__ == "__main__":
    unittest.main()
