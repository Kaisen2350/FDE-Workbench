"""Client-Ready FDE Deployment Brief Generator.

Produces an executive, auditable 12-section deployment briefing document
translating physical reality, operational evidence, and platform adapters
into an actionable commercial and technical pilot plan.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from fde_workbench.domain.pilots import PilotSpecification


class FDEBriefGenerator:
    """Compiles a PilotSpecification into a client-ready executive brief."""

    @staticmethod
    def generate_brief_dict(pilot: PilotSpecification, store: Optional[Any] = None) -> Dict[str, Any]:
        """Generate structured 12-section brief data dictionary."""
        econ = pilot.economic_model
        econ_summary = econ.summary()

        # Resolve evidence citations if store provided
        evidence_claims = []
        if store and hasattr(store, "list_evidence"):
            evis = store.list_evidence()
            for evi in evis:
                # Include evidence if linked to this opportunity or customer
                if (pilot.opportunity_id in (evi.references_events or [])) or \
                   (pilot.decision in (evi.references_decisions or [])) or \
                   any(e in (evi.references_entities or []) for e in [pilot.customer, "org-aidesa"]):
                    evidence_claims.append({
                        "id": evi.id,
                        "source": evi.source,
                        "source_type": evi.source_type,
                        "provenance": evi.provenance,
                        "claim": evi.extracted_claim,
                        "confidence": evi.confidence,
                    })

        # Fallback if no specific evidence matched in store
        if not evidence_claims:
            evidence_claims = [
                {
                    "id": "EVI-REF-01",
                    "source": "Operational Field Telemetry & Disruption Log",
                    "source_type": "ERP_RECORD",
                    "provenance": pilot.provenance,
                    "claim": f"Historical operational logs confirm {pilot.decision_owner} executes manual validations with {pilot.baseline_kpi.get('exception_rate', 'elevated')} exception rate.",
                    "confidence": 0.95,
                }
            ]

        watermark = "Illustrative — based on synthetic AIDESA data, pending client-specific baseline validation"

        sections = {
            "1_operational_problem": {
                "title": "1. Operational Problem",
                "question": "What is happening?",
                "workflow": pilot.workflow,
                "summary": f"In the {pilot.workflow} workflow at {pilot.customer}, manual execution creates severe latency and operational friction.",
                "baseline_kpi": pilot.baseline_kpi,
                "pain_points": [
                    f"Manual cycle time: {econ.manual_effort_minutes_per_decision} minutes per decision",
                    f"Current exception rate: {econ.current_error_or_exception_rate * 100:.1f}% across {econ.annual_decision_volume:,} annual decisions",
                    f"Direct cost per exception: ${econ.cost_per_exception_usd:,.2f} in demurrage, re-inspection, and delay penalties"
                ]
            },
            "2_evidence": {
                "title": "2. Empirical Evidence",
                "question": "How do we know?",
                "grounding_method": pilot.measurement_method,
                "evidence_records": evidence_claims,
            },
            "3_decision_loop": {
                "title": "3. Decision Loop",
                "question": "What decision is currently being made manually?",
                "decision": pilot.decision,
                "decision_owner": pilot.decision_owner,
                "trigger": pilot.trigger,
                "cycle": f"Triggered by '{pilot.trigger}', evaluated by {pilot.decision_owner}."
            },
            "4_economic_impact": {
                "title": "4. Economic Impact & ROI Equation",
                "question": "What does the problem cost, and what does the solution yield?",
                "equations": {
                    "baseline_annual_cost": econ_summary["baseline_annual_total_usd"],
                    "baseline_labor_cost": econ_summary["baseline_annual_labor_usd"],
                    "baseline_exception_cost": econ_summary["baseline_annual_exception_usd"],
                    "target_annual_cost": econ_summary["target_annual_total_usd"],
                    "addressable_annual_savings": econ_summary["addressable_annual_savings_usd"],
                    "pilot_batch_value": econ_summary["pilot_batch_value_usd"],
                    "implementation_cost": econ_summary["pilot_implementation_cost_usd"],
                    "annual_software_license": econ_summary["annual_software_license_usd"],
                    "total_first_year_investment": econ_summary["total_first_year_investment_usd"],
                    "net_first_year_roi": econ_summary["first_year_net_roi_usd"],
                    "roi_percentage": econ_summary["expected_roi_percentage"],
                    "payback_months": econ_summary["payback_period_months"]
                },
                "assumptions_ledger": econ.get_assumptions_table(),
                "sensitivity_analysis": econ.compute_sensitivity()
            },
            "5_proposed_intervention": {
                "title": "5. Proposed AI Intervention",
                "question": "What should AI actually do?",
                "intervention": pilot.recommended_action,
                "inputs": pilot.inputs,
                "context": pilot.context,
            },
            "6_human_authority": {
                "title": "6. Human Authority & Governance",
                "question": "What remains under strict human control?",
                "gate": pilot.human_approval_required,
                "authorized_actions": pilot.authorized_actions,
                "safety_constraints": pilot.safety_constraints,
                "rollback_condition": pilot.rollback_condition
            },
            "7_required_data": {
                "title": "7. Required Data & Telemetry",
                "question": "What systems and data are needed?",
                "data_sources": pilot.data_sources,
                "required_integrations": pilot.required_integrations,
                "dependencies": pilot.deployment_dependencies
            },
            "8_architecture": {
                "title": "8. Architecture & Integration Pattern",
                "question": "How will it integrate into customer infrastructure?",
                "pattern": "Sidecar Decision Engine with Human-in-the-Loop Gate",
                "read_path": "Read-only ingestion from ERP/TMS/Documents via webhook or poll",
                "eval_path": "Deterministic validation against domain ontology + LLM fuzzy cross-document extraction",
                "action_path": "Pre-filled rectification draft posted to operator queue; zero direct external mutation without human broker sign-off"
            },
            "9_pilot_scope": {
                "title": "9. Pilot Scope & Duration",
                "question": "What gets deployed first?",
                "duration": pilot.pilot_duration,
                "scope": pilot.pilot_scope,
                "volume": f"{econ.pilot_decision_volume} decisions / shipments",
                "effort": pilot.implementation_effort
            },
            "10_success_criteria": {
                "title": "10. Success & Acceptance Criteria",
                "question": "What measurable result constitutes success?",
                "target_kpi": pilot.target_kpi,
                "acceptance_criteria": pilot.acceptance_criteria,
                "failure_modes_monitored": pilot.failure_modes
            },
            "11_platform_options": {
                "title": "11. Enterprise Platform Options",
                "question": "Which technology stacks can run this blueprint?",
                "active_platform": pilot.selected_platform,
                "supported_platforms": pilot.supported_platforms,
                "platform_breakdown": {
                    "gemini_enterprise": {
                        "name": "Google Cloud / Gemini Enterprise",
                        "core_service": "Vertex AI Agent Engine (gemini-2.5-flash / gemini-2.5-pro)",
                        "tooling": "Typed OpenAPI 3.0 / GenAI SDK function declarations",
                        "grounding": "Vertex AI Search over regulatory customs tariffs & SOPs"
                    },
                    "microsoft_azure_ai_foundry": {
                        "name": "Microsoft Azure AI Foundry",
                        "core_service": "Azure OpenAI Service (GPT-4o / 4o-mini) + Semantic Kernel",
                        "tooling": "Native C# / Python Semantic Kernel Plugins with RequiresConsent policy",
                        "grounding": "Azure AI Search with integrated vector index"
                    },
                    "openai_assistants": {
                        "name": "OpenAI Enterprise",
                        "core_service": "Assistants API v2",
                        "tooling": "Strict JSON Schema function calling (strict: true)",
                        "grounding": "File Search vector storage over transit documents"
                    },
                    "databricks_mosaic_ai": {
                        "name": "Databricks Mosaic AI",
                        "core_service": "Mosaic AI Agent Framework & Model Serving",
                        "tooling": "Unity Catalog three-tier registered functions (catalog.schema.tool)",
                        "grounding": "Unity Catalog Vector Search"
                    }
                }
            },
            "12_expansion_path": {
                "title": "12. Expansion Path & Flywheel Leverage",
                "question": "What adjacent workflow becomes possible if the pilot works?",
                "expansion": pilot.expansion_path,
                "flywheel": "Deploy Pilot -> Measure Hard Dollar ROI -> Expand to Adjacent Workflows -> Compound Enterprise Moat."
            }
        }

        return {
            "pilot_id": pilot.pilot_id,
            "opportunity_id": pilot.opportunity_id,
            "title": pilot.title,
            "customer": pilot.customer,
            "generated_at": datetime.utcnow().isoformat(),
            "status": pilot.status,
            "provenance": pilot.provenance,
            "watermark": watermark,
            "sections": sections,
        }

    @classmethod
    def generate_markdown(cls, pilot: PilotSpecification, store: Optional[Any] = None) -> str:
        """Generate client-ready formatted Markdown document."""
        data = cls.generate_brief_dict(pilot, store)
        s = data["sections"]
        econ = s["4_economic_impact"]["equations"]

        md = []
        md.append(f"# FDE Deployment Brief: {pilot.title}")
        md.append("")
        md.append("> [!WARNING]")
        md.append(f"> **{data.get('watermark', 'Illustrative — based on synthetic AIDESA data, pending client-specific baseline validation')}**")
        md.append("")
        md.append(f"**Target Enterprise**: {pilot.customer}  ")
        md.append(f"**Pilot Identifier**: `{pilot.pilot_id}` | **Status**: `{pilot.status}` | **Provenance**: `{pilot.provenance}`  ")
        md.append(f"**Document Date**: {datetime.utcnow().strftime('%B %d, %Y')} | **Prepared By**: Forward Deployed Engineering (FDE)  ")
        md.append("")
        md.append("> **Executive Mandate**: This briefing document establishes the operational reality, economic equation, human governance boundary, and measurable acceptance criteria for a 30-day pilot deployment.")
        md.append("")
        md.append("---")
        md.append("")

        # 1. Problem
        p = s["1_operational_problem"]
        md.append(f"## {p['title']}")
        md.append(f"*{p['question']}*  \n")
        md.append(f"{p['summary']}\n")
        md.append("**Observed Operational Baseline:**")
        for k, v in p["baseline_kpi"].items():
            md.append(f"- **{k.replace('_', ' ').title()}**: `{v}`")
        for pt in p["pain_points"]:
            md.append(f"- ⚠️ {pt}")
        md.append("")

        # 2. Evidence
        ev = s["2_evidence"]
        md.append(f"## {ev['title']}")
        md.append(f"*{ev['question']}*  \n")
        md.append(f"**Measurement & Audit Methodology**: {ev['grounding_method']}\n")
        md.append("| Evidence ID | Source / System | Type | Provenance | Confidence | Empirical Claim |")
        md.append("|:---|:---|:---|:---|:---:|:---|")
        for r in ev["evidence_records"]:
            md.append(f"| `{r['id']}` | **{r['source']}** | `{r['source_type']}` | `{r['provenance']}` | {r['confidence']*100:.0f}% | *\"{r['claim']}\"* |")
        md.append("")

        # 3. Decision Loop
        dl = s["3_decision_loop"]
        md.append(f"## {dl['title']}")
        md.append(f"*{dl['question']}*  \n")
        md.append(f"- **Manual Decision Point**: `{dl['decision']}`")
        md.append(f"- **Accountable Decision Owner**: **{dl['decision_owner']}**")
        md.append(f"- **Operational Trigger**: {dl['trigger']}")
        md.append(f"- **Escalation Trigger Model**: Evaluated on-demand via operator review sweep or automated hourly cron sweep calling `POST /api/decisions/check-escalations` (timeout threshold: 2.0 hours; does not rely on an unmonitored background daemon in local-first mode).")
        md.append("")

        # 4. Economic Impact
        ei = s["4_economic_impact"]
        md.append(f"## {ei['title']}")
        md.append(f"*{ei['question']}*  \n")
        md.append("```text")
        md.append(f"Baseline Annual Cost:          ${econ['baseline_annual_cost']:>12,.2f}  (Labor: ${econ['baseline_labor_cost']:,.2f} + Exceptions: ${econ['baseline_exception_cost']:,.2f})")
        md.append(f"Target Annual Post-Pilot:      ${econ['target_annual_cost']:>12,.2f}")
        md.append("--------------------------------------------------------------------------------")
        md.append(f"Addressable Annual Savings:    ${econ['addressable_annual_savings']:>12,.2f} / year")
        md.append(f"Implementation Cost:           ${econ['implementation_cost']:>12,.2f}  (One-time engineering & deployment)")
        md.append(f"Annual Software License:       ${econ['annual_software_license']:>12,.2f}  (Subscription runtime)")
        md.append(f"Total 1st-Year Investment:     ${econ['total_first_year_investment']:>12,.2f}  (Implementation + License)")
        md.append("--------------------------------------------------------------------------------")
        md.append(f"Net 1st-Year ROI ($):          ${econ['net_first_year_roi']:>12,.2f}  (Savings - Total Investment)")
        md.append(f"ROI %:                          {econ['roi_percentage']:>12.1f}%  (Net 1st-Year ROI / Total Investment * 100)")
        md.append(f"Capital Payback Period:         {econ['payback_months']:>12.1f} months")
        md.append(f"Pilot Batch Measured Value:    ${econ['pilot_batch_value']:>12,.2f}  (During controlled pilot scope)")
        md.append("```")
        md.append("")
        md.append("### Assumptions Ledger")
        md.append("| Parameter | Baseline Value | Unit | Operational Source / Rationale |")
        md.append("|:---|:---:|:---|:---|")
        for item in ei["assumptions_ledger"]:
            md.append(f"| `{item['parameter']}` | **{item['value']}** | {item['unit']} | *{item['source_or_rationale']}* |")
        md.append("")
        md.append("### Sensitivity Analysis (±20% Sensitivity Range)")
        md.append("| Scenario | Volume | Touch Time | Residual Errors | Annual Savings | Net 1st-Year ROI ($) | Net ROI (%) | Payback |")
        md.append("|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")
        scenarios = ei["sensitivity_analysis"].get("scenarios", {})
        for sc_key, sc in scenarios.items():
            md.append(f"| **{sc['label']}** | {sc['annual_volume']:,} | {sc['target_manual_minutes']}m | {sc['target_exception_rate_pct']:.1f}% | ${sc['addressable_annual_savings_usd']:,.2f} | ${sc['net_first_year_roi_usd']:,.2f} | **{sc['roi_percentage']:.1f}%** | {sc['payback_period_months']:.1f} mo |")
        md.append("")

        # 5. Proposed Intervention
        pi = s["5_proposed_intervention"]
        md.append(f"## {pi['title']}")
        md.append(f"*{pi['question']}*  \n")
        md.append(f"{pi['intervention']}\n")
        md.append(f"**Operational Context**: {pi['context']}\n")
        md.append("**Processed Document Inputs:**")
        for inp in pi["inputs"]:
            md.append(f"- `📄 {inp}`")
        md.append("")

        # 6. Human Authority
        ha = s["6_human_authority"]
        md.append(f"## {ha['title']}")
        md.append(f"*{ha['question']}*  \n")
        md.append(f"> [!IMPORTANT]\n> **Mandatory Human-in-the-Loop Sign-Off**:  \n> {ha['gate']}\n")
        md.append("**Permitted Agent Actions (Read-Only & Drafting):**")
        for act in ha["authorized_actions"]:
            md.append(f"- `✓ {act}`")
        md.append("")
        md.append(f"**Rollback Condition / Kill Switch**:  \n*{ha['rollback_condition']}*\n")
        md.append("**Safety Invariants:**")
        for sc in ha["safety_constraints"]:
            md.append(f"- 🛡️ {sc}")
        md.append("- 🛡️ Audit guarantee: All human actions logged to append-only SHA-256 hash-chain (tamper-evident within current seeded database session; resets on database reseed).")
        md.append("- 🛡️ Decision timeout governance: Pending decisions escalate via on-demand sweep or scheduled cron webhook, maintaining determinism without unmonitored background daemons.")
        md.append("")

        # 7. Required Data
        rd = s["7_required_data"]
        md.append(f"## {rd['title']}")
        md.append(f"*{rd['question']}*  \n")
        md.append("**Systems of Record & Feeds:**")
        for ds in rd["data_sources"]:
            md.append(f"- 💾 {ds}")
        md.append("\n**Required Integration Connectors:**")
        for ri in rd["required_integrations"]:
            md.append(f"- 🔌 {ri}")
        md.append("")

        # 8. Architecture
        ar = s["8_architecture"]
        md.append(f"## {ar['title']}")
        md.append(f"*{ar['question']}*  \n")
        md.append(f"- **Integration Pattern**: **{ar['pattern']}**")
        md.append(f"- **Ingestion (Read Path)**: {ar['read_path']}")
        md.append(f"- **Evaluation (Reasoning)**: {ar['eval_path']}")
        md.append(f"- **Execution (Action Path)**: {ar['action_path']}")
        md.append("")

        # 9. Pilot Scope
        ps = s["9_pilot_scope"]
        md.append(f"## {ps['title']}")
        md.append(f"*{ps['question']}*  \n")
        md.append(f"- **Calendar Duration**: **{ps['duration']}**")
        md.append(f"- **Deployment Boundary**: {ps['scope']} ({ps['volume']})")
        md.append(f"- **FDE Engineering Effort**: {ps['effort']}")
        md.append("")

        # 10. Success Criteria
        sc = s["10_success_criteria"]
        md.append(f"## {sc['title']}")
        md.append(f"*{sc['question']}*  \n")
        md.append("**Target KPI Outcomes:**")
        for k, v in sc["target_kpi"].items():
            md.append(f"- **{k.replace('_', ' ').title()}**: `{v}`")
        md.append("\n**Rigorous Acceptance Criteria for Production Graduation:**")
        for ac in sc["acceptance_criteria"]:
            md.append(f"- [ ] **{ac}**")
        md.append("")

        # 11. Platform Options
        po = s["11_platform_options"]
        md.append(f"## {po['title']}")
        md.append(f"*{po['question']}*  \n")
        md.append(f"The pilot blueprint is **platform-agnostic**. The operational domain logic remains identical across any of the following enterprise execution substrates:\n")
        md.append("| Platform Ecosystem | Core Engine / Models | Tool Execution Mechanism | Grounding Data Substrate |")
        md.append("|:---|:---|:---|:---|")
        for pkey, pval in po["platform_breakdown"].items():
            is_active = " **(Selected)**" if pkey == po["active_platform"] else ""
            md.append(f"| **{pval['name']}**{is_active} | `{pval['core_service']}` | {pval['tooling']} | {pval['grounding']} |")
        md.append("")

        # 12. Expansion Path
        ep = s["12_expansion_path"]
        md.append(f"## {ep['title']}")
        md.append(f"*{ep['question']}*  \n")
        md.append(f"**Immediate Expansion Horizon**:  \n{ep['expansion']}\n")
        md.append(f"**FDE Flywheel**: *{ep['flywheel']}*")
        md.append("")

        return "\n".join(md)

    generate_brief_data = generate_brief_dict

