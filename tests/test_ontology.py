"""Unit tests for ontology metamodel and relationship validation rules."""

import unittest
from fde_workbench.domain.ontology import EntityTypeEnum, RelationTypeEnum, ONTOLOGY_METADATA
from fde_workbench.domain.relationships import is_valid_relationship, Relationship, ALLOWED_RELATIONSHIPS


class TestOntology(unittest.TestCase):

    def test_entity_types_count(self):
        """Must have exactly 24 domain entities representing operational reality."""
        self.assertEqual(len(EntityTypeEnum), 24)
        metadata_types = ONTOLOGY_METADATA["entity_types"]
        self.assertEqual(len(metadata_types), 24)

    def test_all_24_entities_documented(self):
        """Every entity type must have a rich description and Paraguayan context note."""
        definitions = ONTOLOGY_METADATA["entity_definitions"]
        for et in EntityTypeEnum:
            self.assertIn(et.value, definitions)
            self.assertTrue(len(definitions[et.value]["description"]) > 10)
            self.assertTrue(len(definitions[et.value]["paraguayan_context"]) > 10)

    def test_relationship_rules(self):
        """Check valid operational relationship triples."""
        self.assertTrue(is_valid_relationship(EntityTypeEnum.ORGANIZATION, RelationTypeEnum.OPERATES, EntityTypeEnum.FACILITY))
        self.assertTrue(is_valid_relationship(EntityTypeEnum.ORGANIZATION, RelationTypeEnum.BUYS_FROM, EntityTypeEnum.SUPPLIER))
        self.assertTrue(is_valid_relationship(EntityTypeEnum.ORGANIZATION, RelationTypeEnum.SELLS_TO, EntityTypeEnum.CUSTOMER))
        self.assertTrue(is_valid_relationship(EntityTypeEnum.ORDER, RelationTypeEnum.CONTAINS, EntityTypeEnum.PRODUCT))
        self.assertTrue(is_valid_relationship(EntityTypeEnum.ORDER, RelationTypeEnum.GENERATES, EntityTypeEnum.SHIPMENT))
        self.assertTrue(is_valid_relationship(EntityTypeEnum.SHIPMENT, RelationTypeEnum.TRANSPORTS, EntityTypeEnum.PRODUCT))
        self.assertTrue(is_valid_relationship(EntityTypeEnum.SHIPMENT, RelationTypeEnum.HANDLED_BY, EntityTypeEnum.CARRIER))
        self.assertTrue(is_valid_relationship(EntityTypeEnum.INVOICE, RelationTypeEnum.ASSOCIATED_WITH, EntityTypeEnum.ORDER))
        self.assertTrue(is_valid_relationship(EntityTypeEnum.PAYMENT, RelationTypeEnum.SETTLES, EntityTypeEnum.INVOICE))

    def test_invalid_relationship_rejected(self):
        """Invalid random connections should fail schema validation."""
        self.assertFalse(is_valid_relationship(EntityTypeEnum.CUSTOMER, RelationTypeEnum.CONSUMES, EntityTypeEnum.MACHINE))


if __name__ == "__main__":
    unittest.main()
