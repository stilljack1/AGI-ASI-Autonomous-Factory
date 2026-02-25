# CLAUDE.md — AGI/ASI Autonomous Factory

## Project Overview

This repository implements a **distributed "Hive Mind" architecture** for coordinating autonomous AI agents across multiple cloud platforms. A central orchestrator (intended for AWS EC2) manages connections to multiple specialised agent nodes that run on various hosting services (Render, Railway, Hostinger, etc.).

The system is referred to internally as **Clawdbot** / **AGI-1**.

---

## Repository Structure

```
AGI-ASI-Autonomous-Factory/
├── orchestrator.py      # Central WebSocket server — the "brain"
├── agent_node.py        # Generic agent runtime (simulation mode)
├── role_library.json    # 30+ role definitions with missions, authority, and KPIs
├── deploy_role.sh       # One-shot bash installer that writes and starts a live agent
├── install_agent.sh     # Minimal installer that launches the existing agent_node.py
├── .gitignore           # Ignores __pycache__/, *.log, .env
└── README.md            # Quick-start guide
```

---

## Architecture

### Components

| Component | File | Hosting target | Role |
|---|---|---|---|
| **Orchestrator** | `orchestrator.py` | AWS EC2 | WebSocket server; registers agents, routes commands, exposes admin console |
| **Agent Node** (sim) | `agent_node.py` | Render / Railway / Hostinger | Connects to orchestrator, receives `EXECUTE` messages, returns simulated results |
| **Agent Node** (live) | embedded in `deploy_role.sh` | Any remote host | Same as above but executes instructions as real shell commands via `subprocess.getoutput` |
| **Role Library** | `role_library.json` | N/A (data file) | Canonical definitions for all 30+ agent roles |

### Communication Protocol

All communication is **WebSocket** (`ws://`, port `8765`, unencrypted by default).

Message types:

| Direction | Type | Payload fields |
|---|---|---|
| Agent → Orchestrator (init) | — (raw JSON) | `token`, `role` |
| Orchestrator → Agent | `HANDSHAKE` | `status`, `system_prompt` |
| Orchestrator → Agent | `EXECUTE` | `instruction` |
| Agent → Orchestrator | — (raw JSON) | `role`, `result` |

### Authentication

A single shared secret is passed at connect time:
- Environment variable: `HIVE_SECRET_KEY` (defaults to `"default_secret_key"` — **must be changed in production**)
- Passed as `token` in the initial JSON handshake

---

## Role Library (`role_library.json`)

Each role entry has four fields:

```json
"<role_key>": {
  "location": "<hosting platform>",
  "mission":  "<primary objective>",
  "authority": "<what the agent can control>",
  "kpis":     "<success metrics>"
}
```

### Full Role Roster (32 roles)

| Key | Location | Primary mission |
|---|---|---|
| `backend_engineer` | Render | High-concurrency APIs / FastAPI |
| `frontend_engineer` | Railway | React/TypeScript UI |
| `project_manager` | GitHub | Agile workflow orchestration |
| `product_manager` | GitHub | PRDs and feature prioritisation |
| `data_engineer` | AWS EC2 | ETL pipelines / stream processing |
| `data_scientist` | AWS DynamoDB | Predictive modelling |
| `data_analyst` | Hostinger | BI dashboards |
| `ai_researcher` | AWS | AGI alignment research |
| `customer_rep` | Hostinger | User support / NPS |
| `chief_data_officer` | App/Play Store | Data governance / app analytics |
| `prompt_engineer` | AWS | System prompt versioning |
| `product_market_fit` | GitHub | Competitor and market analysis |
| `social_media_manager` | Hostinger | Platform engagement |
| `digital_marketing` | Hostinger | Paid/organic acquisition |
| `chief_of_staff` | AWS EC2 | CEO proxy / cross-dept coordination |
| `safety_alignment` | AWS | Ethical guardrails / bias detection |
| `ux_ui_engineer` | Railway | UX design / Figma |
| `sales_agent` | Hostinger | Enterprise sales / pipeline |
| `fundraising_agent` | AWS | Investor relations |
| `executive_assistant` | Hostinger | CEO calendar / admin |
| `cloud_engineer` | AWS | VPC / IAM / cost optimisation |
| `qa_engineer` | Render | Regression testing / coverage |
| `eval_simulation` | AWS | Adversarial stress testing |
| `brand_manager` | Hostinger | Brand guidelines / PR review |
| `pr_manager` | Hostinger | Media relations / crisis comms |
| `content_writer` | Hostinger | Docs / blogs / SEO |
| `copy_writer` | Hostinger | Ad copy / landing pages |
| `designer` | Railway | Visual assets / collateral |
| `content_manager` | Hostinger | Editorial calendar |
| `growth_manager` | App Store | Viral growth / referral loops |
| `revenue_agent` | App Store | Monetisation / LTV |
| `business_intelligence` | Hostinger | Executive-level data synthesis |
| `coo_agent` | GitHub | Operational efficiency / scaling |
| `cyber_security_agent` | AWS | Real-time threat monitoring |

The `ROLE_DEFINITIONS` dict in `orchestrator.py` contains a shorter, inline subset of these roles (8 roles). The canonical, extended set lives in `role_library.json`.

---

## Deployment Workflows

### 1. Start the Orchestrator (Brain)

```bash
export HIVE_SECRET_KEY="<your-strong-secret>"
python3 orchestrator.py
```

The server listens on `0.0.0.0:8765`. An interactive admin console accepts commands in the form:

```
<role>: <instruction>      # Target a single agent
all: <instruction>         # Broadcast to every connected agent
```

### 2a. Deploy an Agent — Simulation Mode (`install_agent.sh`)

Installs dependencies and starts the existing `agent_node.py` in background:

```bash
./install_agent.sh <ROLE_NAME> <ORCHESTRATOR_IP> <TOKEN>
# Example:
./install_agent.sh backend_engineer 10.0.0.1 my_secret
```

The agent runs in simulation mode: instructions are acknowledged but not actually executed.

### 2b. Deploy an Agent — Full Deployment Script (`deploy_role.sh`)

Writes a new `agent_node.py` to `~/clawdbot_role/` on the target host and starts it:

```bash
./deploy_role.sh <ROLE> <CONTROL_SERVER_IP> <AUTH_TOKEN>
```

> **CRITICAL SECURITY NOTE**: The agent written by `deploy_role.sh` uses
> `subprocess.getoutput(task['instruction'])` to execute **any shell command**
> received from the orchestrator verbatim. This means any party who controls
> the orchestrator (or can send a valid `EXECUTE` message on the WebSocket) has
> **unauthenticated remote code execution (RCE)** on every host running this
> agent. Treat the `HIVE_SECRET_KEY` as a root-level credential. The default
> value `"default_secret_key"` must never be used in any real deployment.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `HIVE_SECRET_KEY` | `"default_secret_key"` | Shared auth token between orchestrator and all agents — **change this** |

---

## Key Conventions

### Python Style
- Standard library (`asyncio`, `websockets`, `json`, `os`, `sys`, `subprocess`) — no third-party packages beyond `websockets`.
- No type annotations in the current codebase.
- Agent nodes are designed to be **stateless** and **self-reconnecting** (5 s retry loop in `agent_node.py`).

### JSON Schemas
- Role keys in `role_library.json` use `snake_case`.
- Every role object must include exactly four fields: `location`, `mission`, `authority`, `kpis`.

### Shell Scripts
- Scripts expect positional arguments (`$1`, `$2`, `$3`) — no flags.
- Exit early with code `1` and a usage message if required arguments are missing.
- Background processes are started with `nohup … > agent.log 2>&1 &`.
- Log output goes to `agent.log` (excluded by `.gitignore`).

### Git
- `master` is the main branch.
- Feature/task branches follow the pattern `claude/<slug>-<session-id>`.
- `.env` files and `*.log` files are gitignored.

---

## Security Considerations for AI Assistants

1. **Do not change `HIVE_SECRET_KEY` to any guessable value** when modifying configuration.
2. **Do not add `subprocess` / `os.system` / `eval` calls** to the simulation (`agent_node.py`) that would execute instruction strings as system commands.
3. **Do not open the WebSocket to public internet** without TLS (`wss://`) and a strong auth token.
4. The `deploy_role.sh` script already embeds a full RCE pathway — be careful when reasoning about or modifying it.
5. When extending the role library, follow the existing four-field schema and keep role keys `snake_case`.

---

## Running / Testing Locally (Quick Reference)

```bash
# Install the single dependency
pip install websockets

# Terminal 1 — start the brain
python3 orchestrator.py

# Terminal 2 — connect a simulated agent
python3 agent_node.py backend_engineer localhost default_secret_key

# Terminal 1 (admin console) — send a command
backend_engineer: Write a health-check endpoint for /ping
```

No formal test suite exists in the repository at this time.
