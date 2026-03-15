cat > README.md << 'EOF'
# Unified Support Tickets: Data Consolidation Pipeline

> Consolidating 7 siloed support programs into a unified, self-service, AI-queryable dataset

## The Problem

Seven independent support ticket programs operated in silos — each with different schemas, status values, timezone handling, and data types. The compliance team had to ask 7 different people for data. There was no cross-brand visibility, no self-service access, and no unified source of truth.

**The specific messiness:**
- Different column names for the same concepts (`ticket_number` vs `request_id` vs `ticket_id`)
- Status values with no consistency (`OPEN`, `wip`, `NEW`, `in_progress` all meaning the same thing)
- Timestamps in mixed timezones and formats (including ISO strings)
- Booleans stored as integers in some sources (`1/0` instead of `true/false`)

---

## The Solution
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
EOF