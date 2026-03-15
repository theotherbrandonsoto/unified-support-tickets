# 🗂️ Unified Support Tickets

**Author:** theotherbrandonsoto &nbsp;|&nbsp; [GitHub](https://github.com/theotherbrandonsoto) &nbsp;|&nbsp; [LinkedIn](https://www.linkedin.com/in/hirebrandonsoto/)

*Built with assistance from Claude.*

> 🔗 **Part of a connected portfolio.** The customer universe in this project (user IDs, plan types, churn status) is drawn from the same data model as [metrics-store](https://github.com/theotherbrandonsoto/metrics-store), simulating what a real multi-system analytics environment looks like.

---

## 📌 Executive Summary

### The Business Problem
Seven independent support programs operated in complete isolation — each with its own schema, status vocabulary, timezone handling, and data owner. There was no way to ask a simple question like "what's our SLA compliance rate across the company?" without manually collecting data from seven different people and reconciling it yourself.

### The Solution
This project consolidates all seven sources into a single unified fact table using a layered dbt pipeline on DuckDB. Each source gets its own staging model that handles field mapping, type normalization, timezone conversion to UTC, and status canonicalization via a seed-based lookup table. The result is one clean, queryable table — 7,000 tickets, zero nulls in critical fields, fully lowercase and UTC-normalized.

### Project Impact
This is the kind of work that looks unglamorous from the outside but unlocks everything downstream. Before consolidation, cross-brand analysis wasn't possible. After, support ops can self-serve, SLA compliance is comparable across brands, and the unified table is ready to feed dashboards, AI workflows, or downstream pipelines — without asking anyone for a data pull first. It demonstrates the ETL judgment that separates analysts who can build reliable data foundations from those who can only consume them.

### Next Steps
In a production environment, this pipeline would ingest directly from source APIs or a shared data warehouse rather than CSVs, with incremental loading to handle new tickets without full reruns. Planned additions include dbt tests for uniqueness and referential integrity, a time-to-resolution fact table for SLA trend analysis, and automated pipeline runs via Airflow or Prefect on a daily schedule.

---

**The Challenges:**
- Different column names for the same concepts (`ticket_number` vs `request_id` vs `ticket_id`)
- Status values with no consistency (`OPEN`, `wip`, `NEW`, `in_progress` all meaning the same thing)
- Timestamps in mixed timezones and formats (including ISO strings)
- Booleans stored as integers in some sources (`1/0` instead of `true/false`)

---

## 🏗️ The Method
```
RAW LAYER (7 source tables)
        ↓
STAGING LAYER (7 normalized models)
  - Field mapping & type normalization
  - Timezone conversion to UTC
  - Status canonicalization via lookup table
        ↓
MART LAYER (1 unified fact table)
  - 7,000 tickets, single source of truth
        ↓
METRICS LAYER (4 pre-aggregated models)
  - SLA compliance, escalation rates, volume, trends
        ↓
MCP SERVER
  - Plain-English queries via Claude Desktop
```

---

## 📁 Project Structure
```
unified-support-tickets/
├── models/
│   ├── staging/          # 7 normalized models (one per source)
│   ├── mart/             # fct_unified_support_tickets (unified fact table)
│   └── metrics/          # Pre-aggregated metric models
├── seeds/
│   └── status_mapping.csv
├── analysis/             # Example SQL queries
└── generate_raw_data.py  # Creates synthetic raw data
```

---

## 📐 Unified Schema

The final `fct_unified_support_tickets` table:

| Column | Type | Description |
|--------|------|-------------|
| `brand` | string | Which of the 7 programs |
| `ticket_id` | string | Unique identifier |
| `received_date` | timestamp | UTC |
| `resolution_date` | timestamp | UTC |
| `ticket_status` | string | open, closed, in_progress, pending |
| `primary_issue` | string | Issue category |
| `root_cause_label` | string | Why it happened |
| `resolution_label` | string | How it was resolved |
| `financial_compensation` | float | Dollar amount issued |
| `escalated_to_management` | boolean | Whether the ticket was escalated beyond frontline support |
| `resolved_within_sla` | boolean | Whether the ticket was resolved within the defined SLA window |
| `customer_id` | string | Unique identifier for the customer who submitted the ticket |

---

## 🔍 Key Insights from the Data

- **BrandB is a clear outlier** — 45.2% SLA compliance vs. 49–53% for all other brands, meaning they miss SLA on more than half their tickets
- **Total financial compensation exposure: $546,420** across 7,000 tickets
- **50.5% of all tickets escalate to management** — a signal that frontline resolution rates are low across the board
- **Issue volume is evenly distributed** across the top 5 categories (865–931 tickets each), meaning brand-level differences aren't driven by issue mix — they reflect genuine operational variance

---

## 🚀 Running the Project

### 1. Set up your environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> **Note for Mac users:** macOS manages its own Python installation and will block system-wide pip installs. Always create a virtual environment first as shown above.

### 2. Generate synthetic raw data
```bash
python3 generate_raw_data.py
```

### 3. Run the dbt pipeline
```bash
dbt seed --profiles-dir .
dbt run --profiles-dir .
```

### 4. Verify it worked
```python
import duckdb
conn = duckdb.connect('./unified_support_tickets.duckdb')
conn.execute('SELECT COUNT(*), COUNT(DISTINCT brand) FROM main_mart.fct_unified_support_tickets').df()
# total_tickets: 7000, brands: 7
```

---

## 🔌 MCP Server — Claude Desktop Integration

This project uses [`mcp-server-duckdb`](https://github.com/hannesrudolph/mcp-server-duckdb) to expose the unified dataset to Claude Desktop for plain-English queries — no custom server code required.

### Prerequisites

`uv` must be installed:
```bash
brew install uv
```

### Setup

Add the following to your Claude Desktop config at `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "unified-support-tickets": {
      "command": "uvx",
      "args": [
        "mcp-server-duckdb",
        "--db-path",
        "/path/to/unified-support-tickets/unified_support_tickets.duckdb"
      ]
    }
  }
}
```

Replace `/path/to/unified-support-tickets/` with the actual path to this repo on your machine. Then fully quit and restart Claude Desktop.

### Example queries in Claude Desktop

- *"Which brand has the worst SLA compliance?"*
- *"What's our total financial compensation exposure by brand?"*
- *"Show me escalation rates by brand"*
- *"Which brands are missing SLA on more than half their tickets?"*

---

## 🛠️ Stack

| Tool | Role |
|------|------|
| **dbt Core** | Data transformation and metrics layer |
| **DuckDB** | Local analytical warehouse |
| **Python** | Synthetic data generation |
| **MCP Server** | Claude Desktop direct connectivity via `mcp-server-duckdb` |

---

## 🔧 Troubleshooting

**`zsh: command not found: python`** — Use `python3` instead. macOS does not alias `python` by default.

**`externally-managed-environment` pip error** — You need a virtual environment. See step 1 of Running the Project above.

**`Catalog 'main' does not exist`** — Run `python3 generate_raw_data.py` first.

**`Model not found`** — Make sure you're passing `--profiles-dir .` to all dbt commands.

**DuckDB file lock** — Close other connections or delete `unified_support_tickets.duckdb` and rerun from step 2.
