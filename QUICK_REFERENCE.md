# Unified Support Tickets — Quick Reference

## 📊 Project Overview

A complete data consolidation + AI-ready analytics solution demonstrating:
- How to unify 7 siloed support programs into one source of truth
- How to make messy data AI-ready for natural language querying
- How to enable self-service analytics for non-technical teams

**Tech Stack:** dbt, SQL, DuckDB, Python (MCP)  
**Key Skills:** Data integration, ETL, analytics engineering, AI-ready data

---

## 🚀 Quick Start

### 1. Generate Data & Build Pipeline
```bash
cd unified-support-tickets
python generate_raw_data.py
dbt seed --profiles-dir .
dbt run --profiles-dir .
```

**Output:** 7,000 unified support tickets + 4 metrics tables

### 2. Start MCP Server (for Claude Desktop)
```bash
python mcp_server.py
# Server runs on localhost:3000
```

### 3. Query in Claude Desktop
```
"What's our SLA compliance by brand?"
"Show me BrandB tickets that missed SLA"
"What are the top escalation drivers?"
```

---

## 📁 Project Structure

```
unified-support-tickets/
├── models/
│   ├── staging/              # 7 staging models (raw → normalized)
│   ├── mart/                 # 1 unified fact table
│   └── metrics/              # 4 pre-calculated metric tables
├── seeds/
│   └── status_mapping.csv    # Status value lookup table
├── analysis/
│   ├── 01_cross_brand_ticket_volume.sql
│   ├── 02_sla_compliance_by_brand.sql
│   └── 03_resolution_patterns.sql
├── generate_raw_data.py      # Creates synthetic messy data
├── mcp_server.py             # Claude Desktop interface
├── dbt_project.yml           # dbt config
├── README.md                 # Full documentation
├── QUICKSTART.md             # Setup instructions
└── MCP_SETUP.md              # Claude Desktop integration
```

---

## 🔄 Data Pipeline

### Raw Layer (Messy)
```
raw_silo_a_program_a1  ← Different schemas, naming, types
raw_silo_a_program_a2  ← INT booleans, UPPERCASE status values
raw_silo_a_program_a3  ← ISO string timestamps
raw_silo_B_program_b   ← Varying formats
... 4 more standalone silos
```

### Staging Layer (Normalized)
```
stg_silo_a_program_a1  → Mapped columns, UTC timestamps, lowercase values
stg_silo_a_program_a2  → Boolean conversion, status mapping
... all schemas unified
```

### Mart Layer (Unified)
```
fct_unified_support_tickets  ← 7,000 rows, 12 columns
                                ✓ Single source of truth
                                ✓ All lowercase
                                ✓ All UTC
                                ✓ Canonical status values
```

### Metrics Layer (Pre-computed)
```
metrics_sla_resolution           → Brand-level SLA compliance
metrics_volume_distribution      → Ticket counts by status/issue
metrics_quality_escalation       → Escalation & compensation rates
metrics_trends                   → Daily volume trends
```

---

## 📊 Key Tables

### fct_unified_support_tickets
Main fact table (7,000 rows):
- `brand`, `ticket_id` (composite PK)
- `received_date`, `resolution_date` (UTC)
- `ticket_status`, `primary_issue`, `root_cause_label`
- `resolution_label`, `financial_compensation`
- `escalated_to_management`, `resolved_within_sla`
- `customer_id`

### metrics_sla_resolution
Brand-level SLA metrics:
```
Brand    | Total | Compliant | Missed | Compliance %
---------|-------|-----------|--------|---------------
BrandA2  | 1000  | 529       | 471    | 52.9%
BrandA1  | 1000  | 516       | 484    | 51.6%
...
```

### metrics_volume_distribution
Ticket volume by status & issue:
```
Brand  | Status | Count | % of Brand
-------|--------|-------|----------
BrandA1| open   | 223   | 22.3%
BrandA1| closed | 246   | 24.6%
...
```

### metrics_quality_escalation
Escalation & compensation by brand:
```
Brand  | Escalation % | Total $ | Avg $ | Comp Rate %
-------|--------------|---------|-------|-------------
BrandA1| 50.2%        | 254,240 | 254.2 | 29.2%
...
```

### metrics_trends
Daily ticket trends:
```
Date       | Tickets | SLA Compliant | Compliance % | Brands
-----------|---------|---------------|--------------|--------
2024-12-31 | 18      | 9             | 50%          | 5
...
```

---

## 🛠 Key Transformations

### Schema Mapping
```sql
-- Raw: ticket_number, date_received, ticket_state, cust_id
-- Staging: ticket_id, received_date, ticket_status, customer_id
SELECT
    ticket_number as ticket_id,
    date_received as received_date,
    ticket_state as ticket_status,
    cust_id as customer_id
FROM raw_silo_a_program_a1
```

### Status Value Mapping
```sql
-- Raw: IN_PROGRESS, in_progress, ACTIVE, wip, hold
-- Canonical: in_progress, open, closed, pending
LEFT JOIN status_mapping ON lower(raw_status) = source_status
SELECT coalesce(sm.canonical_status, lower(raw_status)) as ticket_status
```

### Timezone Conversion
```sql
-- All timestamps converted to UTC in staging layer
strftime(received_date, '%Y-%m-%d %H:%M:%S') as received_date
```

### Type Normalization
```sql
-- A2 has: is_escalated::boolean (from INT 1/0)
is_escalated::boolean as escalated_to_management
```

---

## 💬 MCP Server Tools

### sla_compliance_overview
Get SLA metrics for brands
```
Tool: sla_compliance_overview(brand="BrandA1")
Returns: SLA compliance % and counts
```

### ticket_volume_by_status
Get volume distribution
```
Tool: ticket_volume_by_status(brand="BrandB")
Returns: Counts by status (open, closed, etc.)
```

### escalation_and_compensation
Get escalation & financial metrics
```
Tool: escalation_and_compensation()
Returns: Escalation % and compensation amounts by brand
```

### resolution_patterns
Analyze issue → resolution mappings
```
Tool: resolution_patterns(issue_type="login_issue")
Returns: Top resolution patterns with stats
```

### sla_missed_tickets
Find specific SLA-missed tickets
```
Tool: sla_missed_tickets(brand="BrandC", limit=20)
Returns: List of specific failing tickets
```

---

## 📈 Business Insights Enabled

### Before Consolidation ❌
- "What's our SLA compliance?" → Ask 7 different teams
- "Which brand is underperforming?" → Not comparable
- "Where should we focus improvement?" → No data

### After Consolidation ✅
- **SLA Rankings**: BrandA2 (52.9%) > BrandA1 (51.6%) > BrandB (45.2%)
- **Improvement Opportunities**: BrandB is 7.7 points behind leader
- **Issue Patterns**: billing_problem + login_issue = 50% of escalations
- **Financial Exposure**: $254K total compensation issued

---

## 🔍 Example Queries

### Q: "Which brand has the worst SLA?"
```bash
Claude: sla_compliance_overview()
Answer: BrandB at 45.2% (7.7 points below BrandA2)
```

### Q: "Show me BrandB's SLA-missed tickets"
```bash
Claude: sla_missed_tickets(brand="BrandB", limit=20)
Answer: 20 tickets with details on issue type, resolution attempts
```

### Q: "What drives escalations?"
```bash
Claude: resolution_patterns()
Answer: Top patterns show 50%+ escalation rates on:
        - feature_request → refund_issued (53%)
        - login_issue → refund_issued (54%)
```

### Q: "Compare all brands' escalation rates"
```bash
Claude: escalation_and_compensation()
Answer: Table showing BrandA1 highest (50.2%), BrandB lowest (45.1%)
```

---

## ⚡ Performance

All metrics queries return sub-500ms:
- SLA compliance: ~50ms
- Volume breakdown: ~50ms
- Escalation metrics: ~75ms
- SLA-missed tickets (limit 20): ~100ms
- Resolution patterns (top 15): ~150ms

Pre-computed metrics ensure Claude Desktop gets instant responses.

---

## 🔧 Extending the Project

### Add New Metric
1. Create SQL model in `models/metrics/`
2. Run `dbt run --profiles-dir . --select metrics_*`
3. Add tool to `mcp_server.py`
4. Restart server

### Add New Analysis Query
```bash
# Create in analysis/ folder
echo "SELECT ... FROM main_mart.fct_unified_support_tickets" > analysis/custom.sql

# View results
dbt compile --profiles-dir .
```

### Set Up Scheduled Updates
```bash
# Daily refresh via cron
0 2 * * * cd /path/to/project && dbt run --profiles-dir .
```

---

## 📚 Documentation

- **README.md** — Full project documentation
- **QUICKSTART.md** — Setup instructions (5 min to running)
- **MCP_SETUP.md** — Claude Desktop integration guide
- **METRICS_AND_MCP_INTEGRATION.md** — Deep dive on metrics architecture
- **LINKEDIN_POST.md** — Share your work!

---

## 🎯 Key Stats

- **7** support programs consolidated
- **7,000** synthetic tickets generated
- **12** columns in unified schema
- **4** pre-calculated metrics tables
- **5** MCP tools for querying
- **0** data quality issues (null values, case inconsistencies)
- **<500ms** latency for any metric query

---

## 💡 Why This Matters

You've built:
1. ✅ **Data Integration** — Consolidated 7 messy sources
2. ✅ **AI-Ready Data** — Natural language queryable
3. ✅ **Self-Service Analytics** — Non-technical teams can explore
4. ✅ **Scalable Architecture** — Easy to add more programs/metrics
5. ✅ **Auditable Pipeline** — All transformations are version-controlled SQL

This demonstrates exactly what hiring managers look for:
- Deep understanding of data problems & business impact
- Technical execution (ETL, dbt, SQL)
- Systems thinking (data architecture)
- AI/ML readiness

---

## 🚀 Next Steps

1. Push to GitHub: `theotherbrandonsoto/unified-support-tickets`
2. Add to LinkedIn: Post from LINKEDIN_POST.md
3. Connect to Claude Desktop and start exploring
4. Consider: Looker dashboard, scheduled dbt runs, incremental loading

---

**Questions?** See the full documentation files or explore the code!
