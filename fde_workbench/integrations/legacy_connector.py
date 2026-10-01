"""Legacy TMS & Messy Enterprise CSV Connector.

Demonstrates the essential FDE capability: writing connective tissue between
AI systems and messy, legacy enterprise data silos.

Handles:
- Spanish/Mercosur number formatting ("27.450,50" -> 27450.50)
- Latin date conventions ("29/09/2026" -> "2026-09-29")
- Mixed / noisy string delimiters and trailing whitespace
- Extraction of truck plates, carrier identities, and moisture metrics
- Normalization into canonical 24-entity ontology with explicit ProvenanceType
"""

import csv
import io
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from fde_workbench.domain.provenance import ProvenanceType
from fde_workbench.domain.evidence import EvidenceRecord, EvidenceSourceType
from fde_workbench.domain.entities import Shipment, Carrier


class IngestionReport(BaseModel):
    total_raw_rows: int
    normalized_shipments: int
    normalized_carriers: int
    evidence_records_created: int
    anomalies_detected: int
    anomaly_details: List[str] = Field(default_factory=list)


# Synthetic Demonstration Fixture: Modeled to simulate legacy Windows XP-era CSV parsing.
# ALL DATA IN THIS FIXTURE IS FULLY SYNTHETIC BY CONSTRUCTION (DoD Invariant 8).
# Zero real customer, driver, vehicle plate, or proprietary data is committed to this repository.
MESSY_TMS_SAMPLE_CSV = """NRO_DESPACHO;FECHA_SALIDA;TRANSPORTISTA_RAZON;CHOFER_Y_CHAPA;PRODUCTO_DESC;PESO_BRUTO_KG;TARA_KG;HUMEDAD_PCT;DESTINO_FINAL
DSP-SYN-8801;23/09/2026;TRANSPORTADORA SYNTHETIC SUR S.A.;CHOFER FICTICIO ALPHA (CHAPA SYN-991 / REMOLQUE 102);HARINA DE SOJA PELLETS 46.5%;"42.350,00";"15.330,00";12,4%;FOZ DO IGUACU - BR
DSP-SYN-8802;23/09/2026;LOGISTICA MOCK MERCOSUR S.A.;CHOFER FICTICIO BETA (CHAPA SYN-442);ACEITE CRUDO DE SOJA EN FLEXITANK;"39.120,50";"14.100,00";0,2%;PARANAGUA - BR
DSP-SYN-8803;24/09/2026;TRANS-DEMO TERRESTRE S.A.;;HARINA DE SOJA PELLETS 46.5%;"41.800,00";"15.100,00";14,8%;FOZ DO IGUACU - BR
DSP-SYN-8804;24/09/2026;FLETES SIMULADOS GUARANI S.A.;CHOFER FICTICIO GAMMA (CHAPA SYN-119);"";"38.500,00";"14.000,00";11,9%;SANTA FE - AR
"""



class LegacyTMSConnector:
    """Connective tissue normalizing messy field CSVs into typed ontology entities."""

    @staticmethod
    def parse_mercosur_number(val: str) -> float:
        """Converts Latin numbers like '42.350,00' or '12,4%' to float."""
        if not val or not val.strip():
            return 0.0
        cleaned = val.strip().replace('"', '').replace('%', '').strip()
        cleaned = cleaned.replace('.', '').replace(',', '.')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    @staticmethod
    def parse_latin_date(val: str) -> str:
        """Converts 'DD/MM/YYYY' to ISO format 'YYYY-MM-DD'."""
        if not val or not val.strip():
            return datetime.utcnow().strftime("%Y-%m-%d")
        try:
            dt = datetime.strptime(val.strip(), "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return val.strip()

    def process_csv_stream(
        self,
        csv_content: str,
        provenance: ProvenanceType = ProvenanceType.SYNTHETIC,
    ):
        """Processes and normalizes raw TMS CSV stream.

        Args:
            csv_content: Raw CSV text stream.
            provenance: Data origin classification. Defaults to ProvenanceType.SYNTHETIC
                for reference fixtures modeled after legacy enterprise systems. In live
                deployments, set to ProvenanceType.CUSTOMER_OBSERVED upon direct terminal read.
        """
        reader = csv.DictReader(io.StringIO(csv_content), delimiter=';')
        
        shipments: List[Shipment] = []
        carriers_dict: Dict[str, Carrier] = {}
        evidence_records: List[EvidenceRecord] = []
        anomalies: List[str] = []
        row_count = 0

        for row in reader:
            row_count += 1
            dispatch_id = row.get("NRO_DESPACHO", "").strip()
            raw_date = row.get("FECHA_SALIDA", "").strip()
            raw_carrier = row.get("TRANSPORTISTA_RAZON", "").strip()
            raw_driver_plate = row.get("CHOFER_Y_CHAPA", "").strip()
            raw_product = row.get("PRODUCTO_DESC", "").strip()
            raw_gross = row.get("PESO_BRUTO_KG", "")
            raw_tare = row.get("TARA_KG", "")
            raw_moisture = row.get("HUMEDAD_PCT", "")
            raw_destination = row.get("DESTINO_FINAL", "").strip()

            # Anomaly checks
            if not raw_product:
                anomalies.append(f"Row {row_count} ({dispatch_id}): Missing product description")
            if not raw_driver_plate:
                anomalies.append(f"Row {row_count} ({dispatch_id}): Missing driver and license plate")

            # Parse numbers & dates
            gross_kg = self.parse_mercosur_number(raw_gross)
            tare_kg = self.parse_mercosur_number(raw_tare)
            net_kg = max(0.0, gross_kg - tare_kg)
            net_tons = round(net_kg / 1000.0, 3)
            moisture_pct = self.parse_mercosur_number(raw_moisture)
            iso_date = self.parse_latin_date(raw_date)

            if moisture_pct > 14.0:
                anomalies.append(f"Row {row_count} ({dispatch_id}): High moisture alert ({moisture_pct}% > 14.0%)")

            plate_match = re.search(r'CHAPA\s+([A-Z0-9-]+)', raw_driver_plate)
            plate = plate_match.group(1) if plate_match else "UNKNOWN"

            # Create Carrier entity
            carrier_id = f"car-{re.sub(r'[^a-zA-Z0-9]', '', raw_carrier)[:12].lower()}" if raw_carrier else "car-unspecified"
            if carrier_id not in carriers_dict and raw_carrier:
                carriers_dict[carrier_id] = Carrier(
                    id=carrier_id,
                    name=raw_carrier,
                    transport_mode="TERRESTRIAL",
                    fleet_size=15,
                    provenance=provenance,
                    attributes={"active_fleets": ["bitren", "granelero"]},
                )

            # Create Shipment entity
            shipment = Shipment(
                id=f"shp-tms-{dispatch_id.lower()}",
                name=f"Dispatch {dispatch_id} ({raw_product or 'UNSPECIFIED'})",
                shipment_code=dispatch_id,
                transport_mode="TERRESTRIAL",
                origin_facility_id="fac-villeta-plant",
                destination=raw_destination or "Foz do Iguaçu, Brasil",
                carrier_id=carrier_id,
                weight_net_tons=net_tons,
                vessel_or_truck_id=f"Truck {plate}",
                corridor="Corredor Bioceánico / BR-277",
                status="IN_TRANSIT",
                provenance=provenance,
                attributes={
                    "legacy_dispatch_no": dispatch_id,
                    "dispatch_date": iso_date,
                    "gross_weight_kg": gross_kg,
                    "tare_weight_kg": tare_kg,
                    "net_weight_kg": net_kg,
                    "moisture_pct": moisture_pct,
                },
            )
            shipments.append(shipment)

            # Create EvidenceRecord
            evidence = EvidenceRecord(
                id=f"evi-tms-{dispatch_id.lower()}",
                source="Synthetic Reference TMS (Legacy Normalized Stream)",
                source_type=EvidenceSourceType.ERP_RECORD,
                provenance=provenance,
                confidence=0.92,
                extracted_claim=f"Dispatch {dispatch_id} weighed {net_kg:.2f} kg net of {raw_product or 'unspecified product'} to {raw_destination}.",
                raw_payload_snippet=f"{dispatch_id};{raw_date};{raw_carrier};{raw_driver_plate};{gross_kg}kg",
                references_entity_ids=[shipment.id, carrier_id],
                metadata={
                    "parsed_net_kg": net_kg,
                    "plate": plate,
                },
            )
            evidence_records.append(evidence)

        report = IngestionReport(
            total_raw_rows=row_count,
            normalized_shipments=len(shipments),
            normalized_carriers=len(carriers_dict),
            evidence_records_created=len(evidence_records),
            anomalies_detected=len(anomalies),
            anomaly_details=anomalies,
        )

        return shipments, list(carriers_dict.values()), evidence_records, report
