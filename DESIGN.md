---
name: FDE Tradecraft & Control Plane
colors:
  primary: "#1C1A17"
  secondary: "#4A463D"
  tertiary: "#1E5850"
  neutral: "#F5F3EC"
  surface: "#FFFFFF"
  surface-subtle: "#ECE8DD"
  border: "#D1CBB8"
  border-light: "#E2DDD0"
  text-primary: "#1C1A17"
  text-secondary: "#4A463D"
  text-muted: "#7A7568"
  river: "#1E5850"
  river-deep: "#123B36"
  river-soft: "#E5EFEB"
  rust: "#9B4A24"
  rust-soft: "#F8EBE3"
  gold: "#8A6D1E"
  gold-soft: "#F6F0DF"
  alert: "#8C2E1F"
  alert-soft: "#F8E5E1"
  success: "#2B6B3F"
  success-soft: "#E8F3EB"
typography:
  display:
    fontFamily: "Source Serif 4"
    fontSize: "2.25rem"
    fontWeight: "700"
    lineHeight: "1.2"
  h1:
    fontFamily: "Source Serif 4"
    fontSize: "1.75rem"
    fontWeight: "700"
    lineHeight: "1.25"
  h2:
    fontFamily: "Source Serif 4"
    fontSize: "1.35rem"
    fontWeight: "600"
    lineHeight: "1.3"
  h3:
    fontFamily: "IBM Plex Sans"
    fontSize: "1.1rem"
    fontWeight: "600"
    lineHeight: "1.4"
  body-lg:
    fontFamily: "IBM Plex Sans"
    fontSize: "1rem"
    fontWeight: "400"
    lineHeight: "1.5"
  body-md:
    fontFamily: "IBM Plex Sans"
    fontSize: "0.875rem"
    fontWeight: "400"
    lineHeight: "1.5"
  body-sm:
    fontFamily: "IBM Plex Sans"
    fontSize: "0.75rem"
    fontWeight: "400"
    lineHeight: "1.4"
  mono-md:
    fontFamily: "IBM Plex Mono"
    fontSize: "0.875rem"
    fontWeight: "500"
    lineHeight: "1.4"
  mono-sm:
    fontFamily: "IBM Plex Mono"
    fontSize: "0.75rem"
    fontWeight: "500"
    lineHeight: "1.4"
  label:
    fontFamily: "IBM Plex Mono"
    fontSize: "0.6875rem"
    fontWeight: "600"
    letterSpacing: "0.12em"
    textTransform: "uppercase"
rounded:
  none: "0px"
  sm: "2px"
  md: "4px"
  lg: "6px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  xxl: "48px"
---

# FDE Tradecraft & Control Plane Design System

> **Aesthetic Philosophy**: Physical Reality meets Journalistic Rigor and Forward Deployed Engineering Tradecraft.
> 
> The Paraguay Export Economy FDE Workbench does not look like generic modern SaaS with bubbly gradients and soft purple shadows. It looks like an authoritative operational command ledger: warm archival paper (`#F5F3EC`), deep carbon ink (`#1C1A17`), Paraná river greens (`#1E5850`), earth rust (`#9B4A24`), and crisp typography combining classical editorial serif titles with monospaced cryptographic and operational telemetry stamps.

---

## 1. Visual Hierarchy & Design Tokens

### 1.1 Color Palette & Semantic Roles
* **Paper Canvas (`#F5F3EC`)**: Warm archival document ground. Gives the application physical gravitas and reduces eye fatigue during multi-hour deployment sessions.
* **Surface Card (`#FFFFFF`)**: Pure document white. Used for data cards, dossiers, decision ledgers, and modal inspectors.
* **Subtle Surface (`#ECE8DD`)**: Soft recessed contrast for table headers, inactive tabs, and secondary sidebars.
* **Editorial Ink (`#1C1A17`)**: High-contrast, razor-sharp typography for primary headlines, table data, and border accents.
* **River Teal (`#1E5850` / Deep `#123B36`)**: Primary brand color representing river corridors (Río Paraguay / Río Paraná), fluvial convoys, navigation waypoints, and the primary critical path.
* **Logistics Rust (`#9B4A24`)**: Terrestrial physical logistics: trucks, weighbridges, silos, and bulk grain transshipment.
* **Customs Gold (`#8A6D1E`)**: Financial and regulatory milestones: DNA SOFIA customs declarations, tariffs, CADEX export certificates, and commercial invoicing.
* **SLA Alert (`#8C2E1F`)**: Critical operational friction: SLA breaches, customs holds, grounding hazards, and escalated human-in-the-loop decisions.
* **Cryptographic Verification (`#2B6B3F`)**: Unbroken SHA-256 hash chains, verified audits, completed sign-offs, and calibrated benchmarks.

### 1.2 Typography Triad
1. **Source Serif 4**: For masthead titles, section headlines, pilot names, and strategic narratives. Imparts archival gravitas and legal/audit weight.
2. **IBM Plex Sans**: For body paragraphs, operator questionnaires, input labels, and interactive button text. Clean, ergonomic, high legibility.
3. **IBM Plex Mono**: For entity IDs (`ship-2026-001`), SHA-256 hashes (`5d9abe...`), SLA clocks (`T+04:12`), hydrometric gauges (`2.45m`), and JSON schema specifications.

### 1.3 Geometry & Elevation
* **Borders**: Sharp 1px solid rules (`#D1CBB8`), with 2px solid carbon ink rules (`#1C1A17`) for primary structural section dividers.
* **Border Radii**: Minimalist `2px` or `4px`. Strictly avoid large rounded pills or bubbly radiuses.
* **Shadows**: None or ultra-flat (`0 1px 3px rgba(0,0,0,0.05)`). Depth is established through subtle paper tint shifts, bordered cards, and hairline dividers rather than diffuse drop shadows.

---

## 2. Core Screen Blueprints for Stitch Canvas

Stitch (`stitch.withgoogle.com`) organizes prototypes as screens arranged across an infinite canvas. Below are the 5 essential screens designed for the FDE Reasoning Plane:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               STITCH INFINITE CANVAS MAP                                │
│                                                                                         │
│  [Screen 1: Critical Path] ──────(Inspect Node)────► [Screen 5: Physical Evidence]      │
│            │                                                    ▲                       │
│            │ (Review Alert)                                     │ (Trace Claim)         │
│            ▼                                                    │                       │
│  [Screen 2: Decision Pipeline] ──(Field Calibrate)─► [Screen 3: Calibration Studio]     │
│            │                                                    │                       │
│            └──────────────(Deploy Platform Spec)────────────────┼───────────────────────┘
│                                                                 ▼
│                                                     [Screen 4: Multi-Platform Adapter]  
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Screen 1: FDE Operational Command Center & Critical Path
* **Canvas Placement**: Center-Top (Primary Entrypoint)
* **Viewport**: Desktop 1440 × 900
* **Header Bar**:
  * Top masthead in `#FFFFFF` with 2px bottom border `#1C1A17`.
  * Left: Label `FORWARD DEPLOYED ENGINEER · DOMAIN & OPERATIONAL MODELING`, title `Paraguay Export Economy FDE Workbench`, subtitle `Physical Reality · Cross-Border Corridors · Operational Events · Decision Pipelines`.
  * Right: Monospaced status pill `AIDESA S.A.`, Green badge `Audit: SHA-256 Verified (281 blocks)`, and `Export Snapshot` button.
* **Key Components**:
  1. **Curated Critical Path Ribbon**: 6-node horizontal step pipeline connected by directional arrow rules:
     * `Commercial Contract` ➔ `Truck Transport` ➔ `Customs Dispatch` ➔ `Port Terminal` ➔ `River Barge Convoy` ➔ `Export Settlement`
  2. **Active Corridor Map Widget**: Schematic rail/river corridor connecting Ciudad del Este (Puente de la Amistad) through Coronel Oviedo to Villeta Port on the Paraguay River, featuring active hydrometric gauge levels (`Asunción: 1.82m - Caution`).
  3. **Live KPI Strip**: 4-column cards with serif metrics:
     * `Annual Tonnage`: 450,000 MT
     * `Average Truck Turnaround`: 4.2 hrs
     * `Customs Friction Index`: 6.5%
     * `Fluvial Convoy Draft`: 9.5 ft (Max allowed: 10.0 ft)

---

### Screen 2: Decision Pipeline & Escalation Control Room
* **Canvas Placement**: Center-Middle
* **Viewport**: Desktop 1440 × 900
* **Header**: "Operational Event Stream & Human-in-the-Loop Decision Escalation"
* **Key Components**:
  1. **SLA Trigger Sweep Bar**:
     * Banner with indicator: "Deterministic Sweep Engine — Local-first on-demand execution. Zero unobservable background daemons."
     * Button `⚡ Run Decision Sweep (SLA Threshold: 4.0h)`.
     * Live head hash ticker: `Head: c7d45fef84d08f... (SHA-256 unbroken)`.
  2. **Three-Column Kanban / State Board**:
     * **Pending (`DECISION_PENDING`)**: Cards showing time elapsed, countdown timer, priority badge, and affected entity. E.g., `dec-2026-005` (Customs Valuation Variance, pending 4h 12m).
     * **Escalated (`ESCALATED`)**: Highlighted with 3px alert red left border (`#8C2E1F`), escalation target role `role-executive` / `role-operations-director`, and automated escalation reason.
     * **Resolved (`APPROVED` / `REJECTED`)**: Monospaced sign-off timestamps, operator identity, and linked SHA-256 audit entry ID.
  3. **Detail Drawer**: Slide-over panel revealing decision context, economic risk impact, and linked source evidence documents.

---

### Screen 3: Field Calibration Studio & Unanchored Brief Engine
* **Canvas Placement**: Bottom-Right
* **Viewport**: Desktop 1440 × 900
* **Header**: "Field Calibration & Operator Discovery Mode"
* **Key Components**:
  1. **Interview Mode Toggle**:
     * Switch between `Client Executive Mode` (shows verified/modeled numbers) and `Field Calibration Mode` (strictly blanked).
     * Prominent callout banner:
       > **Field Calibration Standard (DoD Invariant 7)**:
       > Numerical baselines, rates, and volume targets are blanked (`_____`) to eliminate cognitive anchoring during operator interviews in Asunción, Villeta, and Ciudad del Este.
  2. **Unanchored Field Calibration Ledger**:
     * Two-column split: Left side shows qualitative operational workflow; right side shows fill-in fields with open-ended prompt questions:
       * `Annual Dispatch Volume`: `_____` ("How many truck dispatches do you process during peak harvest?")
       * `Weighbridge & Customs Touch Time`: `_____` ("From arrival to green channel exit, how long is an operator touching this file?")
       * `Exception & Red-Channel Frequency`: `_____` ("Out of every 100 shipments, how many trigger customs physical inspection or weigh discrepancy?")
       * `Fluvial Demurrage & Lightening Surcharge`: `_____` ("What is the daily penalty when a convoy grounds or waits for terminal discharge?")
  3. **Human Review Warning Badge**: "Mandatory human review: Verify qualitative narrative does not telegraphed ranges before meeting."
  4. **Leave-Behind Export Action**: `Download Field Interview Brief (Markdown)`.

---

### Screen 4: Enterprise Multi-Platform Adapter Studio
* **Canvas Placement**: Bottom-Left
* **Viewport**: Desktop 1440 × 900
* **Header**: "Enterprise Agent Manifest & Platform Deployment Compiler"
* **Key Components**:
  1. **Platform Tabs**:
     * `Google Cloud / Vertex AI` (FunctionDeclaration OpenAPI 3.03)
     * `OpenAI Assistants API` (Strict Tool Calling & Schema Validation)
     * `Microsoft Azure AI` (Semantic Kernel & Human Consent Filter)
     * `Databricks Mosaic AI` (Unity Catalog 3-Tier SQL Function)
  2. **Live Schema Grounding Inspector**:
     * Direct link to verified public documentation URL (e.g. `https://cloud.google.com/vertex-ai/docs/reference/rest/v1beta1/Tool#FunctionDeclaration`).
     * Constraint verification pill: `regex: ^[a-zA-Z0-9_-]{1,64}$`, `type: object`, `additionalProperties: false`.
  3. **Compiled Manifest Split-View**:
     * Left: FDE Agent Domain Specification (`CustomsReconcilerAgent`).
     * Right: Monospaced JSON / YAML code editor with syntax highlighting, ready for enterprise CI/CD deployment.
  4. **Deployment Validation Status**:
     * Green check: `Platform Schema Validation Passed (Grounded against live specs)`.

---

### Screen 5: Physical Reality Source Evidence & Provenance Inspector
* **Canvas Placement**: Top-Right
* **Viewport**: Desktop 1440 × 900
* **Header**: "Source Evidence & Empirical Grounding Registry"
* **Key Components**:
  1. **Provenance Filter Bar**:
     * Filter pills: `All`, `ERP Records (SAP B1)`, `DNA SOFIA Customs Docs`, `River Hydrometry Telemetry`, `Weighbridge Tickets`, `Operator Statements`.
  2. **Evidence Dossier Grid**:
     * Card for each empirical document:
       * Monospaced header: `evi-2026-cde-001`
       * Badge: `CUSTOMER_OBSERVED` / `HIGH_CONFIDENCE (0.95)`
       * System: `DNA SOFIA Customs System - Port of Ciudad del Este`
       * Extracted Claim: `"Trucks experience 180 min average dwell time awaiting phytosanitary SENAVE physical release."`
       * Chain of Custody: Links directly to `Decision: dec-2026-005` and `Shipment: ship-2026-001`.
  3. **Raw Document Viewer Modal**: Simulated facsimile of Paraguayan customs despacho showing stamps, stamps, tariff codes, and signature verification.

---

## 3. Stitch Screen-to-Screen Interaction Flows ("The Stitching")

In Google Stitch, select elements and define interactions to connect screens together into a clickable prototype:

1. **Flow A (The Field Discovery Journey)**:
   * On **Screen 1 (Command Center)**: Click button `Enter Field Calibration Mode` in header.
   * **Stitches to**: **Screen 3 (Calibration Studio)** with animated fade-in transition.
   * On **Screen 3**: Operator answers unanchored prompt for touch time; typing in `18 min` shows real-time sensitivity preview.
   * Click `Export Field Brief` triggers toast: `Generated docs/calibration_customs_recon.md (Zero Leaks Verified)`.

2. **Flow B (The Decision Escalation Journey)**:
   * On **Screen 1 (Command Center)**: Click on red alert badge `1 Pending Decision Breaching SLA`.
   * **Stitches to**: **Screen 2 (Decision Control Room)** focused on `dec-2026-005`.
   * On **Screen 2**: Click `⚡ Run Decision Sweep`.
   * Animate card transition from `DECISION_PENDING` ➔ `ESCALATED` with audit log counter incrementing `281 ➔ 282`.
   * Click `Inspect Evidence` on card stitches directly to **Screen 5 (Evidence Inspector)** highlighting `evi-2026-cde-001`.

3. **Flow C (The Enterprise Deployment Journey)**:
   * On **Screen 1 (Command Center)**: Click `Export Platform Agent Manifest`.
   * **Stitches to**: **Screen 4 (Platform Adapter Studio)**.
   * Toggle between `Google Vertex AI` and `OpenAI Strict` tabs to inspect live JSON schemas and verified public documentation URLs.

---

## 4. Ready-to-Paste Stitch Generation Prompts

Copy and paste these exact prompts directly into the prompt bar at **[stitch.withgoogle.com](https://stitch.withgoogle.com)** to generate high-fidelity screens:

### Prompt for Screen 1: Command Center
```text
A desktop operational command center for a Forward Deployed Engineer (FDE) managing grain export logistics in Paraguay. 
Aesthetic: Tradecraft, warm archival paper (#F5F3EC) background, crisp white (#FFFFFF) card surfaces, deep ink black (#1C1A17) text, and Paraná river teal (#1E5850) accents. Editorial typography combining elegant serif headlines (Source Serif 4) with monospaced data tags (IBM Plex Mono). 
Header masthead with client badge "AIDESA S.A.", cryptographic status pill "Audit: SHA-256 Verified (281 blocks)", and button "Export Snapshot". 
Main layout features a horizontal 6-step Critical Path pipeline: Commercial Contract -> Truck Transport -> Customs Dispatch -> Port Terminal -> River Barge Convoy -> Export Settlement. 
Below it, a 4-card metric row showing Annual Volume (450,000 MT), Truck Dwell (4.2 hrs), Customs Friction (6.5%), and River Draft Level (9.5 ft). Clean 1px solid rules (#D1CBB8), sharp 2px corners, zero bubbly shadows.
```

### Prompt for Screen 2: Decision Pipeline & Escalation Control
```text
An operational decision and escalation dashboard for cross-border logistics in Paraguay.
Design system: Tradecraft theme, warm paper (#F5F3EC), white cards, ink text (#1C1A17), alert crimson accents (#8C2E1F) for SLA breaches. 
Top banner features a deterministic sweep control: "Deterministic Sweep Engine — Local-first on-demand execution. Zero unobservable background daemons" with action button "Run Decision Sweep (SLA Threshold: 4.0h)" and monospaced SHA-256 head hash ticker. 
Main view is a 3-column kanban board: 
1. Pending Decisions (showing countdown SLA timers and pending hours), 
2. Escalated Decisions (highlighted with bold crimson left border #8C2E1F, showing target role "role-executive"), 
3. Resolved Decisions (with green verified checkmarks #2B6B3F and hash-chained audit IDs). 
Card details include decision type, affected truck shipment ID, economic risk value, and link to source evidence.
```

### Prompt for Screen 3: Field Calibration Studio
```text
An unanchored field interview and model calibration studio for an FDE sitting with logistics operators in Ciudad del Este, Paraguay. 
Warm paper (#F5F3EC) editorial layout. 
Prominent notification banner: "Field Calibration Mode (DoD Invariant 7): Numerical baselines and cost targets are blanked to prevent operator anchoring during discovery." 
Split screen interface: 
Left pane displays the qualitative physical workflow for cross-border soybean export through Customs and River Ports. 
Right pane is a Field Calibration Ledger with blank fill-in underlines "baseline: _____" and open-ended interview discovery prompts for the operator: "How many trucks arrive daily?", "How long does manual customs clearance take per truck?", and "What is the cost when a barge grounds on the river?". 
A human review advisory badge warns: "Verify qualitative narrative does not telegraph ranges before interview." 
Action button at bottom: "Export Assumption-Stripped Brief (Markdown)".
```

### Prompt for Screen 4: Enterprise Multi-Platform Adapter
```text
An enterprise AI agent compiler and manifest inspector for 4 cloud platforms. 
Minimalist engineering workbench style with IBM Plex Mono code elements, white card on warm paper background. 
Tabbed navigation for platforms: 
1. Google Cloud / Vertex AI (FunctionDeclaration OpenAPI 3.03), 
2. OpenAI Assistants (Strict Structured Outputs), 
3. Microsoft Azure AI (Semantic Kernel Plugins & Human Consent), 
4. Databricks Mosaic AI (Unity Catalog 3-Tier SQL Functions). 
Top section displays live documentation URL citations with green verification badges. 
Center shows a side-by-side view: left is domain agent metadata and tools; right is a dark-mode monospaced JSON schema viewer showing the generated, fully-validated enterprise manifest. 
Validation indicator at footer: "Manifest schema 100% compliant with vendor API documentation."
```

### Prompt for Screen 5: Physical Reality Evidence Registry
```text
A physical reality evidence registry and document provenance inspector for Paraguayan supply chain operations. 
Warm paper (#F5F3EC) document docket aesthetic. 
Filter bar at top with tags: All, ERP Records (SAP B1), DNA SOFIA Customs Documents, River Hydrometric Telemetry, Weighbridge Tickets. 
Grid of evidence cards, each featuring: 
Monospaced ID tag (e.g. evi-2026-cde-001), Provenance badge (CUSTOMER_OBSERVED or PHYSICAL_INSPECTION), Confidence score meter (95%), Source system name, and extracted operational claim text. 
Clicking a card opens an evidence inspector drawer displaying a simulated physical customs despacho document with official DNA SOFIA stamps, truck license plates, weighbridge ticket readings, and a link to the cryptographic audit trail entry.
```

---

## 5. Implementation Do's and Don'ts for AI Agents & Designers

* **DO** use exact hex tokens: `#F5F3EC` for ground, `#1C1A17` for ink, `#1E5850` for river, `#9B4A24` for logistics rust.
* **DO** combine `Source Serif 4` for headlines and `IBM Plex Mono` for hashes, timers, IDs, and metrics.
* **DO** preserve the unanchored blank fill-in lines (`baseline: _____`) in Field Calibration screens.
* **DO** show explicit SHA-256 hashes and deterministic sweep buttons (no magical automatic spinners).
* **DON'T** use purple gradients, glowing neon borders, or glassmorphism blurs.
* **DON'T** round corners past `4px` or `6px` — keep the layout crisp, planar, and document-like.
* **DON'T** insert speculative synthetic dollar figures into calibration mode screens.
* **DON'T** invent non-existent entity types — keep all references grounded in the settled 24-entity taxonomy.
