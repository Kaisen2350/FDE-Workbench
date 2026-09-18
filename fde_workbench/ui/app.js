/**
 * Paraguay Export Economy FDE Workbench — Client Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  loadOntology();
  loadEntities();
  loadRelationships();
  loadEvents();
  loadDecisions();
  loadWorkflows();
  loadOpportunities();
  loadAgentSpecs();
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
async function loadEntities() {
  const typeSelect = document.getElementById("selectEntityType");
  const searchInput = document.getElementById("searchEntityInput");
  const typeVal = typeSelect ? typeSelect.value : "";
  const searchVal = searchInput ? searchInput.value : "";

  let url = `/api/entities?limit=300`;
  if (typeVal) url += `&type=${encodeURIComponent(typeVal)}`;
  if (searchVal) url += `&search=${encodeURIComponent(searchVal)}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    renderEntitiesTable(data.entities);

    const countBadge = document.getElementById("entityCountBadge");
    if (countBadge) {
      countBadge.textContent = `${data.count} / ${data.total_overall} Entities`;
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
      <td><span style="font-family:var(--font-mono); font-size:11px;">${e.system_of_record}</span></td>
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
          <span class="badge badge-local">${d.decision_id}</span>
          <span class="badge badge-status">Owner: ${d.decision_owner}</span>
          <span class="badge" style="background:${isEscalated ? 'var(--alert)' : 'var(--river-soft)'}; color:${isEscalated ? '#fff' : 'var(--river-deep)'}; font-weight:600;">
            ${d.status}
          </span>
        </div>
        <span style="font-family:var(--font-mono); font-size:11px; color:var(--ink-muted);">${new Date(d.timestamp).toLocaleString()}</span>
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
  container.innerHTML = opportunities.map(opp => `
    <div class="card card-accent-rust">
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <h3 class="card-title">${opp.title}</h3>
        <span class="badge" style="background:${opp.deployment_complexity === 'LOW' ? 'var(--green-soft)' : 'var(--gold-soft)'}; color:var(--ink);">Complexity: ${opp.deployment_complexity}</span>
      </div>
      <div class="card-subtitle">Workflow: <strong>${opp.workflow}</strong></div>
      
      <div style="background:#FAF9F5; border:1px solid var(--rule-light); padding:10px 12px; margin-bottom:12px; font-size:13px;">
        <div style="margin-bottom:6px;"><strong style="color:var(--alert);">Operational Bottleneck:</strong> ${opp.bottleneck}</div>
        <div><strong style="color:var(--ink);">Business Impact:</strong> ${opp.business_impact} (Est. Annual Payoff: <strong>$${opp.estimated_payoff_annual_usd.toLocaleString()}</strong>)</div>
      </div>

      <div style="font-size:13px; margin-bottom:12px;">
        <strong>Proposed AI Intervention:</strong> ${opp.proposed_ai_intervention}
      </div>

      <div style="background:var(--river-soft); padding:10px 12px; border-radius:3px; margin-bottom:10px; font-size:12.5px;">
        <strong style="color:var(--river-deep);">Human-in-the-Loop Requirement:</strong> ${opp.human_in_the_loop_requirement}
      </div>

      <div style="font-size:12px; color:var(--ink-soft); margin-bottom:6px;">
        <strong>Failure Modes & Guardrails:</strong>
        <ul style="margin:4px 0 8px; padding-left:18px;">
          ${opp.failure_modes.map(f => `<li>${f}</li>`).join("")}
        </ul>
      </div>

      <div style="display:flex; justify-content:space-between; font-family:var(--font-mono); font-size:11px; color:var(--ink-muted); border-top:1px solid var(--rule-light); padding-top:8px;">
        <span>Target KPI: <strong>${opp.kpi}</strong></span>
        <span>Decision: <code>${opp.decision_involved}</code></span>
      </div>
    </div>
  `).join("");
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

// 9. KPIS
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
    idEl.textContent = `ID: ${ent.id} · System: ${ent.system_of_record}`;

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

function escapeHtml(text) {
  if (!text) return "";
  return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
