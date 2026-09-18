"""Unit tests verifying all 24 Pydantic domain entity schemas."""

import unittest
from datetime import datetime
from fde_workbench.domain.ontology import EntityTypeEnum
from fde_workbench.domain.entities import (
    ENTITY_TYPE_TO_CLASS,
    Organization,
    Facility,
    Supplier,
    Customer,
    Product,
    Material,
    Order,
    PurchaseOrder,
    Shipment,
    Carrier,
    Warehouse,
    Invoice,
    Payment,
    Contract,
    Document,
    CustomsDeclaration,
    RegulatoryObligation,
    EmployeeRole,
    Machine,
    ProductionBatch,
    QualityEvent,
    OperationalEvent,
    Decision,
    KPI,
)


class TestEntities(unittest.TestCase):

    def test_all_24_entity_classes_exist(self):
        self.assertEqual(len(ENTITY_TYPE_TO_CLASS), 24)
        for et, cls in ENTITY_TYPE_TO_CLASS.items():
            instance = cls(id=f"test-{et.value}", name=f"Test {et.value}")
            self.assertEqual(instance.entity_type, et)
            self.assertEqual(instance.version, 1)

    def test_paraguayan_specific_attributes(self):
        org = Organization(id="org-test", name="Test Agro", ruc="80012345-1", export_regime="Maquila Ley 1064")
        self.assertEqual(org.ruc, "80012345-1")

        fac = Facility(id="fac-test", name="Planta Villeta", port_code="PYVIL", has_barge_dock=True)
        self.assertTrue(fac.has_barge_dock)

        customs = CustomsDeclaration(id="cdec-test", name="MIC/DTA", declaration_type="MIC_DTA", inspection_channel="VERDE")
        self.assertEqual(customs.inspection_channel, "VERDE")


if __name__ == "__main__":
    unittest.main()
