"""FDE Discovery Intake Layer — Structured intake and transformation engine."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from fde_workbench.domain.provenance import ProvenanceType
from fde_workbench.domain.ontology import EntityTypeEnum
from fde_workbench.domain.entities import Organization, Facility, EmployeeRole, KPI
from fde_workbench.domain.ai_opportunities import (
    AIOpportunity,
    DeploymentComplexity,
    FDEPrioritization,
    EconomicLeverage,
    OperationalCharacteristics,
    DeploymentFeasibility,
    StrategicValue,
)
from fde_workbench.domain.agent_specs import AgentSpecification, ToolDefinition


class CompanyDiscoveryProfile(BaseModel):
    """Core profile captured during FDE Day-1 enterprise intake."""
    name: str = Field(..., description="Legal company name")
    ruc: str = Field(default="", description="Paraguayan RUC fiscal ID")
    industry: str = Field(..., description="e.g. Agribusiness, Maquila, Cattle/Meat Processing")
    headcount: int = Field(default=250)
    annual_revenue_usd: str = Field(default="50M-100M", description="Revenue bracket")
    export_markets: List[str] = Field(default_factory=list, description="Target export jurisdictions: Brazil, Argentina, Chile, EU")
    facilities: List[Dict[str, Any]] = Field(default_factory=list, description="Plants, ports, and warehouses")
    erp: str = Field(default="SAP Business One", description="Core ERP system")
    crm: str = Field(default="None / Spreadsheets", description="Customer management")
    tms_wms: str = Field(default="Trans-Chaco TMS", description="Logistics / Warehouse management")
    cloud_ecosystem: str = Field(default="Google Workspace", description="Google Workspace, Microsoft 365, or Hybrid")


class CriticalWorkflowIntake(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    volume_per_month: str = Field(...)
    lead_time_days: float = Field(default=0.0)
    primary_systems: List[str] = Field(default_factory=list)


class BottleneckIntake(BaseModel):
    id: str = Field(...)
    workflow_id: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    estimated_cost_exposure_annual_usd: float = Field(default=0.0)
    delay_hours: float = Field(default=0.0)
    primary_cause: str = Field(...)


class DecisionIntake(BaseModel):
    id: str = Field(...)
    title: str = Field(...)
    decision_maker_role: str = Field(...)
    frequency: str = Field(...)
    information_sources: List[str] = Field(default_factory=list)
    consequence_of_delay: str = Field(...)


class KPIIntake(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    current_value: str = Field(...)
    target_value: str = Field(...)
    unit: str = Field(...)


class DataSourceIntake(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    system: str = Field(...)
    format: str = Field(..., description="SQL, Sheets, PDFs, REST API, Báscula tickets")
    accessibility: str = Field(..., description="Direct Read Access, Manual Export, Air-Gapped")


class StakeholderIntake(BaseModel):
    role_title: str = Field(...)
    department: str = Field(...)
    interviews_completed: int = Field(default=1)
    key_priorities: List[str] = Field(default_factory=list)


class ConstraintsIntake(BaseModel):
    security: str = Field(..., description="Data residency, PII, internal IP rules")
    compliance: str = Field(..., description="DNIT tax, SEPRELAD AML, SENACSA/SENAVE rules")
    budget_tier: str = Field(..., description="Pilot investment tolerance")
    integration: str = Field(..., description="API availability, on-prem vs cloud")
    change_management: str = Field(..., description="User technical readiness, union/worker considerations")


class DiscoveryIntake(BaseModel):
    """
    Structured FDE Discovery Intake dossier.
    Represents the operational capture artifact when an FDE enters an enterprise.
    """
    intake_id: str = Field(..., description="Unique intake identifier, e.g. 'intake-2026-aidesa'")
    date_conducted: datetime = Field(default_factory=datetime.utcnow)
    lead_fde: str = Field(default="Forward Deployed Engineer")
    company_profile: CompanyDiscoveryProfile
    critical_workflows: List[CriticalWorkflowIntake] = Field(default_factory=list)
    known_bottlenecks: List[BottleneckIntake] = Field(default_factory=list)
    key_decisions: List[DecisionIntake] = Field(default_factory=list)
    current_kpis: List[KPIIntake] = Field(default_factory=list)
    data_sources: List[DataSourceIntake] = Field(default_factory=list)
    stakeholders: List[StakeholderIntake] = Field(default_factory=list)
    constraints: ConstraintsIntake


class DiscoveryTransformationEngine:
    """
    Transforms an FDE Discovery Intake into the operational foundation:
    Discovery Intake -> Operational Model -> Bottlenecks -> Opportunities -> Agent Specs
    """

    @staticmethod
    def generate_operational_model(intake: DiscoveryIntake, store: Any) -> Dict[str, Any]:
        """
        Populates or augments the workbench store with the models derived from intake.
        """
        created_counts = {
            "entities": 0,
            "opportunities": 0,
            "agent_specs": 0,
            "pilot_candidates": 0,
        }

        # 1. Organization Entity
        org = Organization(
            id=f"org-{intake.company_profile.name.lower().replace(' ', '-')[:12]}",
            name=intake.company_profile.name,
            ruc=intake.company_profile.ruc,
            headcount=intake.company_profile.headcount,
            export_regime=intake.company_profile.industry,
            primary_corridors=intake.company_profile.export_markets,
            system_of_record=intake.company_profile.erp,
            provenance=ProvenanceType.CUSTOMER_PROVIDED,
        )
        store.add_entity(org)
        created_counts["entities"] += 1

        # 2. Facilities
        for fac_info in intake.company_profile.facilities:
            fac = Facility(
                id=fac_info.get("id", f"fac-{fac_info.get('name', 'facility')[:8].lower()}"),
                name=fac_info.get("name", "Industrial Facility"),
                facility_type=fac_info.get("type", "PROCESSING_PLANT"),
                department=fac_info.get("department", "Central"),
                city=fac_info.get("city", "Villeta"),
                throughput_capacity_tpd=float(fac_info.get("capacity_tpd", 2500.0)),
                has_barge_dock=bool(fac_info.get("has_barge_dock", False)),
                provenance=ProvenanceType.CUSTOMER_PROVIDED,
            )
            store.add_entity(fac)
            created_counts["entities"] += 1

        # 3. Employee Roles from Stakeholders
        for stk in intake.stakeholders:
            role_id = f"role-{stk.role_title.lower().replace(' ', '-')[:16]}"
            role = EmployeeRole(
                id=role_id,
                name=stk.role_title,
                department=stk.department,
                headcount=1,
                provenance=ProvenanceType.CUSTOMER_PROVIDED,
            )
            store.add_entity(role)
            created_counts["entities"] += 1

        # 4. Opportunities from Bottlenecks
        for bnk in intake.known_bottlenecks:
            opp_id = f"opp-{bnk.id}"
            opp = AIOpportunity(
                id=opp_id,
                title=f"Automate & Guardrail: {bnk.title}",
                workflow=bnk.workflow_id,
                bottleneck=bnk.description,
                business_impact=f"${bnk.estimated_cost_exposure_annual_usd:,.0f}/yr cost exposure; {bnk.delay_hours}h average delay",
                entities_involved=[EntityTypeEnum.OPERATIONAL_EVENT, EntityTypeEnum.DECISION],
                data_required=[ds.name for ds in intake.data_sources[:3]],
                decision_involved=f"Resolution of {bnk.title}",
                proposed_ai_intervention=f"Deterministic cross-system reconciliation and early anomaly prediction for {bnk.title}",
                human_in_the_loop_requirement="Mandatory human sign-off prior to state mutation or external filing",
                permissions_required=["READ: ERP/TMS", "DRAFT: Internal Notification"],
                failure_modes=["False positive anomaly alert", "Stale cached hydrology or border state"],
                kpi=intake.current_kpis[0].name if intake.current_kpis else "Cycle Time",
                deployment_complexity=DeploymentComplexity.MEDIUM,
                estimated_payoff_annual_usd=bnk.estimated_cost_exposure_annual_usd * 0.40,
                prioritization=FDEPrioritization(
                    economic_leverage=EconomicLeverage(
                        revenue_impact=7,
                        cost_impact=8,
                        working_capital_impact=8,
                        risk_exposure=9,
                    ),
                    operational_characteristics=OperationalCharacteristics(
                        frequency=9,
                        decision_complexity=7,
                        current_manual_effort=9,
                        latency_sensitivity=8,
                        cross_system_fragmentation=8,
                    ),
                    deployment_feasibility=DeploymentFeasibility(
                        data_availability=8,
                        integration_complexity=7,
                        security_sensitivity=8,
                        human_approval_clarity=9,
                        change_management_readiness=7,
                    ),
                    strategic_value=StrategicValue(
                        repeatability=9,
                        adjacent_workflows_count=8,
                        cross_customer_applicability=9,
                        reusable_ip_potential=9,
                    ),
                    pilot_recommendation="HIGH_PRIORITY_PILOT",
                    prioritization_rationale=f"High frequency and severe cost impact ({bnk.description}) with accessible data in {intake.company_profile.cloud_ecosystem}.",
                ),
            )
            store.add_opportunity(opp)
            created_counts["opportunities"] += 1
            if opp.prioritization.pilot_recommendation == "HIGH_PRIORITY_PILOT":
                created_counts["pilot_candidates"] += 1

        return created_counts
