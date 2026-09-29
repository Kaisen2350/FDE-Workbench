"""Enterprise Integration Connectors for Legacy & Messy Systems.

Normalizes legacy CSVs, non-standard ERP exports, and localized TMS telemetry
into canonical Pydantic ontology entities with explicit provenance.
"""

from .legacy_connector import LegacyTMSConnector, IngestionReport

__all__ = ["LegacyTMSConnector", "IngestionReport"]
