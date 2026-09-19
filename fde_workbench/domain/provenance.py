"""Provenance abstraction defining explicit data origins across the FDE workbench."""

from enum import Enum
from typing import Dict, Any


class ProvenanceType(str, Enum):
    """
    Explicit data origin categories.
    Ensures every fact, entity, event, and evidence answers:
    'Where did this fact come from?'
    """
    SYNTHETIC = "SYNTHETIC"
    CUSTOMER_OBSERVED = "CUSTOMER_OBSERVED"
    PUBLIC_SOURCE = "PUBLIC_SOURCE"
    CUSTOMER_PROVIDED = "CUSTOMER_PROVIDED"
    DERIVED = "DERIVED"


PROVENANCE_METADATA: Dict[str, Dict[str, Any]] = {
    ProvenanceType.SYNTHETIC.value: {
        "label": "Synthetic",
        "badge_color": "var(--rust)",
        "description": "Procedural data generated for workbench stress-testing and architectural exercises. Reflects real operational patterns without compromising customer privacy.",
        "reliability_weight": 0.50,
    },
    ProvenanceType.CUSTOMER_OBSERVED.value: {
        "label": "Customer Observed",
        "badge_color": "var(--green)",
        "description": "Observed on-site by the Forward Deployed Engineer during shadow shifts, physical plant walks, weighbridge inspections, or river barge loading.",
        "reliability_weight": 0.95,
    },
    ProvenanceType.PUBLIC_SOURCE.value: {
        "label": "Public Source",
        "badge_color": "var(--river-deep)",
        "description": "Authoritative government gazettes, DNIT tax portals, Prefectura Naval river hydrometric bulletins, DINATRAN decrees, or SENAVE regulatory resolutions.",
        "reliability_weight": 0.90,
    },
    ProvenanceType.CUSTOMER_PROVIDED.value: {
        "label": "Customer Provided",
        "badge_color": "var(--gold)",
        "description": "Provided directly by enterprise stakeholders (SAP B1 database extracts, Google Workspace spreadsheets, bill of lading PDFs, email threads, contracts).",
        "reliability_weight": 0.85,
    },
    ProvenanceType.DERIVED.value: {
        "label": "Derived",
        "badge_color": "var(--ink-light)",
        "description": "Computed or inferred by workbench analytical logic (e.g. cross-document reconciliation diffs, cash conversion cycle deltas, draft grounding margins).",
        "reliability_weight": 0.80,
    },
}
