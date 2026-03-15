# 🗂️ Unified Support Tickets

**Author:** theotherbrandonsoto | [GitHub](https://github.com/theotherbrandonsoto) | [LinkedIn](https://www.linkedin.com/in/hirebrandonsoto/)

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

## The Method
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

## Project Structure
```
unified-support-tickets/
├── models/
│   ├── staging/          # 7 normalized models (one per source)
│   ├── mart/             # fct_unified_support_tickets (unified fact table)
│   └── metrics/          # Pre-aggregated metric models
├── seeds/
│   └── status_mapping.csv
├── analysis/             # Example SQL queries
├── generate_raw_data.py  # Creates synthetic raw data
└── mcp_server.py         # Claude Desktop integration
```

---

## Unified Schema

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
| `escalated_to_management` | boolean | |
| `resolved_within_sla` | boolean | |
| `customer_id` | string | |

---

## Running the Project
```bash
# Install dependencies
pip install -r requirements.txt

# Generate synthetic raw data (7,000 tickets across 7 sources)
python generate_raw_data.py

# Run the full dbt pipeline
dbt seed --profiles-dir .
dbt run --profiles-dir .
```

Verify it worked:
```python
import duckdb
conn = duckdb.connect('./unified_support_tickets.duckdb')
conn.execute('SELECT COUNT(*), COUNT(DISTINCT brand) FROM main_mart.fct_unified_support_tickets').df()
# total_tickets: 7000, brands: 7
```

---

## MCP Server (Claude Desktop Integration)

The MCP server exposes the unified dataset to Claude Desktop for plain-English queries.

**Start the server:**
```bash
python mcp_server.py
```

**Available tools:**
- `sla_compliance_overview` — SLA compliance by brand (filterable)
- `ticket_volume_by_status` — Ticket counts by status (filterable)
- `escalation_and_compensation` — Escalation rates and $ exposure
- `resolution_patterns` — Top issue/resolution combinations
- `sla_missed_tickets` — Drill into SLA misses

**Example queries in Claude Desktop:**
- "Which brand has the worst SLA compliance?"
- "What's our total financial compensation exposure?"
- "Show me escalation rates by brand"

**Claude Desktop config** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "unified-support-tickets": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

---

## Troubleshooting

**"Catalog 'main' does not exist"** — Run `python generate_raw_data.py` first

**"Model not found"** — Make sure you're passing `--profiles-dir .`

**DuckDB file lock** — Close other connections or delete `unified_support_tickets.duckdb` and rerun

---

## Stack

dbt · DuckDB · SQL · Python · MCP
