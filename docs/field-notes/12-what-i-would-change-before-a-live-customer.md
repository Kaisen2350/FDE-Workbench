# FDE Field Note #12: What I Would Change Before Putting This in Front of a Live Customer

> **Target Channel**: LinkedIn / Substack / X  
> **Repository Anchor**: [`README.md`](https://github.com/[your-username]/fde-workbench/blob/main/README.md)  
> **Key Principle**: *The clearest indicator of engineering seniority isn't claiming your prototype is "enterprise-ready." It is knowing precisely what will break when you move from a local control plane to enterprise infrastructure.*

---

One of the most dangerous tendencies in AI engineering is over-claiming. 

When presenting a reference system, inexperienced teams often claim: *"This is a production-ready enterprise agent system that can be deployed tomorrow."*

An experienced Forward Deployed Engineer looks at the same codebase and asks:
* *Where does authentication live?*
* *How do we reach the on-premise database across corporate firewalls?*
* *What happens when 50 terminals write to the database concurrently?*

The FDE Workbench is an executable demonstration of **operational tradecraft, deterministic control planes, and domain ontologies**. If I were deploying this into a live client engagement tomorrow morning, here are the five architectural changes I would make first:

### 1. Enterprise Identity & Authorization (IAM)
* **Current Reference Implementation**: We use cryptographic SHA-256 tokens and simulated role personas (`CustomsBroker`, `PortCaptain`) to enforce authorization gates.
* **Production Requirement**: Enterprise customers will not accept standalone token managers. This must be integrated directly with **Microsoft Entra ID (Azure AD)**, **Okta**, or **Google Cloud Identity** via OAuth2/OIDC, using JSON Web Tokens (JWT) signed by corporate identity providers with fine-grained RBAC and mTLS (mutual TLS).

### 2. Network Perimeters & Air-Gapped OT
* **Current Reference Implementation**: Ingestion connectors read local filesystem fixtures or simulated CSV exports.
* **Production Requirement**: In live operations, weighbridge scales (Básculas) and silo SCADA systems sit on separate Operational Technology (OT) networks or behind strict perimeter firewalls. Ingestion requires secure DMZ forward proxies, IPsec VPN tunnels, or Google Cloud Private Service Connect / AWS PrivateLink.

### 3. Database Concurrency & High Availability
* **Current Reference Implementation**: The workbench persists into a local SQLite database in WAL (Write-Ahead Logging) mode.
* **Production Requirement**: SQLite is ideal for zero-dependency developer onboarding, CI testing, and edge nodes. But an enterprise processing thousands of concurrent dispatches across multiple river ports requires a distributed, highly available relational store (such as **Cloud SQL for PostgreSQL** or **Spanner**) with automated replication, read replicas, and point-in-time recovery.

### 4. Distributed Context Across Legacy Plumbing
* **Current Reference Implementation**: In-memory span collector (`tracer.py`) calculating p95 latency and token costs across the Python execution tree.
* **Production Requirement**: The moment an action requires an external SOAP XML call to a 2004 customs mainframe or drops a flat file onto an on-premise Windows SMB share, W3C `traceparent` headers are stripped. Production requires custom envelope wrappers to maintain distributed trace context across non-HTTP legacy boundaries.

### 5. 90-Day Shadow Deployment & Drift Calibration
* **Current Reference Implementation**: 50 automated synthetic evaluation scenarios executed locally in CI.
* **Production Requirement**: Before granting an AI advisory agent permission to draft real customs paperwork, the system must run in **Shadow Mode** for 60 to 90 days. During shadow mode, the system drafts recommendations in silence, and an automated pipeline compares its proposals against the human customs broker's actual manual submissions, flagging subtle semantic drift or policy shifts.

---

### The Final Takeaway
The goal of building the FDE Workbench was never to build another generic SaaS app. 

The goal was to demonstrate how an engineer tackles the **last mile of AI**: taking messy, high-friction physical operations, wrapping them in deterministic schemas and explicit provenance, and proving that safety and measurable business value can be built into software before a single model endpoint is called.

---

**Explore the complete repository and documentation**:  
👉 [https://github.com/[your-username]/fde-workbench](https://github.com/[your-username]/fde-workbench)
