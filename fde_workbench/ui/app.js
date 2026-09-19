/**
 * Paraguay Export Economy FDE Workbench — Client Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  loadDiscoveryIntake();
  loadEvidence();
  loadOntology();
  loadEntities();
  loadRelationships();
  loadEvents();
  loadDecisions();
  loadWorkflows();
  loadOpportunities();
  loadAgentSpecs();
  loadPilots();
  loadKPIs();
  loadCompany();
  bindGlobalActions();
});

// Tab Switching
function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  const panes = document.querySelectorAll(".tab-pane");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetId = tab.dataset.tab;
      tabs.forEach(t => t.classList.remove("active"));
      panes.forEach(p => p.classList.remove("active"));

      tab.classList.add("active");
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");
    });
  });
}

// Helper: Provenance Badge HTML
function getProvenanceBadge(prov) {
  if (!prov) prov = "SYNTHETIC";
  const p = prov.toLowerCase().replace(/_/g, "-");
  return `<span class="badge-provenance badge-prov-${p}">${escapeHtml(prov)}</span>`;
}

// 0. FDE DISCOVERY INTAKE & TRANSFORMATION
async function loadDiscoveryIntake() {
  const container = document.getElementById("discoveryContent");
  if (!container) return;
  container.innerHTML = `<div class="card">Loading enterprise discovery dossier...</div>`;

  try {
    const res = await fetch("/api/discovery/intake");
    if (!res.ok) throw new Error("Failed to load discovery intake");
    const intake = await res.json();
    renderDiscoveryIntake(intake);
  } catch (err) {
    container.innerHTML = `<div class="card" style="color:var(--alert);">Failed to load discovery intake: ${escapeHtml(err.message)}</div>`;
  }
}

function renderDiscoveryIntake(intake) {
  const container = document.getElementById("discoveryContent");
  if (!container) return;

  const p = intake.company_profile;
  const corridors = (p.primary_export_corridors || []).map(c => `<span class="badge badge-local">${escapeHtml(c)}</span>`).join(" ");

  container.innerHTML = `
    <!-- Company Profile Summary -->
    <div class="discovery-card" style="border-left: 4px solid var(--river);">
      <div class="discovery-card-header">
        <div>
          <span class="badge badge-provenance badge-prov-customer-provided">CUSTOMER_PROVIDED</span>
          <h3 style="font-family:var(--font-serif); margin:4px 0 2px;">${escapeHtml(p.company_name)}</h3>
          <span style="font-family:var(--font-mono); font-size:11.5px; color:var(--ink-muted);">RUC: ${escapeHtml(p.ruc)} · Sector: ${escapeHtml(p.sector)} · Headcount: ${p.approximate_headcount}</span>
        </div>
        <div style="text-align:right;">
          <span class="badge badge-status">${escapeHtml(p.export_regime)}</span>
          <div style="font-size:12px; margin-top:4px;">Annual Export: <strong>${p.annual_export_volume_usd ? '$' + Number(p.annual_export_volume_usd).toLocaleString() : 'N/A'}</strong></div>
        </div>
      </div>
      <p style="font-size:13.5px; color:var(--ink-soft); margin:0 0 12px;">${escapeHtml(p.core_business)}</p>
      <div style="font-size:12.5px; margin-bottom:8px;"><strong>Export Corridors:</strong> ${corridors}</div>
      <div style="font-size:12px; color:var(--ink-muted); font-family:var(--font-mono);">Intake ID: ${escapeHtml(intake.intake_id)} · Interviewed: ${escapeHtml(intake.interviewed_by)} · Date: ${escapeHtml(intake.created_at ? intake.created_at.slice(0,10) : '')}</div>
    </div>

    <div class="grid-2">
      <!-- Critical Workflows -->
      <div class="discovery-card">
        <div class="discovery-card-header">
          <span>Critical Operational Workflows (${intake.critical_workflows.length})</span>
          <span class="badge badge-local">High Impact</span>
        </div>
        <div>
          ${intake.critical_workflows.map(wf => `
            <div style="border-bottom:1px solid var(--rule-light); padding:8px 0; margin-bottom:8px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong style="color:var(--river-deep); font-size:13.5px;">${escapeHtml(wf.name)}</strong>
                <span class="badge" style="background:${wf.priority === 'CRITICAL' ? 'var(--alert-soft)' : 'var(--gold-soft)'}; color:var(--ink); font-size:10.5px;">${escapeHtml(wf.priority)}</span>
              </div>
              <p style="font-size:12.5px; margin:4px 0 6px; color:var(--ink);">${escapeHtml(wf.description)}</p>
              <div style="font-size:11.5px; color:var(--ink-soft);">
                <strong>Owner:</strong> ${escapeHtml(wf.primary_owner_role)} | <strong>Cycle:</strong> ${escapeHtml(wf.cycle_time_estimate)}<br>
                <strong>Pain Point:</strong> <span style="color:var(--rust);">${escapeHtml(wf.current_pain_point)}</span>
              </div>
            </div>
          `).join("")}
        </div>
      </div>

      <!-- Operational Bottlenecks -->
      <div class="discovery-card">
        <div class="discovery-card-header">
          <span>Reported Bottlenecks (${intake.bottlenecks.length})</span>
          <span class="badge" style="background:var(--alert-soft); color:var(--alert);">Financial Drag</span>
        </div>
        <div>
          ${intake.bottlenecks.map(b => `
            <div style="border-bottom:1px solid var(--rule-light); padding:8px 0; margin-bottom:8px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong style="color:var(--rust); font-size:13.5px;">${escapeHtml(b.name)}</strong>
                <span style="font-family:var(--font-mono); font-weight:700; color:var(--alert); font-size:12px;">-$${(b.monthly_financial_loss_usd || 0).toLocaleString()}/mo</span>
              </div>
              <p style="font-size:12.5px; margin:4px 0 4px; color:var(--ink);">${escapeHtml(b.root_cause)}</p>
              <div style="font-size:11.5px; color:var(--ink-soft);">
                <strong>Delay:</strong> ~${b.latency_hours_impact} hrs | <strong>Frequency:</strong> ${escapeHtml(b.frequency)}<br>
                <strong>Current Workaround:</strong> <em>${escapeHtml(b.current_workaround)}</em>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    </div>

    <!-- Operational Constraints & Data Sources -->
    <div class="grid-2" style="margin-top:16px;">
      <div class="discovery-card">
        <div class="discovery-card-header">
          <span>Hard Enterprise Constraints (${intake.constraints ? intake.constraints.length : 0})</span>
          <span class="badge badge-status">Boundary Conditions</span>
        </div>
        <div>
          ${(intake.constraints || []).map(c => `
            <div class="constraint-pill">
              <div style="display:flex; justify-content:space-between;">
                <strong>${escapeHtml(c.category)}</strong>
                <span class="badge" style="font-size:10px; background:${c.rigidness === 'NON_NEGOTIABLE' ? 'var(--alert-soft)' : 'var(--gold-soft)'}; color:var(--ink);">${escapeHtml(c.rigidness)}</span>
              </div>
              <div style="margin:4px 0; font-size:12px;">${escapeHtml(c.description)}</div>
              <div style="font-size:11px; color:var(--ink-muted);">Mitigation: ${escapeHtml(c.mitigation_approach)}</div>
            </div>
          `).join("")}
        </div>
      </div>

      <div class="discovery-card">
        <div class="discovery-card-header">
          <span>Data Sources & Telemetry (${intake.data_sources.length})</span>
          <span class="badge badge-local">Systems of Record</span>
        </div>
        <div>
          ${intake.data_sources.map(ds => `
            <div style="border-bottom:1px solid var(--rule-light); padding:6px 0; font-size:12.5px;">
              <div style="display:flex; justify-content:space-between;">
                <strong style="color:var(--river-deep);">${escapeHtml(ds.system_name)}</strong>
                <span class="badge badge-local" style="font-size:10.5px;">${escapeHtml(ds.source_type)}</span>
              </div>
              <div style="color:var(--ink-soft); font-size:12px; margin:2px 0;">${escapeHtml(ds.description)}</div>
              <div style="font-size:11px; font-family:var(--font-mono); color:var(--ink-muted);">Access: ${escapeHtml(ds.access_method)} · Refresh: ${escapeHtml(ds.refresh_cadence)} · Format: ${escapeHtml(ds.data_format)}</div>
            </div>
          `).join("")}
        </div>
      </div>
    </div>
  `;
}

// Bind Discovery Transformation Button
const btnTransform = document.getElementById("btnRunDiscoveryTransform");
if (btnTransform) {
  btnTransform.addEventListener("click", async () => {
    if (!confirm("Run Discovery Transformation Engine?\\n\\nThis parses the enterprise discovery intake and compiles the operational model into entities, workflows, and prioritized AI opportunities.")) return;
    btnTransform.disabled = true;
    btnTransform.textContent = "Processing Transformation...";
    try {
      const res = await fetch("/api/discovery/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ intake_file: "aidesa_discovery_intake.json" })
      });
      const data = await res.json();
      alert(`Transformation Succeeded!\\n\\nGenerated:\\n- ${data.summary.entities_count} Entities\\n- ${data.summary.relationships_count} Relationships\\n- ${data.summary.workflows_count} Workflows\\n- ${data.summary.opportunities_count} AI Opportunities\\n- ${data.summary.agent_specs_count} Agent Specifications\\n\\nReloading views...`);
      window.location.reload();
    } catch (err) {
      alert("Transformation failed: " + err);
    } finally {
      btnTransform.disabled = false;
      btnTransform.textContent = "⚡ Ingest Intake & Generate Model";
    }
  });
}

// 0.5. SOURCE EVIDENCE & PROVENANCE REGISTRY
async function loadEvidence() {
  const typeSel = document.getElementById("selectEvidenceSourceType");
  const provSel = document.getElementById("selectEvidenceProvenance");
  let url = "/api/evidence?limit=100";
  const params = [];
  if (typeSel && typeSel.value) params.push(`source_type=${encodeURIComponent(typeSel.value)}`);
  if (provSel && provSel.value) params.push(`provenance=${encodeURIComponent(provSel.value)}`);
  if (params.length) url += "&" + params.join("&");

  try {
    const res = await fetch(url);
    const data = await res.json();
    renderEvidenceTable(data.evidence);

    const countBadge = document.getElementById("evidenceCountBadge");
    if (countBadge) countBadge.textContent = `${data.count} Evidence Items`;
  } catch (err) {
    console.error("Failed to load evidence:", err);
  }
}

function renderEvidenceTable(items) {
  const tbody = document.querySelector("#tableEvidence tbody");
  if (!tbody) return;
  if (!items.length) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--ink-muted);">No evidence records match current filters.</td></tr>`;
    return;
  }

  tbody.innerHTML = items.map(e => {
    const provBadge = getProvenanceBadge(e.provenance);
    const refs = [];
    if (e.references_entities && e.references_entities.length) {
      refs.push(`Entities: ` + e.references_entities.map(eid => `<a href="javascript:void(0)" onclick="event.stopPropagation(); inspectEntity('${eid}')" style="color:var(--river-deep); font-weight:600;">${eid}</a>`).join(", "));
    }
    if (e.references_events && e.references_events.length) {
      refs.push(`Events: ` + e.references_events.join(", "));
    }
    if (e.references_decisions && e.references_decisions.length) {
      refs.push(`Decisions: ` + e.references_decisions.join(", "));
    }

    return `
      <tr style="cursor:pointer;" onclick="inspectEvidence('${e.id}')">
        <td><code style="font-weight:600; color:var(--river-deep);">${e.id}</code></td>
        <td>
          <strong>${escapeHtml(e.source)}</strong>
          ${e.source_system ? `<br><span style="font-family:var(--font-mono); font-size:11px; color:var(--ink-muted);">${escapeHtml(e.source_system)}</span>` : ''}
        </td>
        <td><span class="badge badge-local">${e.source_type}</span></td>
        <td>${provBadge}</td>
        <td><span style="font-family:var(--font-mono); font-weight:600; color:var(--river-deep);">${(e.confidence * 100).toFixed(0)}%</span></td>
        <td>
          <div class="evidence-quote">${escapeHtml(e.extracted_claim)}</div>
        </td>
        <td style="font-size:11.5px; color:var(--ink-soft);">
          ${refs.length ? refs.join("<br>") : '<span style="color:var(--ink-muted); font-style:italic;">None</span>'}
        </td>
      </tr>
    `;
  }).join("");
}

const selectEvidenceSourceType = document.getElementById("selectEvidenceSourceType");
if (selectEvidenceSourceType) selectEvidenceSourceType.addEventListener("change", loadEvidence);
const selectEvidenceProvenance = document.getElementById("selectEvidenceProvenance");
if (selectEvidenceProvenance) selectEvidenceProvenance.addEventListener("change", loadEvidence);

// 1. ONTOLOGY
let ontologyData = null;
async function loadOntology() {
  try {
    const res = await fetch("/api/ontology");
    const data = await res.json();
    ontologyData = data;

    renderCriticalPathFeatured(data.metadata.critical_path_narrative || []);
    renderOntologyCards(data.metadata.entity_definitions);
    renderAllowedRelations(data.allowed_relationships);
    populateEntityTypeSelect(data.metadata.entity_types);
    initOntologyViewToggle();
  } catch (err) {
    console.error("Failed to load ontology:", err);
  }
}

function initOntologyViewToggle() {
  const btnCrit = document.getElementById("btnViewCriticalPath");
  const btnFull = document.getElementById("btnViewFullTaxonomy");
  const critContainer = document.getElementById("criticalPathFeaturedContainer");
  const fullContainer = document.getElementById("fullTaxonomyContainer");

  if (btnCrit && btnFull && critContainer && fullContainer) {
    btnCrit.addEventListener("click", () => {
      btnCrit.classList.add("btn-primary");
      btnFull.classList.remove("btn-primary");
      critContainer.style.display = "block";
      fullContainer.style.display = "none";
    });

    btnFull.addEventListener("click", () => {
      btnFull.classList.add("btn-primary");
      btnCrit.classList.remove("btn-primary");
      critContainer.style.display = "none";
      fullContainer.style.display = "block";
    });
  }
}

function renderCriticalPathFeatured(narrative) {
  const container = document.getElementById("criticalPathNodesList");
  if (!container) return;
  container.innerHTML = narrative.map(node => `
    <div class="workflow-node" style="border-left:3px solid var(--river); margin-bottom:12px;">
      <div class="node-step-num">${node.icon || '●'} Step ${node.step} · ${node.entity_type.toUpperCase()}</div>
      <div class="node-name" style="color:var(--river-deep); font-size:16px;">${node.label}</div>
      <p style="font-size:13px; margin:4px 0 6px; color:var(--ink);">${node.narrative}</p>
      <div style="font-family:var(--font-mono); font-size:11.5px; background:var(--paper); padding:4px 8px; border-radius:3px; display:inline-block;">
        Active Instance: <strong>${node.sample_instance}</strong>
      </div>
    </div>
  `).join("");
}

function renderOntologyCards(definitions) {
  const grid = document.getElementById("ontologyCardGrid");
  if (!grid) return;
  grid.innerHTML = "";

  Object.entries(definitions).forEach(([typeKey, def]) => {
    const card = document.createElement("div");
    card.className = "card card-accent-river";
    card.dataset.name = def.name.toLowerCase();
    card.dataset.desc = def.description.toLowerCase();
    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <h4 class="card-title">${def.name}</h4>
        <span class="badge badge-local">${def.category}</span>
      </div>
      <div class="card-subtitle">Type: <code>${typeKey}</code></div>
      <p style="font-size:13px; margin:0 0 10px; color:var(--ink);">${def.description}</p>
      <div style="background:var(--paper); padding:8px 10px; border-left:3px solid var(--river); font-size:12px; margin-bottom:10px;">
        <strong style="color:var(--river-deep);">Paraguayan Context:</strong> ${def.paraguayan_context}
      </div>
      <div style="font-family:var(--font-mono); font-size:11px; color:var(--ink-muted);">
        Key attributes: ${def.key_attributes.join(", ")}
      </div>
    `;
    grid.appendChild(card);
  });

  const searchInput = document.getElementById("searchOntologyInput");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase();
      document.querySelectorAll("#ontologyCardGrid .card").forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(q) ? "block" : "none";
      });
    });
  }
}

function renderAllowedRelations(relations) {
  const tbody = document.querySelector("#tableAllowedRelations tbody");
  if (!tbody) return;
  tbody.innerHTML = relations.map(r => `
    <tr>
      <td><code>${r.source_type}</code></td>
      <td><span class="badge badge-status">── ${r.relation_type} ──►</span></td>
      <td><code>${r.target_type}</code></td>
      <td style="color:var(--ink-soft);">${r.description}</td>
    </tr>
  `).join("");
}

function populateEntityTypeSelect(types) {
  const sel = document.getElementById("selectEntityType");
  if (!sel) return;
  types.forEach(t => {
    const opt = document.createElement("option");
    opt.value = t;
    opt.textContent = t.replace(/_/g, " ").toUpperCase();
    sel.appendChild(opt);
  });
}

// 2. ENTITIES
let filterCriticalPathEntities = false;

async function loadEntities() {
  const typeSelect = document.getElementById("selectEntityType");
  const searchInput = document.getElementById("searchEntityInput");
  const typeVal = typeSelect ? typeSelect.value : "";
  const searchVal = searchInput ? searchInput.value : "";

  let url = `/api/entities?limit=300`;
  if (filterCriticalPathEntities) url += `&critical_path=true`;
  if (typeVal) url += `&type=${encodeURIComponent(typeVal)}`;
  if (searchVal) url += `&search=${encodeURIComponent(searchVal)}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    renderEntitiesTable(data.entities);

    const countBadge = document.getElementById("entityCountBadge");
    if (countBadge) {
      const mode = filterCriticalPathEntities ? " (Critical Path)" : "";
      countBadge.textContent = `${data.count} / ${data.total_overall} Entities${mode}`;
    }
  } catch (err) {
    console.error("Failed to load entities:", err);
  }
}

function renderEntitiesTable(entities) {
  const tbody = document.querySelector("#tableEntities tbody");
  if (!tbody) return;
  tbody.innerHTML = entities.map(e => `
    <tr style="cursor:pointer;" onclick="inspectEntity('${e.id}')">
      <td><code style="font-weight:600; color:var(--river-deep);">${e.id}</code></td>
      <td><span class="badge badge-local">${e.entity_type}</span></td>
      <td><strong>${escapeHtml(e.name)}</strong></td>
      <td>
        <span style="font-family:var(--font-mono); font-size:11px;">${e.system_of_record}</span>
        <div style="margin-top:3px;">${getProvenanceBadge(e.provenance)}</div>
      </td>
      <td>${(e.tags || []).map(t => `<span class="badge" style="background:#EBE7DB; margin-right:4px;">${t}</span>`).join("")}</td>
      <td><button class="btn btn-primary" style="padding:3px 8px; font-size:11px;" onclick="event.stopPropagation(); inspectEntity('${e.id}')">Inspect</button></td>
    </tr>
  `).join("");
}

// Entity Filter bindings
const entityTypeSelect = document.getElementById("selectEntityType");
if (entityTypeSelect) entityTypeSelect.addEventListener("change", loadEntities);
const entitySearchInput = document.getElementById("searchEntityInput");
if (entitySearchInput) {
  let debounceTimeout = null;
  entitySearchInput.addEventListener("input", () => {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(loadEntities, 250);
  });
}
const btnFilterCrit = document.getElementById("btnFilterCriticalPathEntities");
if (btnFilterCrit) {
  btnFilterCrit.addEventListener("click", () => {
    filterCriticalPathEntities = !filterCriticalPathEntities;
    if (filterCriticalPathEntities) {
      btnFilterCrit.classList.add("btn-primary");
      btnFilterCrit.textContent = "★ Critical Path (Active)";
    } else {
      btnFilterCrit.classList.remove("btn-primary");
      btnFilterCrit.textContent = "★ Critical Path Only";
    }
    loadEntities();
  });
}

// 3. RELATIONSHIPS
async function loadRelationships() {
  const sel = document.getElementById("selectRelationType");
  const relVal = sel ? sel.value : "";

  let url = `/api/relationships?limit=500`;
  if (relVal) url += `&relation_type=${encodeURIComponent(relVal)}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    renderRelationshipsTable(data.relationships);

    const countBadge = document.getElementById("relCountBadge");
    if (countBadge) countBadge.textContent = `${data.count} Active Edges`;

    // populate relation types in filter if empty
    if (sel && sel.options.length <= 1 && ontologyData) {
      ontologyData.metadata.relation_types.forEach(rt => {
        const opt = document.createElement("option");
        opt.value = rt;
        opt.textContent = rt;
        sel.appendChild(opt);
      });
      sel.addEventListener("change", loadRelationships);
    }
  } catch (err) {
    console.error("Failed to load relationships:", err);
  }
}

function renderRelationshipsTable(relationships) {
  const tbody = document.querySelector("#tableRelationships tbody");
  if (!tbody) return;
  tbody.innerHTML = relationships.map(r => `
    <tr>
      <td><code style="color:var(--ink-muted);">${r.id}</code></td>
      <td><a href="javascript:void(0)" onclick="inspectEntity('${r.source_id}')" style="color:var(--river-deep); font-weight:600;">${r.source_id}</a> <span style="font-size:11px; color:var(--ink-muted);">(${r.source_type})</span></td>
      <td><span class="badge badge-status">── ${r.relation_type} ──►</span></td>
      <td><a href="javascript:void(0)" onclick="inspectEntity('${r.target_id}')" style="color:var(--river-deep); font-weight:600;">${r.target_id}</a> <span style="font-size:11px; color:var(--ink-muted);">(${r.target_type})</span></td>
      <td><span style="font-family:var(--font-mono); font-size:11px;">${JSON.stringify(r.metadata || {})}</span></td>
    </tr>
  `).join("");
}

// 4. OPERATIONAL EVENTS
async function loadEvents() {
  const sevSel = document.getElementById("selectEventSeverity");
  const statSel = document.getElementById("selectEventStatus");
  let url = "/api/events";
  const params = [];
  if (sevSel && sevSel.value) params.push(`severity=${sevSel.value}`);
  if (statSel && statSel.value) params.push(`status=${statSel.value}`);
  if (params.length) url += "?" + params.join("&");

  try {
    const res = await fetch(url);
    const data = await res.json();
    renderEvents(data.events);
  } catch (err) {
    console.error("Failed to load events:", err);
  }
}

function renderEvents(events) {
  const container = document.getElementById("eventListContainer");
  if (!container) return;
  if (!events.length) {
    container.innerHTML = `<div class="card">No operational events match current filters.</div>`;
    return;
  }

  container.innerHTML = events.map(ev => `
    <div class="event-item severity-${ev.severity}">
      <div class="event-header">
        <div>
          ${getProvenanceBadge(ev.provenance)}
          <span class="badge badge-local">${ev.source}</span>
          <span class="badge" style="background:#EBE7DB;">${ev.event_type}</span>
          <span style="font-family:var(--font-mono); font-size:11px; color:var(--ink-muted); margin-left:8px;">${new Date(ev.timestamp).toLocaleString()}</span>
        </div>
        <div>
          <span class="badge" style="background:${ev.severity === 'CRITICAL' ? 'var(--alert)' : ev.severity === 'HIGH' ? 'var(--rust)' : 'var(--gold)'}; color:#fff;">${ev.severity}</span>
          <span class="badge badge-status">${ev.status}</span>
        </div>
      </div>
      <div class="event-title">Impact on Entity: <a href="javascript:void(0)" onclick="inspectEntity('${ev.entity_id}')" style="color:var(--river-deep);">${ev.entity_id}</a> (${ev.entity_type})</div>
      <p style="margin:6px 0 10px; font-size:13.5px;"><strong>Operational Impact:</strong> ${ev.operational_impact}</p>
      
      <div class="state-diff-box">
        <div class="state-diff-col">
          <h5>Expected Baseline State</h5>
          <pre style="margin:0; font-size:11px;">${JSON.stringify(ev.expected_state, null, 2)}</pre>
        </div>
        <div class="state-diff-col observed">
          <h5 style="color:var(--alert);">Observed Operational Reality</h5>
          <pre style="margin:0; font-size:11px; color:var(--alert);">${JSON.stringify(ev.observed_state, null, 2)}</pre>
        </div>
      </div>

      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px; font-size:12.5px;">
        <div><strong>Financial Exposure:</strong> <span style="font-family:var(--font-mono); font-weight:600; color:var(--alert);">$${(ev.financial_impact || 0).toLocaleString()} ${ev.currency}</span></div>
        <div><strong>Required Decision:</strong> <em>${ev.required_decision || "Under monitoring"}</em></div>
      </div>

      ${ev.evidence_ids && ev.evidence_ids.length ? `
        <div style="margin-top:10px; padding-top:8px; border-top:1px solid var(--rule-light); font-size:12px; color:var(--ink-soft); display:flex; align-items:center; gap:6px;">
          <strong>Source Evidence Grounding:</strong>
          ${ev.evidence_ids.map(eid => `<a href="javascript:void(0)" onclick="inspectEvidence('${eid}')" style="color:var(--river-deep); font-family:var(--font-mono); font-weight:600; text-decoration:underline;">[EVI: ${eid}]</a>`).join(" ")}
        </div>
      ` : ''}
    </div>
  `).join("");
}

const selectEventSeverity = document.getElementById("selectEventSeverity");
if (selectEventSeverity) selectEventSeverity.addEventListener("change", loadEvents);
const selectEventStatus = document.getElementById("selectEventStatus");
if (selectEventStatus) selectEventStatus.addEventListener("change", loadEvents);

// 5. DECISIONS
async function loadDecisions() {
  try {
    const res = await fetch("/api/decisions");
    const data = await res.json();
    renderDecisions(data.decisions);
  } catch (err) {
    console.error("Failed to load decisions:", err);
  }
}

function renderDecisions(decisions) {
  const container = document.getElementById("decisionsContainer");
  if (!container) return;
  container.innerHTML = decisions.map(d => {
    const isEscalated = d.status === "ESCALATED";
    return `
    <div class="card ${isEscalated ? 'card-accent-alert' : 'card-accent-gold'}" style="margin-bottom:24px;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
        <div>
          ${getProvenanceBadge(d.provenance)}
          <span class="badge badge-local">${d.decision_id}</span>
          <span class="badge badge-status">Owner: ${d.decision_owner}</span>
          <span class="badge" style="background:${isEscalated ? 'var(--alert)' : 'var(--river-soft)'}; color:${isEscalated ? '#fff' : 'var(--river-deep)'}; font-weight:600;">
            ${d.status}
          </span>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-family:var(--font-mono); font-size:11px; color:var(--ink-muted);">${new Date(d.timestamp).toLocaleString()}</span>
          ${!isEscalated ? `
            <button class="btn btn-secondary" style="padding:2px 8px; font-size:11px;" onclick="promptEscalateDecision('${d.decision_id}', '${d.decision_owner}')">🚨 Escalate</button>
          ` : ''}
        </div>
      </div>

      ${isEscalated ? `
        <div style="background:var(--alert-soft); border-left:4px solid var(--alert); padding:10px 14px; margin-bottom:12px; border-radius:3px;">
          <strong style="color:var(--alert); font-size:12.5px;">⚠️ DECISION TIMEOUT ESCALATION TRIGGERED</strong><br>
          <span style="font-size:13px; color:var(--ink);">${d.escalation_reason || 'Decision pending past timeout threshold.'}</span><br>
          <div style="font-family:var(--font-mono); font-size:11px; color:var(--alert); margin-top:4px;">
            Target Escalation Role: <strong>${d.escalation_target_role || 'role-executive'}</strong>
          </div>
        </div>
      ` : ''}

      <h3 style="font-family:var(--font-serif); margin:4px 0 10px;">Triggered by Operational Event: <code>${d.triggering_event_id}</code></h3>
      
      <div class="pipeline-step-container">
        <!-- 1. Observation -->
        <div class="pipeline-step">
          <div class="pipeline-step-badge">1. OBSERVATION</div>
          <div style="font-size:13px;">Event triggered: <code>${d.triggering_event_id}</code></div>
          ${d.evidence_ids && d.evidence_ids.length ? `
            <div style="margin-top:8px; font-size:12px; color:var(--ink-soft); display:flex; align-items:center; gap:6px;">
              <strong>Source Evidence Grounding:</strong>
              ${d.evidence_ids.map(eid => `<a href="javascript:void(0)" onclick="inspectEvidence('${eid}')" style="color:var(--river-deep); font-family:var(--font-mono); font-weight:600; text-decoration:underline;">[EVI: ${eid}]</a>`).join(" ")}
            </div>
          ` : ''}
        </div>

        <!-- 2. Context -->
        <div class="pipeline-step">
          <div class="pipeline-step-badge">2. CONTEXT & CONSTRAINTS</div>
          <div style="font-size:12.5px; font-family:var(--font-mono); background:#FAFAF7; padding:8px; border-radius:3px;">
            ${JSON.stringify(d.context, null, 2)}
          </div>
        </div>

        <!-- 3. Decision & Options -->
        <div class="pipeline-step" style="border-left:3px solid var(--river);">
          <div class="pipeline-step-badge">3. DECISION & EVALUATED OPTIONS (${d.options.length} Candidate Paths)</div>
          <div style="margin:8px 0;">
            ${d.options.map(opt => `
              <div style="background:#FAF9F5; border:1px solid var(--rule-light); padding:10px 12px; margin-bottom:8px; border-radius:3px;">
                <div style="font-weight:600; font-size:13.5px; display:flex; justify-content:space-between;">
                  <span>${opt.title}</span>
                  <span style="font-family:var(--font-mono); font-size:11px;">Est. Cost: $${opt.cost_estimate_usd.toLocaleString()} | Delay: ${opt.delay_hours_estimate}h</span>
                </div>
                <p style="font-size:12.5px; margin:4px 0 6px;">${opt.description}</p>
                <div style="font-size:11.5px; color:var(--ink-soft);">
                  <strong>Pros:</strong> ${opt.pros.join("; ")} | <strong>Cons:</strong> ${opt.cons.join("; ")}
                </div>
              </div>
            `).join("")}
          </div>
          <div style="background:var(--river-soft); padding:10px 12px; border-radius:3px;">
            <strong style="color:var(--river-deep);">Recommendation:</strong> ${d.recommendation}
          </div>
        </div>

        <!-- 4. Authorized Action -->
        <div class="pipeline-step" style="border-left:3px solid var(--gold);">
          <div class="pipeline-step-badge">4. AUTHORIZED ACTION</div>
          ${d.authorized_action ? `
            <div style="font-size:13px;">
              <strong>Action:</strong> <code>${d.authorized_action.action_type}</code> on <code>${d.authorized_action.target_entity_id}</code><br>
              <strong>Authorized By:</strong> ${d.authorized_action.authorized_by} (${new Date(d.authorized_action.authorized_at).toLocaleString()})<br>
              <div style="font-family:var(--font-mono); font-size:11px; margin-top:4px;">Parameters: ${JSON.stringify(d.authorized_action.parameters)}</div>
            </div>
          ` : `<div style="font-style:italic; color:var(--ink-muted);">Pending authorization</div>`}
        </div>

        <!-- 5. Outcome -->
        <div class="pipeline-step" style="border-left:3px solid var(--green);">
          <div class="pipeline-step-badge" style="color:var(--green);">5. OUTCOME & AUDIT CONFIRMATION</div>
          ${d.outcome ? `
            <div style="font-size:13px;">
              <strong>Result:</strong> ${d.outcome.observed_result}<br>
              <strong>Actual Latency:</strong> ${d.outcome.actual_latency_hours} hours | <strong>Financial Delta:</strong> $${d.outcome.financial_delta_usd.toLocaleString()}<br>
              <strong>KPI Impact:</strong> ${d.outcome.kpi_impact} | <strong>Audit Verified:</strong> ${d.outcome.verified ? 'YES' : 'NO'}
            </div>
          ` : `<div style="font-style:italic; color:var(--ink-muted);">Pending measurement</div>`}
        </div>
      </div>
    </div>
  `).join("");
}

async function promptEscalateDecision(decisionId, currentOwner) {
  const targetRole = prompt(`Escalate decision ${decisionId} to role:`, "role-executive");
  if (!targetRole) return;
  const reason = prompt("Enter escalation rationale / operational reason:", `Escalated from ${currentOwner} due to high business risk and unresolved latency.`);
  if (!reason) return;
  try {
    const res = await fetch(`/api/decisions/${decisionId}/escalate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ escalated_to: targetRole, reason: reason }),
    });
    if (!res.ok) throw new Error("Failed to escalate decision");
    alert(`Decision ${decisionId} successfully escalated to ${targetRole} and logged to tamper-evident audit trail.`);
    await loadDecisions();
  } catch (err) {
    alert("Error: " + err.message);
  }
}


// 6. WORKFLOWS
async function loadWorkflows() {
  try {
    const res = await fetch("/api/workflows");
    const data = await res.json();
    renderWorkflows(data.workflows);
  } catch (err) {
    console.error("Failed to load workflows:", err);
  }
}

function renderWorkflows(workflows) {
  const container = document.getElementById("workflowsContainer");
  if (!container) return;
  container.innerHTML = workflows.map(wf => `
    <div class="card card-accent-river">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <h3 class="card-title">${wf.title}</h3>
        <span class="badge badge-local">${wf.corridor}</span>
      </div>
      <p style="font-size:13px; margin:4px 0 16px; color:var(--ink-soft);">${wf.description}</p>
      
      <div class="workflow-chain">
        ${wf.nodes.map(n => `
          <div class="workflow-node">
            <div class="node-step-num">Step ${n.step} · ${n.entity_type}</div>
            <div class="node-name"><a href="javascript:void(0)" onclick="inspectEntity('${n.entity_id}')" style="color:var(--ink);">${n.name}</a></div>
            <div class="node-action">${n.action}</div>
          </div>
        `).join("")}
      </div>

      <div style="margin-top:18px; padding:10px 12px; background:var(--rust-soft); border-left:3px solid var(--rust); font-size:12.5px;">
        <strong style="color:var(--rust);">Active Bottleneck:</strong> ${wf.active_bottleneck}
      </div>
    </div>
  `).join("");
}

// 7. AI OPPORTUNITIES
async function loadOpportunities() {
  try {
    const res = await fetch("/api/opportunities");
    const data = await res.json();
    renderOpportunities(data.opportunities);
  } catch (err) {
    console.error("Failed to load opportunities:", err);
  }
}

function renderOpportunities(opportunities) {
  const container = document.getElementById("opportunitiesContainer");
  if (!container) return;
  container.innerHTML = opportunities.map(opp => {
    const prio = opp.prioritization;
    const isPilot = prio && prio.candidate_for_pilot;
    return `
    <div class="card card-accent-rust">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
          ${getProvenanceBadge(opp.provenance)}
          ${isPilot ? '<span class="pilot-tag" style="margin-left:6px;">★ CANDIDATE FOR FDE PILOT</span>' : ''}
          <h3 class="card-title" style="margin-top:6px;">${escapeHtml(opp.title)}</h3>
        </div>
        <span class="badge" style="background:${opp.deployment_complexity === 'LOW' ? 'var(--green-soft)' : 'var(--gold-soft)'}; color:var(--ink);">Complexity: ${opp.deployment_complexity}</span>
      </div>
      <div class="card-subtitle">Workflow: <strong>${escapeHtml(opp.workflow)}</strong></div>
      
      <div style="background:#FAF9F5; border:1px solid var(--rule-light); padding:10px 12px; margin-bottom:12px; font-size:13px;">
        <div style="margin-bottom:6px;"><strong style="color:var(--alert);">Operational Bottleneck:</strong> ${escapeHtml(opp.bottleneck)}</div>
        <div><strong style="color:var(--ink);">Business Impact:</strong> ${escapeHtml(opp.business_impact)} (Est. Annual Payoff: <strong>$${opp.estimated_payoff_annual_usd.toLocaleString()}</strong>)</div>
      </div>

      ${prio ? `
        <div class="prio-breakdown">
          <div class="prio-header">
            <span style="font-weight:600; font-size:12px; color:var(--river-deep);">FDE Opportunity Prioritization</span>
            <span style="font-family:var(--font-mono); font-weight:700; font-size:13px; color:var(--river-deep);">${prio.composite_score.toFixed(1)} / 10</span>
          </div>
          <div class="prio-row">
            <span class="prio-label">1. Economic Leverage</span>
            <div class="prio-bar-track"><div class="prio-bar-fill" style="width:${prio.economic_leverage.dimension_score * 10}%;"></div></div>
            <span class="prio-val">${prio.economic_leverage.dimension_score.toFixed(1)}</span>
          </div>
          <div class="prio-row">
            <span class="prio-label">2. Ops Characteristics</span>
            <div class="prio-bar-track"><div class="prio-bar-fill" style="width:${prio.operational_characteristics.dimension_score * 10}%;"></div></div>
            <span class="prio-val">${prio.operational_characteristics.dimension_score.toFixed(1)}</span>
          </div>
          <div class="prio-row">
            <span class="prio-label">3. Feasibility</span>
            <div class="prio-bar-track"><div class="prio-bar-fill" style="width:${prio.deployment_feasibility.dimension_score * 10}%;"></div></div>
            <span class="prio-val">${prio.deployment_feasibility.dimension_score.toFixed(1)}</span>
          </div>
          <div class="prio-row">
            <span class="prio-label">4. Strategic Value</span>
            <div class="prio-bar-track"><div class="prio-bar-fill" style="width:${prio.strategic_value.dimension_score * 10}%;"></div></div>
            <span class="prio-val">${prio.strategic_value.dimension_score.toFixed(1)}</span>
          </div>
          <div style="font-size:11px; color:var(--ink-muted); margin-top:6px; font-style:italic;">
            ${escapeHtml(prio.recommendation_rationale)}
          </div>
        </div>
      ` : ''}

      <div style="font-size:13px; margin-bottom:12px;">
        <strong>Proposed AI Intervention:</strong> ${escapeHtml(opp.proposed_ai_intervention)}
      </div>

      <div style="background:var(--river-soft); padding:10px 12px; border-radius:3px; margin-bottom:10px; font-size:12.5px;">
        <strong style="color:var(--river-deep);">Human-in-the-Loop Requirement:</strong> ${escapeHtml(opp.human_in_the_loop_requirement)}
      </div>

      <div style="font-size:12px; color:var(--ink-soft); margin-bottom:6px;">
        <strong>Failure Modes & Guardrails:</strong>
        <ul style="margin:4px 0 8px; padding-left:18px;">
          ${opp.failure_modes.map(f => `<li>${escapeHtml(f)}</li>`).join("")}
        </ul>
      </div>

      <div style="display:flex; justify-content:space-between; font-family:var(--font-mono); font-size:11px; color:var(--ink-muted); border-top:1px solid var(--rule-light); padding-top:8px;">
        <span>Target KPI: <strong>${escapeHtml(opp.kpi)}</strong></span>
        <span>Decision: <code>${escapeHtml(opp.decision_involved)}</code></span>
      </div>
    </div>
    `;
  }).join("");
}

// 8. AGENT SPECIFICATIONS & ADAPTER COMPILER
async function loadAgentSpecs() {
  try {
    const res = await fetch("/api/agent-specs");
    const data = await res.json();
    renderAgentSpecs(data.agent_specifications);
  } catch (err) {
    console.error("Failed to load agent specs:", err);
  }
}

function renderAgentSpecs(specs) {
  const container = document.getElementById("agentSpecsContainer");
  if (!container) return;
  container.innerHTML = specs.map(spec => `
    <div class="card card-accent-river" style="margin-bottom:24px;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
        <div>
          <span class="badge badge-local">${spec.spec_id}</span>
          <span class="badge badge-status">Version ${spec.version}</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <button class="btn btn-primary" style="padding:4px 10px; font-size:11px;" onclick="viewGeminiScaffold('${spec.spec_id}')">🐍 View Gemini Python Scaffold</button>
          <span style="font-family:var(--font-mono); font-size:11px;">Target Compiler:</span>
          <select class="select-filter" style="min-width:140px; padding:4px 8px; font-size:11.5px;" onchange="exportPlatformManifest('${spec.spec_id}', this.value)">
            <option value="gemini">Gemini Enterprise</option>
            <option value="openai">OpenAI Assistants</option>
            <option value="microsoft">Azure AI Foundry</option>
            <option value="databricks">Databricks Mosaic</option>
          </select>
        </div>
      </div>

      <h3 style="font-family:var(--font-serif); font-size:20px; margin:4px 0 6px;">${spec.title}</h3>
      <p style="font-size:13.5px; margin:0 0 12px; color:var(--ink-soft);">${spec.objective}</p>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px; font-size:12.5px;">
        <div style="background:#FAF9F5; padding:10px 12px; border:1px solid var(--rule-light);">
          <strong>Trigger:</strong> ${spec.trigger}<br>
          <strong style="margin-top:6px; display:inline-block;">Inputs & Documents:</strong>
          <ul style="margin:2px 0 0; padding-left:18px;">
            ${spec.inputs.map(i => `<li>${i}</li>`).join("")}
          </ul>
        </div>
        <div style="background:#FAF9F5; padding:10px 12px; border:1px solid var(--rule-light);">
          <strong style="color:var(--river-deep);">Human Approval Requirements:</strong>
          <p style="margin:4px 0 6px;">${spec.human_approval_requirements}</p>
          <strong>Evaluation Criteria:</strong>
          <ul style="margin:2px 0 0; padding-left:18px;">
            ${spec.evaluation_criteria.map(c => `<li>${c}</li>`).join("")}
          </ul>
        </div>
      </div>

      <div style="margin-bottom:14px;">
        <div class="pane-eyebrow">Platform-Agnostic Tools (${spec.tools.length})</div>
        <div class="table-wrap">
          <table class="fde-table">
            <thead>
              <tr>
                <th>Tool Name</th>
                <th>Description</th>
                <th>Access Policy</th>
                <th>Parameters</th>
              </tr>
            </thead>
            <tbody>
              ${spec.tools.map(t => `
                <tr>
                  <td><code>${t.name}</code></td>
                  <td>${t.description}</td>
                  <td><span class="badge ${t.read_only ? 'badge-local' : 'badge-status'}">${t.read_only ? 'READ-ONLY' : 'MUTATES STATE'}</span></td>
                  <td><pre style="margin:0; font-size:10.5px;">${JSON.stringify(t.input_schema)}</pre></td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Live Compiler Manifest Display -->
      <div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <div class="pane-eyebrow">Enterprise Manifest Output (Click compiler select above)</div>
          <span class="badge badge-local" id="manifestBadge-${spec.spec_id}">gemini_enterprise</span>
        </div>
        <pre class="code-json" id="manifestCode-${spec.spec_id}">Loading initial manifest...</pre>
      </div>
    </div>
  `).join("");

  // Load initial Gemini manifests
  specs.forEach(s => exportPlatformManifest(s.spec_id, "gemini"));
}

async function exportPlatformManifest(specId, platform) {
  const codeEl = document.getElementById(`manifestCode-${specId}`);
  const badgeEl = document.getElementById(`manifestBadge-${specId}`);
  if (badgeEl) badgeEl.textContent = platform;
  if (codeEl) codeEl.textContent = "Compiling platform manifest...";

  try {
    const res = await fetch(`/api/agent-specs/${specId}/export/${platform}`);
    const data = await res.json();
    if (codeEl) {
      codeEl.textContent = JSON.stringify(data.manifest, null, 2);
    }
  } catch (err) {
    if (codeEl) codeEl.textContent = "Error compiling manifest: " + err;
  }
}

// 11. FDE PILOT ENGINE & DEPLOYMENT BLUEPRINTS
async function loadPilots() {
  try {
    const res = await fetch("/api/pilots");
    if (!res.ok) throw new Error("Failed to load pilots");
    const data = await res.json();
    renderPilots(data.pilots);
  } catch (err) {
    console.error("Failed to load pilots:", err);
  }
}

function renderPilots(pilots) {
  const container = document.getElementById("pilotsContainer");
  if (!container) return;
  if (!pilots || !pilots.length) {
    container.innerHTML = `<div class="card">No pilots currently registered.</div>`;
    return;
  }

  const platformDisplayMap = {
    "gemini_enterprise": "Google Cloud / Gemini Enterprise",
    "gemini": "Google Cloud / Gemini Enterprise",
    "microsoft_azure_ai_foundry": "Microsoft Azure AI Foundry",
    "microsoft": "Microsoft Azure AI Foundry",
    "azure": "Microsoft Azure AI Foundry",
    "openai_assistants": "OpenAI Enterprise Assistants",
    "openai": "OpenAI Enterprise Assistants",
    "databricks_mosaic_ai": "Databricks Mosaic AI",
    "databricks": "Databricks Mosaic AI"
  };

  container.innerHTML = pilots.map(pilot => {
    const econ = pilot.economics_summary || {};
    const platformLabel = platformDisplayMap[pilot.selected_platform] || pilot.selected_platform;

    return `
      <div class="card card-accent-river" style="margin-bottom:24px; border-left:4px solid var(--river);">
        <!-- Pilot Header Bar -->
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; flex-wrap:wrap; gap:8px;">
          <div>
            <span class="badge badge-local" style="font-weight:700;">${escapeHtml(pilot.pilot_id)}</span>
            <span class="badge badge-status">${escapeHtml(pilot.status)}</span>
            <span class="badge" style="background:var(--gold-soft); color:var(--gold); border:1px solid var(--gold); font-weight:600;">Opp: ${escapeHtml(pilot.opportunity_id)}</span>
            ${getProvenanceBadge(pilot.provenance)}
          </div>
          <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
            <span style="font-family:var(--font-mono); font-size:11px; color:var(--ink-muted);">Platform Substrate:</span>
            <select class="select-filter" style="font-size:12px; font-weight:600; padding:4px 8px;" onchange="switchPilotPlatform('${pilot.pilot_id}', this.value)">
              <option value="gemini_enterprise" ${pilot.selected_platform.includes('gemini') ? 'selected' : ''}>Google Cloud / Gemini Enterprise</option>
              <option value="microsoft_azure_ai_foundry" ${pilot.selected_platform.includes('microsoft') || pilot.selected_platform.includes('azure') ? 'selected' : ''}>Microsoft Azure AI Foundry</option>
              <option value="openai_assistants" ${pilot.selected_platform.includes('openai') ? 'selected' : ''}>OpenAI Enterprise Assistants</option>
              <option value="databricks_mosaic_ai" ${pilot.selected_platform.includes('databricks') ? 'selected' : ''}>Databricks Mosaic AI</option>
            </select>
            <button class="btn btn-primary" style="padding:4px 10px; font-size:11.5px;" onclick="viewPilotDeploymentPlan('${pilot.pilot_id}')">⚡ Platform Plan</button>
          </div>
        </div>

        <!-- Title & Subtitle -->
        <h3 style="font-family:var(--font-serif); font-size:22px; margin:6px 0 4px; color:var(--river-deep);">${escapeHtml(pilot.title)}</h3>
        <div style="font-size:13px; color:var(--ink-muted); margin-bottom:12px;">
          <strong>Target Enterprise:</strong> <span style="color:var(--ink);">${escapeHtml(pilot.customer)}</span> · 
          <strong>Workflow:</strong> <span style="color:var(--ink-soft);">${escapeHtml(pilot.workflow)}</span> · 
          <strong>Decision Owner:</strong> <span style="color:var(--river-deep); font-weight:600;">${escapeHtml(pilot.decision_owner)}</span>
        </div>

        <!-- Financial Bridge & ROI Meter -->
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(170px, 1fr)); gap:12px; margin-bottom:16px; background:#FAF9F5; padding:14px; border:1px solid var(--rule-light); border-radius:4px;">
          <div>
            <div class="pane-eyebrow">Baseline Annual Cost</div>
            <div style="font-family:var(--font-mono); font-size:17px; font-weight:700; color:var(--alert);">$${Number(econ.baseline_annual_total_usd || 0).toLocaleString()}</div>
            <div style="font-size:10.5px; color:var(--ink-muted); margin-top:2px;">Labor: $${Number(econ.baseline_annual_labor_usd || 0).toLocaleString()} · Exceptions: $${Number(econ.baseline_annual_exception_usd || 0).toLocaleString()}</div>
          </div>
          <div>
            <div class="pane-eyebrow">Target Post-Intervention</div>
            <div style="font-family:var(--font-mono); font-size:17px; font-weight:700; color:var(--ink-soft);">$${Number(econ.target_annual_total_usd || 0).toLocaleString()}</div>
            <div style="font-size:10.5px; color:var(--ink-muted); margin-top:2px;">Target labor & reduced exceptions</div>
          </div>
          <div>
            <div class="pane-eyebrow">Addressable Annual Savings</div>
            <div style="font-family:var(--font-mono); font-size:17px; font-weight:700; color:var(--green);">$${Number(econ.addressable_annual_savings_usd || 0).toLocaleString()}</div>
            <div style="font-size:10.5px; color:var(--ink-muted); margin-top:2px;">$${Number(econ.savings_per_shipment_usd || 0).toFixed(2)} / decision unit</div>
          </div>
          <div>
            <div class="pane-eyebrow">Net 1st-Year ROI & Payback</div>
            <div style="font-family:var(--font-mono); font-size:17px; font-weight:700; color:var(--river-deep);">${Number(econ.expected_roi_percentage || 0).toFixed(1)}%</div>
            <div style="font-size:10.5px; color:var(--green); font-weight:600; margin-top:2px;">Payback: ${econ.payback_period_months} months</div>
          </div>
        </div>

        <!-- Scope & Human Governance Grid -->
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:16px; font-size:12.5px;">
          <div style="background:#FFFFFF; padding:12px; border:1px solid var(--rule-light); border-radius:3px;">
            <div class="pane-eyebrow">Operational Decision Point</div>
            <div style="margin-top:4px; font-weight:600; color:var(--ink);">${escapeHtml(pilot.decision)}</div>
            <div style="margin-top:6px; color:var(--ink-soft);"><strong>Trigger:</strong> ${escapeHtml(pilot.trigger)}</div>
            <div style="margin-top:6px; color:var(--ink-soft);"><strong>Scope:</strong> ${escapeHtml(pilot.pilot_scope)} (${escapeHtml(pilot.pilot_duration)})</div>
          </div>
          <div style="background:#FFFFFF; padding:12px; border:1px solid var(--rule-light); border-radius:3px;">
            <div class="pane-eyebrow" style="color:var(--alert);">Mandatory Human Approval Gate</div>
            <div style="margin-top:4px; font-weight:600; color:var(--river-deep);">${escapeHtml(pilot.human_approval_required)}</div>
            <div style="margin-top:6px; color:var(--ink-soft);"><strong>Rollback Condition:</strong> ${escapeHtml(pilot.rollback_condition)}</div>
          </div>
        </div>

        <!-- Footer Actions Bar -->
        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--rule-light); padding-top:12px; flex-wrap:wrap; gap:8px;">
          <div style="font-size:12px; color:var(--ink-muted);">
            Active Execution Substrate: <strong style="color:var(--ink);">${escapeHtml(platformLabel)}</strong>
          </div>
          <div style="display:flex; gap:8px;">
            <button class="btn btn-secondary" onclick="viewPilotEconomics('${pilot.pilot_id}')">📊 Inspect Economic Bridge</button>
            <button class="btn btn-primary" onclick="viewPilotBrief('${pilot.pilot_id}')">📑 View 12-Section Client Brief</button>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

async function switchPilotPlatform(pilotId, platform) {
  try {
    const res = await fetch(`/api/pilots/${pilotId}/platform`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ platform }),
    });
    if (!res.ok) throw new Error("Failed to switch platform");
    await loadPilots();
  } catch (err) {
    alert("Error updating platform: " + err.message);
  }
}

async function viewPilotBrief(pilotId) {
  const backdrop = document.getElementById("drawerBackdrop");
  const titleEl = document.getElementById("drawerEntityName");
  const idEl = document.getElementById("drawerEntityId");
  const typeEl = document.getElementById("drawerEntityType");
  const bodyEl = document.getElementById("drawerBody");

  backdrop.style.display = "flex";
  typeEl.textContent = "CLIENT-READY FDE DEPLOYMENT BRIEF";
  titleEl.textContent = "Compiling 12-Section Brief...";
  idEl.textContent = pilotId;
  bodyEl.innerHTML = "<div class='card'>Generating comprehensive executive brief from domain ontology & economic model...</div>";

  try {
    const res = await fetch(`/api/pilots/${pilotId}/brief?format=markdown`);
    if (!res.ok) throw new Error("Failed to generate brief");
    const data = await res.json();

    titleEl.textContent = data.title;
    idEl.textContent = `${data.pilot_id} · ${data.customer} · 12-Section Executive Brief`;

    bodyEl.innerHTML = `
      <div style="background:#FFF3CD; border:1px solid #FFEEBA; color:#856404; padding:10px 14px; border-radius:4px; margin-bottom:14px; font-weight:600; font-size:12px; display:flex; align-items:center; gap:8px;">
        <span>⚠️</span>
        <span>Illustrative — based on synthetic AIDESA data, pending client-specific baseline validation</span>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; background:var(--river-soft); padding:10px 14px; border-radius:4px; flex-wrap:wrap; gap:8px;">
        <div style="font-size:12px; color:var(--river-deep);">
          <strong>Executive Ready:</strong> Full 12-section operational brief grounded in Paraguayan export telemetry.
        </div>
        <div style="display:flex; gap:8px;">
          <button class="btn btn-secondary" style="padding:4px 10px; font-size:11px;" onclick="copyBriefMarkdown()">📋 Copy Markdown</button>
          <button class="btn btn-primary" style="padding:4px 10px; font-size:11px;" onclick="downloadBriefMarkdown('${data.pilot_id}')">⬇️ Download .md</button>
        </div>
      </div>
      <div id="briefMarkdownContent" style="display:none;">${escapeHtml(data.brief_markdown)}</div>
      <div class="brief-markdown-rendered" style="background:#FFFFFF; padding:20px; border:1px solid var(--rule-light); border-radius:4px; font-size:13px; line-height:1.7; max-height:580px; overflow-y:auto;">
        ${renderMarkdownToHtml(data.brief_markdown)}
      </div>
    `;
  } catch (err) {
    bodyEl.innerHTML = `<div style="color:var(--alert);">Failed to load brief: ${escapeHtml(err.message)}</div>`;
  }
}

function copyBriefMarkdown() {
  const content = document.getElementById("briefMarkdownContent")?.textContent || "";
  navigator.clipboard.writeText(content);
  alert("12-Section Deployment Brief copied to clipboard!");
}

function downloadBriefMarkdown(pilotId) {
  const content = document.getElementById("briefMarkdownContent")?.textContent || "";
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${pilotId}-deployment-brief.md`;
  a.click();
  URL.revokeObjectURL(url);
}

function renderMarkdownToHtml(md) {
  if (!md) return "";
  let html = escapeHtml(md);

  // Headers
  html = html.replace(/^# (.*$)/gim, '<h1 style="font-family:var(--font-serif); font-size:22px; color:var(--river-deep); margin:16px 0 8px; border-bottom:2px solid var(--river); padding-bottom:6px;">$1</h1>');
  html = html.replace(/^## (.*$)/gim, '<h2 style="font-family:var(--font-serif); font-size:17px; color:var(--river-deep); margin:18px 0 6px; border-bottom:1px solid var(--rule-light); padding-bottom:4px;">$1</h2>');
  html = html.replace(/^### (.*$)/gim, '<h3 style="font-family:var(--font-serif); font-size:14.5px; color:var(--ink); margin:12px 0 4px;">$1</h3>');

  // Blockquotes
  html = html.replace(/^> (.*$)/gim, '<blockquote style="border-left:4px solid var(--gold); background:var(--gold-soft); padding:8px 12px; margin:10px 0; font-size:12.5px;">$1</blockquote>');

  // Code blocks
  html = html.replace(/```([a-z]*)\n([\s\S]*?)```/gim, '<pre class="code-json" style="max-height:220px; font-size:11.5px; margin:10px 0;">$2</pre>');
  html = html.replace(/`([^`]+)`/g, '<code style="font-family:var(--font-mono); background:#ECE8DD; padding:1px 4px; border-radius:2px; font-size:12px;">$1</code>');

  // Bold / Italic
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

  // Lists
  html = html.replace(/^- (.*$)/gim, '<li style="margin-left:18px;">$1</li>');

  // Horizontal rules
  html = html.replace(/^---$/gim, '<hr style="border:none; border-top:1px solid var(--rule-light); margin:14px 0;">');

  // Newlines
  html = html.replace(/\n\n/g, '<br><br>');

  return html;
}

async function viewPilotEconomics(pilotId) {
  const backdrop = document.getElementById("drawerBackdrop");
  const titleEl = document.getElementById("drawerEntityName");
  const idEl = document.getElementById("drawerEntityId");
  const typeEl = document.getElementById("drawerEntityType");
  const bodyEl = document.getElementById("drawerBody");

  backdrop.style.display = "flex";
  typeEl.textContent = "OPERATIONAL ECONOMIC BRIDGE";
  titleEl.textContent = "Calculating Economic Bridge...";
  idEl.textContent = pilotId;
  bodyEl.innerHTML = "<div class='card'>Loading step-by-step mathematical calculation...</div>";

  try {
    const res = await fetch(`/api/pilots/${pilotId}/economic-bridge`);
    if (!res.ok) throw new Error("Failed to calculate economic bridge");
    const data = await res.json();
    const s = data.summary;
    const inp = data.inputs;
    const assumptions = data.assumptions_ledger || [];
    const sensitivity = data.sensitivity_analysis || {};
    const scenarios = sensitivity.scenarios || {};

    titleEl.textContent = `Economic Bridge: ${data.title}`;
    idEl.textContent = `${data.pilot_id} · ${data.customer}`;

    bodyEl.innerHTML = `
      <!-- Synthetic Data Watermark Banner -->
      <div style="background:#FFF3CD; border:1px solid #FFEEBA; color:#856404; padding:10px 14px; border-radius:4px; margin-bottom:14px; font-weight:600; font-size:12px; display:flex; align-items:center; gap:8px;">
        <span>⚠️</span>
        <span>${escapeHtml(data.watermark || 'Illustrative — based on synthetic AIDESA data, pending client-specific baseline validation')}</span>
      </div>

      <!-- Executive ROI Callout -->
      <div style="background:var(--river-soft); border:1px solid var(--river); border-radius:4px; padding:14px; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
          <div>
            <div class="pane-eyebrow" style="color:var(--river-deep);">Net First-Year Enterprise ROI ($)</div>
            <div style="font-family:var(--font-mono); font-size:24px; font-weight:700; color:var(--river-deep);">$${Number(s.first_year_net_roi_usd).toLocaleString()} <span style="font-size:16px;">(${s.expected_roi_percentage}%)</span></div>
            <div style="font-size:11px; color:var(--ink-soft); margin-top:2px;">Total 1st-Year Outlay: $${Number(data.total_first_year_investment_usd || (inp.pilot_implementation_cost_usd + inp.annual_software_subscription_usd)).toLocaleString()}</div>
          </div>
          <div style="text-align:right;">
            <div class="pane-eyebrow" style="color:var(--river-deep);">Payback Period</div>
            <div style="font-family:var(--font-mono); font-size:20px; font-weight:700; color:var(--green);">${s.payback_period_months} Months</div>
          </div>
        </div>
      </div>

      <!-- Assumptions Ledger Table -->
      <div class="pane-eyebrow" style="margin-bottom:6px;">Assumptions Ledger (Parameter Traceability & Source Rationale)</div>
      <table class="fde-table" style="font-size:12px; margin-bottom:20px;">
        <thead>
          <tr>
            <th>Parameter</th>
            <th style="text-align:right;">Baseline Value</th>
            <th>Unit</th>
            <th>Operational Source / Rationale</th>
          </tr>
        </thead>
        <tbody>
          ${assumptions.map(item => `
            <tr>
              <td><code style="font-weight:600;">${escapeHtml(item.parameter)}</code></td>
              <td style="text-align:right; font-family:var(--font-mono); font-weight:600;">${typeof item.value === 'number' ? item.value.toLocaleString() : escapeHtml(String(item.value))}</td>
              <td style="color:var(--ink-muted); font-size:11px;">${escapeHtml(item.unit)}</td>
              <td style="font-size:11.5px; color:var(--ink-soft);">${escapeHtml(item.source_or_rationale)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>

      <!-- Sensitivity Analysis Range Table -->
      <div class="pane-eyebrow" style="margin-bottom:6px;">Sensitivity Analysis Matrix (±20% Sensitivity Range)</div>
      <table class="fde-table" style="font-size:12px; margin-bottom:20px;">
        <thead>
          <tr>
            <th>Scenario</th>
            <th style="text-align:right;">Volume</th>
            <th style="text-align:right;">Touch Time</th>
            <th style="text-align:right;">Error Rate</th>
            <th style="text-align:right;">Annual Savings</th>
            <th style="text-align:right;">Net 1st-Yr ROI</th>
            <th style="text-align:right;">ROI %</th>
            <th style="text-align:right;">Payback</th>
          </tr>
        </thead>
        <tbody>
          ${Object.values(scenarios).map(sc => `
            <tr style="${sc.label && sc.label.includes('Mid') ? 'background:#F0F7F4; font-weight:600;' : ''}">
              <td><strong>${escapeHtml(sc.label)}</strong></td>
              <td style="text-align:right; font-family:var(--font-mono);">${Number(sc.annual_volume).toLocaleString()}</td>
              <td style="text-align:right; font-family:var(--font-mono);">${sc.target_manual_minutes}m</td>
              <td style="text-align:right; font-family:var(--font-mono);">${sc.target_exception_rate_pct}%</td>
              <td style="text-align:right; font-family:var(--font-mono); color:var(--green);">$${Number(sc.addressable_annual_savings_usd).toLocaleString()}</td>
              <td style="text-align:right; font-family:var(--font-mono);">$${Number(sc.net_first_year_roi_usd).toLocaleString()}</td>
              <td style="text-align:right; font-family:var(--font-mono); font-weight:700; color:var(--river-deep);">${sc.roi_percentage}%</td>
              <td style="text-align:right; font-family:var(--font-mono);">${sc.payback_period_months} mo</td>
            </tr>
          `).join("")}
        </tbody>
      </table>

      <!-- 10 Calculation Steps -->
      <div class="pane-eyebrow" style="margin-bottom:6px;">Auditable 10-Step Mathematical Bridge</div>
      <table class="fde-table" style="font-size:12px;">
        <thead>
          <tr>
            <th>Step</th>
            <th>Metric Name</th>
            <th>Formula</th>
            <th style="text-align:right;">Calculated Value</th>
          </tr>
        </thead>
        <tbody>
          ${data.calculation_steps.map(step => `
            <tr>
              <td style="font-family:var(--font-mono); font-weight:700;">#${step.step}</td>
              <td style="font-weight:600;">${escapeHtml(step.name)}</td>
              <td style="font-size:11px; color:var(--ink-muted); font-family:var(--font-mono);">${escapeHtml(step.formula)}</td>
              <td style="text-align:right; font-family:var(--font-mono); font-weight:700; color:${step.step === 6 || step.step === 9 ? 'var(--green)' : 'var(--ink)'};">
                ${step.result_usd !== undefined ? '$' + Number(step.result_usd).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2}) : (step.roi_percentage + '%')}
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  } catch (err) {
    bodyEl.innerHTML = `<div style="color:var(--alert);">Failed to calculate economics: ${escapeHtml(err.message)}</div>`;
  }
}

async function viewPilotDeploymentPlan(pilotId) {
  const backdrop = document.getElementById("drawerBackdrop");
  const titleEl = document.getElementById("drawerEntityName");
  const idEl = document.getElementById("drawerEntityId");
  const typeEl = document.getElementById("drawerEntityType");
  const bodyEl = document.getElementById("drawerBody");

  backdrop.style.display = "flex";
  typeEl.textContent = "MULTI-PLATFORM DEPLOYMENT PROOF";
  titleEl.textContent = "Loading Deployment Plan...";
  idEl.textContent = pilotId;
  bodyEl.innerHTML = "<div class='card'>Compiling platform-specific deployment architecture...</div>";

  try {
    const res = await fetch(`/api/pilots/${pilotId}/deployment-plan`);
    if (!res.ok) throw new Error("Failed to load deployment plan");
    const data = await res.json();
    const plan = data.deployment_plan;
    const val = data.validation || {};

    titleEl.textContent = `${plan.platform_display_name} Deployment Architecture`;
    idEl.textContent = `${data.pilot_id} · Substrate: ${data.platform}`;

    bodyEl.innerHTML = `
      ${val.valid ? `
        <div style="background:#EBF7EE; border:1px solid #C3E6CB; color:#155724; padding:8px 12px; border-radius:4px; margin-bottom:14px; font-size:12px; display:flex; justify-content:space-between; align-items:center;">
          <span><strong>✓ Platform Plan Schema Validated:</strong> 100% compliant with enterprise invariants.</span>
          <span style="font-family:var(--font-mono); font-size:11px;">${escapeHtml(val.schema_doc || '')}</span>
        </div>
      ` : `
        <div style="background:#FCE8E6; border:1px solid #F5C6CB; color:#721C24; padding:8px 12px; border-radius:4px; margin-bottom:14px; font-size:12px;">
          <strong>⚠️ Schema Validation Warnings:</strong> ${(val.errors || []).join(", ")}
        </div>
      `}

      <div style="background:var(--paper-card); border:1px solid var(--rule-light); border-radius:4px; padding:14px; margin-bottom:14px;">
        <div style="font-size:12.5px; line-height:1.8;">
          <strong>Runtime Framework:</strong> <code>${escapeHtml(plan.runtime_framework)}</code><br>
          <strong>Model Deployment:</strong> <code>${escapeHtml(plan.model_deployment)}</code><br>
          <strong>Architecture Pattern:</strong> <span>${escapeHtml(plan.architecture_pattern)}</span>
        </div>
      </div>

      <div class="pane-eyebrow" style="margin-bottom:6px;">Concrete Integration Steps</div>
      <ol style="font-size:12.5px; padding-left:20px; line-height:1.7; margin-bottom:16px;">
        ${plan.integration_steps.map(s => `<li>${escapeHtml(s)}</li>`).join("")}
      </ol>

      <div class="pane-eyebrow" style="margin-bottom:6px; color:var(--alert);">Human-in-the-Loop Governance Gate</div>
      <div class="evidence-quote" style="font-size:12.5px; margin-bottom:16px; border-left-color:var(--alert);">
        ${escapeHtml(plan.human_in_loop_mechanism)}
      </div>

      <div class="pane-eyebrow" style="margin-bottom:6px;">Required Credentials & Environment Variables</div>
      <pre class="code-json" style="font-size:11.5px; margin-bottom:14px;">${plan.credentials_and_env.join("\n")}</pre>

      <div class="pane-eyebrow" style="margin-bottom:6px;">Verification Command</div>
      <pre class="code-json" style="font-size:11.5px;">${escapeHtml(plan.verification_command)}</pre>
    `;

  } catch (err) {
    bodyEl.innerHTML = `<div style="color:var(--alert);">Failed to load deployment plan: ${escapeHtml(err.message)}</div>`;
  }
}

// 12. KPIS
async function loadKPIs() {
  try {
    const res = await fetch("/api/kpis");
    const data = await res.json();
    renderKPIs(data.kpis);
  } catch (err) {
    console.error("Failed to load KPIs:", err);
  }
}

function renderKPIs(kpis) {
  const container = document.getElementById("kpisContainer");
  if (!container) return;
  container.innerHTML = kpis.map(k => `
    <div class="card card-accent-gold">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <span class="badge badge-local">${k.category}</span>
        <span class="badge" style="background:${k.trend === 'IMPROVING' ? 'var(--green-soft)' : k.trend === 'DEGRADING' ? 'var(--alert-soft)' : 'var(--gold-soft)'}; color:var(--ink);">
          ${k.trend}
        </span>
      </div>
      <h4 class="card-title" style="margin-top:10px;">${k.name}</h4>
      
      <div style="display:flex; align-items:baseline; gap:12px; margin:12px 0 8px;">
        <span style="font-family:var(--font-serif); font-size:32px; font-weight:700; color:var(--river-deep);">${k.current_value}</span>
        <span style="font-size:14px; color:var(--ink-muted);">/ Target: ${k.target_value} ${k.unit_of_measure}</span>
      </div>

      <p style="font-size:12.5px; color:var(--ink-soft); margin:0;">
        ${k.attributes && k.attributes.notes ? k.attributes.notes : `Operational metric code: ${k.metric_code}`}
      </p>
    </div>
  `).join("");
}

// 10. SYNTHETIC COMPANY
async function loadCompany() {
  try {
    const res = await fetch("/api/company");
    const data = await res.json();
    renderCompany(data);
  } catch (err) {
    console.error("Failed to load company:", err);
  }
}

function renderCompany(comp) {
  const container = document.getElementById("companyOverviewContainer");
  if (!container) return;
  const org = comp.organization || {};

  container.innerHTML = `
    <div class="grid-2" style="margin-bottom:24px;">
      <div class="card card-accent-river">
        <h3 class="card-title">${org.name || "AIDESA S.A."}</h3>
        <div class="card-subtitle">RUC: <code>${org.ruc || "80099412-4"}</code> | Legal Form: ${org.legal_form || "S.A."}</div>
        <p style="font-size:13.5px;">Primary Paraguayan agro-industrial and export processing enterprise with crushing, oil refining, and cross-border container packaging facilities.</p>
        <div style="font-size:13px; line-height:1.7;">
          <strong>Export Regime:</strong> ${org.export_regime}<br>
          <strong>Total Verified Headcount:</strong> <span style="font-family:var(--font-mono); font-weight:700; color:var(--river-deep);">${comp.headcount} Employees</span><br>
          <strong>Active Facilities:</strong> ${comp.facilities.length} operational plants<br>
          <strong>Suppliers Network:</strong> ${comp.supplier_count} approved suppliers<br>
          <strong>Customers Network:</strong> ${comp.customer_count} international buyers (Brazil & Argentina)
        </div>
      </div>

      <div class="card card-accent-gold">
        <h3 class="card-title">IT & Operational Systems of Record</h3>
        <p class="card-subtitle">Real-world operational landscape without artificial unified software</p>
        <div style="font-size:13px;">
          ${(comp.it_systems || []).map(sys => `
            <div style="border-bottom:1px solid var(--rule-light); padding:6px 0;">
              <strong style="color:var(--river-deep);">${sys.system}</strong> (${sys.category})<br>
              <span style="font-size:12px; color:var(--ink-soft);">${sys.scope}</span>
            </div>
          `).join("")}
        </div>
      </div>
    </div>

    <!-- Facilities -->
    <div style="margin-bottom:28px;">
      <div class="pane-eyebrow">Operating Infrastructure</div>
      <h3 style="font-family:var(--font-serif); margin:0 0 12px;">Physical Facilities</h3>
      <div class="grid-2">
        ${comp.facilities.map(fac => `
          <div class="card card-accent-river">
            <h4 class="card-title">${fac.name}</h4>
            <div class="card-subtitle">${fac.city}, Dpto. ${fac.department} | ${fac.facility_type}</div>
            <p style="font-size:13px;">Throughput Capacity: <strong>${fac.throughput_capacity_tpd} Tons/Day</strong> | Barge Dock: <strong>${fac.has_barge_dock ? 'YES' : 'NO'}</strong></p>
            <div style="font-family:var(--font-mono); font-size:11px; color:var(--ink-soft);">
              Coordinates: Lat ${fac.coordinates.lat}, Lng ${fac.coordinates.lng}
            </div>
          </div>
        `).join("")}
      </div>
    </div>

    <!-- Org Chart Headcount Distribution -->
    <div>
      <div class="pane-eyebrow">Human Capital (Exactly 250 Headcount)</div>
      <h3 style="font-family:var(--font-serif); margin:0 0 12px;">Headcount Distribution Across Roles</h3>
      <div class="table-wrap">
        <table class="fde-table">
          <thead>
            <tr>
              <th>Role Title</th>
              <th>Department</th>
              <th>Headcount</th>
              <th>Approval Limit (USD)</th>
              <th>Critical Responsibilities</th>
            </tr>
          </thead>
          <tbody>
            ${comp.roles.map(r => `
              <tr>
                <td><strong>${r.title}</strong></td>
                <td><span class="badge badge-local">${r.department}</span></td>
                <td><strong style="font-family:var(--font-mono); color:var(--river-deep);">${r.headcount_in_role}</strong></td>
                <td style="font-family:var(--font-mono);">$${(r.approval_threshold_usd || 0).toLocaleString()}</td>
                <td style="font-size:12px; color:var(--ink-soft);">${(r.key_responsibilities || []).join(", ")}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// Global Actions: Reset, Export & Audit Verification
function bindGlobalActions() {
  const auditBadge = document.getElementById("auditChainBadge");
  if (auditBadge) {
    auditBadge.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/audit/verify");
        const data = await res.json();
        if (data.valid) {
          alert(`✓ Cryptographic Audit Chain Verified (SHA-256)\n\nStatus: 100% Tamper-Free\nTotal Logged Actions: ${data.total_entries}\nHead Hash: ${data.head_hash}`);
        } else {
          alert(`⚠️ AUDIT CHAIN INTEGRITY CORRUPTED!\n\nCorrupted Sequence: ${data.corrupted_sequence}\nReason: ${data.reason}`);
        }
      } catch (err) {
        alert("Failed to verify audit chain: " + err);
      }
    });
  }

  const btnReset = document.getElementById("btnResetSeed");
  if (btnReset) {
    btnReset.addEventListener("click", async () => {
      if (!confirm("Reset FDE Workbench to default synthetic dataset for Agro-Industrial del Este S.A.?")) return;
      try {
        const res = await fetch("/api/company/reset", { method: "POST" });
        const data = await res.json();
        alert("Store reset successfully! " + data.message);
        window.location.reload();
      } catch (err) {
        alert("Failed to reset: " + err);
      }
    });
  }

  const btnExport = document.getElementById("btnExportSnapshot");
  if (btnExport) {
    btnExport.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/snapshot/export");
        const data = await res.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `aidesa_workbench_snapshot_${new Date().toISOString().slice(0,10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
      } catch (err) {
        alert("Export failed: " + err);
      }
    });
  }

  const btnCheckEsc = document.getElementById("btnCheckEscalations");
  if (btnCheckEsc) {
    btnCheckEsc.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/decisions/check-escalations", { method: "POST" });
        const data = await res.json();
        alert(`Checked all decisions. ${data.escalated_count} decision(s) timed out and escalated.`);
        await loadDecisions();
      } catch (err) {
        alert("Failed to check escalations: " + err);
      }
    });
  }

  // Drawer Close
  const btnCloseDrawer = document.getElementById("btnCloseDrawer");
  const drawerBackdrop = document.getElementById("drawerBackdrop");
  if (btnCloseDrawer && drawerBackdrop) {
    btnCloseDrawer.addEventListener("click", () => {
      drawerBackdrop.style.display = "none";
    });
    drawerBackdrop.addEventListener("click", (e) => {
      if (e.target === drawerBackdrop) drawerBackdrop.style.display = "none";
    });
  }
}

// Side Drawer Inspection
async function inspectEntity(entityId) {
  const backdrop = document.getElementById("drawerBackdrop");
  const titleEl = document.getElementById("drawerEntityName");
  const idEl = document.getElementById("drawerEntityId");
  const typeEl = document.getElementById("drawerEntityType");
  const bodyEl = document.getElementById("drawerBody");

  backdrop.style.display = "flex";
  titleEl.textContent = "Loading...";
  idEl.textContent = entityId;
  bodyEl.innerHTML = "Fetching entity graph details...";

  try {
    const res = await fetch(`/api/entities/${entityId}`);
    if (!res.ok) throw new Error("Entity not found");
    const data = await res.json();
    const ent = data.entity;

    typeEl.textContent = ent.entity_type.toUpperCase();
    titleEl.textContent = ent.name;
    idEl.innerHTML = `ID: ${ent.id} · System: ${ent.system_of_record} · ${getProvenanceBadge(ent.provenance)}`;

    bodyEl.innerHTML = `
      <div style="margin-bottom:16px;">
        <div class="pane-eyebrow">Attributes & Metadata</div>
        <pre class="code-json" style="max-height:220px;">${JSON.stringify(ent, null, 2)}</pre>
      </div>

      <div style="margin-bottom:16px;">
        <div class="pane-eyebrow">Outgoing Relationships (${data.outgoing_relationships.length})</div>
        ${data.outgoing_relationships.length ? `
          <ul style="padding-left:18px; margin:4px 0; font-size:12.5px;">
            ${data.outgoing_relationships.map(r => `
              <li>── <strong>${r.relation_type}</strong> ──► <a href="javascript:void(0)" onclick="inspectEntity('${r.target_id}')" style="color:var(--river-deep); font-weight:600;">${r.target_id}</a> <span style="font-size:11px; color:var(--ink-muted);">(${r.target_type})</span></li>
            `).join("")}
          </ul>
        ` : `<div style="font-size:12px; color:var(--ink-muted); font-style:italic;">No outgoing edges</div>`}
      </div>

      <div>
        <div class="pane-eyebrow">Incoming Relationships (${data.incoming_relationships.length})</div>
        ${data.incoming_relationships.length ? `
          <ul style="padding-left:18px; margin:4px 0; font-size:12.5px;">
            ${data.incoming_relationships.map(r => `
              <li>◄── <strong>${r.relation_type}</strong> ── <a href="javascript:void(0)" onclick="inspectEntity('${r.source_id}')" style="color:var(--river-deep); font-weight:600;">${r.source_id}</a> <span style="font-size:11px; color:var(--ink-muted);">(${r.source_type})</span></li>
            `).join("")}
          </ul>
        ` : `<div style="font-size:12px; color:var(--ink-muted); font-style:italic;">No incoming edges</div>`}
      </div>
    `;
  } catch (err) {
    bodyEl.innerHTML = `<div style="color:var(--alert);">Failed to load entity details: ${err.message}</div>`;
  }
}

// Side Drawer Evidence Inspection
async function inspectEvidence(evidenceId) {
  const backdrop = document.getElementById("drawerBackdrop");
  const titleEl = document.getElementById("drawerEntityName");
  const idEl = document.getElementById("drawerEntityId");
  const typeEl = document.getElementById("drawerEntityType");
  const bodyEl = document.getElementById("drawerBody");

  backdrop.style.display = "flex";
  titleEl.textContent = "Loading Evidence...";
  idEl.textContent = evidenceId;
  bodyEl.innerHTML = "Fetching empirical artifact record...";

  try {
    const res = await fetch(`/api/evidence/${evidenceId}`);
    if (!res.ok) throw new Error("Evidence record not found");
    const data = await res.json();
    const evi = data.evidence;

    typeEl.textContent = `EVIDENCE · ${evi.source_type}`;
    titleEl.textContent = evi.source;
    idEl.innerHTML = `ID: ${evi.id} · Confidence: ${(evi.confidence * 100).toFixed(0)}% · ${getProvenanceBadge(evi.provenance)}`;

    const refs = [];
    if (evi.references_entities && evi.references_entities.length) {
      refs.push(`<strong>Referenced Entities:</strong> ` + evi.references_entities.map(eid => `<a href="javascript:void(0)" onclick="inspectEntity('${eid}')" style="color:var(--river-deep); font-weight:600; margin-right:6px;">${eid}</a>`).join(", "));
    }
    if (evi.references_events && evi.references_events.length) {
      refs.push(`<strong>Referenced Events:</strong> ` + evi.references_events.join(", "));
    }
    if (evi.references_decisions && evi.references_decisions.length) {
      refs.push(`<strong>Referenced Decisions:</strong> ` + evi.references_decisions.join(", "));
    }

    bodyEl.innerHTML = `
      <div style="margin-bottom:16px;">
        <div class="pane-eyebrow">Extracted Operational Claim</div>
        <div class="evidence-quote" style="font-size:13px; margin-top:6px;">${escapeHtml(evi.extracted_claim)}</div>
      </div>

      <div style="margin-bottom:16px;">
        <div class="pane-eyebrow">Grounding Telemetry & Origin</div>
        <div style="font-size:12.5px; line-height:1.8;">
          <strong>Source System:</strong> ${escapeHtml(evi.source_system || "N/A")}<br>
          <strong>Observed Timestamp:</strong> <span style="font-family:var(--font-mono);">${new Date(evi.timestamp).toLocaleString()}</span><br>
          <strong>Provenance:</strong> ${getProvenanceBadge(evi.provenance)}<br>
          <strong>Confidence Score:</strong> <span style="font-family:var(--font-mono); font-weight:700; color:var(--river-deep);">${(evi.confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      <div style="margin-bottom:16px;">
        <div class="pane-eyebrow">Linked Operational Graph Objects</div>
        <div style="font-size:12.5px; line-height:1.7;">
          ${refs.length ? refs.join("<br>") : '<span style="color:var(--ink-muted); font-style:italic;">No linked entities/events</span>'}
        </div>
      </div>

      <div>
        <div class="pane-eyebrow">Full Empirical Artifact Payload</div>
        <pre class="code-json" style="max-height:220px;">${JSON.stringify(evi, null, 2)}</pre>
      </div>
    `;
  } catch (err) {
    bodyEl.innerHTML = `<div style="color:var(--alert);">Failed to load evidence details: ${escapeHtml(err.message)}</div>`;
  }
}

// Side Drawer Gemini Python SDK Scaffold Viewer
async function viewGeminiScaffold(specId) {
  const backdrop = document.getElementById("drawerBackdrop");
  const titleEl = document.getElementById("drawerEntityName");
  const idEl = document.getElementById("drawerEntityId");
  const typeEl = document.getElementById("drawerEntityType");
  const bodyEl = document.getElementById("drawerBody");

  backdrop.style.display = "flex";
  titleEl.textContent = "Compiling Gemini Scaffold...";
  idEl.textContent = specId;
  bodyEl.innerHTML = "Generating runnable google-genai deployment code...";

  try {
    const res = await fetch(`/api/agent-specs/${specId}/scaffold/gemini`);
    if (!res.ok) throw new Error("Failed to generate scaffold");
    const data = await res.json();

    typeEl.textContent = `GEMINI ENTERPRISE · PYTHON SDK SCAFFOLD`;
    titleEl.textContent = `${specId} — Production Agent`;
    idEl.textContent = `Model: ${data.model} · Tools: ${data.tools_count} · Platform: Google GenAI SDK`;

    bodyEl.innerHTML = `
      <div style="margin-bottom:14px; background:var(--river-soft); padding:10px 12px; border-radius:3px; font-size:12.5px;">
        <strong style="color:var(--river-deep);">Target Framework:</strong> Official <code>google-genai</code> Python SDK<br>
        <span style="color:var(--ink-soft); font-size:11.5px;">Runnable deployment code with typed function tool definitions, system instructions, and human-in-the-loop review guards.</span>
      </div>

      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <div class="pane-eyebrow">Generated Python Deployment Code</div>
        <button class="btn btn-primary" style="padding:2px 8px; font-size:11px;" onclick="navigator.clipboard.writeText(document.getElementById('scaffoldPythonCode').textContent); alert('Copied Python code to clipboard!');">📋 Copy Code</button>
      </div>
      <pre class="code-json" id="scaffoldPythonCode" style="max-height:400px; font-size:11.5px;">${escapeHtml(data.python_code)}</pre>

      <div style="margin-top:14px;">
        <div class="pane-eyebrow">Installation & Execution</div>
        <pre class="code-json" style="padding:8px 12px; font-size:11px;">pip install ${(data.dependencies || []).join(" ")}
export GEMINI_API_KEY="your-api-key"
python agent_${specId.replace(/-/g, "_")}.py</pre>
      </div>
    `;
  } catch (err) {
    bodyEl.innerHTML = `<div style="color:var(--alert);">Failed to generate scaffold: ${escapeHtml(err.message)}</div>`;
  }
}

function escapeHtml(text) {
  if (!text) return "";
  return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
