# Metrics Store & MCP Integration Guide

## Overview

Your unified support tickets project now has two additional components:

1. **Metrics Store** — dbt models that pre-calculate common support metrics
2. **MCP Server** — Allows Claude Desktop to query metrics in plain English

This enables a complete AI-ready analytics workflow.

---

## Part 1: Metrics Store

### What It Is

The metrics store consists of 4 dbt models that pre-calculate common support metrics:

```
metrics_sla_resolution      → SLA compliance by brand
metrics_volume_distribution → Ticket counts by status and issue
metrics_quality_escalation  → Escalation and compensation metrics
metrics_trends              → Daily ticket volume trends
```

### How It Works

Instead of running complex queries every time, these metrics are pre-computed in the mart layer:

```
Unified Fact Table (fct_unified_support_tickets)
            ↓
      Pre-calculated Metrics
            ↓
   MCP Server (Query Interface)
            ↓
    Claude Desktop (Natural Language)
```

### Available Metrics

#### 1. SLA & Resolution
```sql
SELECT * FROM main.metrics_sla_resolution
```

Returns:
- Brand name
- Total tickets
- SLA compliant tickets
- SLA missed tickets
- SLA compliance percentage

#### 2. Volume & Distribution
```sql
SELECT * FROM main.metrics_volume_distribution
WHERE metric_type = 'by_brand_status'
```

Returns:
- Brand, ticket status, count, percentage of brand
- Segments by both status and issue type

#### 3. Quality & Escalation
```sql
SELECT * FROM main.metrics_quality_escalation
WHERE brand IS NOT NULL
```

Returns:
- Escalation rate percentage
- Total compensation issued
- Average compensation per ticket
- Compensation rate percentage

#### 4. Trends
```sql
SELECT * FROM main.metrics_trends
```

Returns:
- Daily ticket volumes
- SLA compliance percentage by day
- Number of brands represented
- Average compensation

---

## Part 2: MCP Server

### What It Is

An MCP (Model Context Protocol) server that translates Claude's natural language queries into database calls.

### How It Works

1. **You ask Claude:** "What's our SLA compliance by brand?"
2. **Claude calls the MCP server** with the `sla_compliance_overview` tool
3. **MCP server queries the database** and formats results
4. **Claude shows you the answer** in a nice table

### Running the Server

```bash
python mcp_server.py
```

Should output:
```
INFO:     Uvicorn running on http://localhost:3000
```

The server stays running and listens for queries from Claude Desktop.

### Available Tools

#### `sla_compliance_overview`
Get SLA metrics for all brands or filter by brand.

```
Claude: "What's SLA compliance for BrandA1?"
↓
Tool call: sla_compliance_overview(brand="BrandA1")
↓
Result: SLA table for that brand
```

#### `ticket_volume_by_status`
Get ticket counts by status (open, closed, in_progress, pending).

```
Claude: "How many open tickets does each brand have?"
↓
Tool call: ticket_volume_by_status()
↓
Result: Volume table grouped by brand and status
```

#### `escalation_and_compensation`
Get escalation rates and compensation metrics.

```
Claude: "Show me escalation rates and total compensation by brand"
↓
Tool call: escalation_and_compensation()
↓
Result: Metrics table with escalation % and $ amounts
```

#### `resolution_patterns`
Analyze how issues are resolved.

```
Claude: "What are the most common resolution patterns?"
↓
Tool call: resolution_patterns()
↓
Result: Table of issue type → resolution method with stats
```

#### `sla_missed_tickets`
Find specific tickets that missed SLA.

```
Claude: "Show me the last 10 BrandC tickets that missed SLA"
↓
Tool call: sla_missed_tickets(brand="BrandC", limit=10)
↓
Result: List of specific ticket IDs and details
```

---

## Part 3: Claude Desktop Integration

### Setup

1. **Keep MCP server running:**
   ```bash
   python mcp_server.py
   ```

2. **Configure Claude Desktop** (see MCP_SETUP.md for detailed steps)

3. **Start asking questions**

### Example Workflow

```
You: "What's our business health across all brands?"

Claude calls: sla_compliance_overview(), escalation_and_compensation()

Claude returns: Analysis showing BrandA2 is best performer (52.9% SLA),
               BrandB needs improvement (45.2% SLA), escalation rates 
               highest in BrandA1 (53%)

You: "Deep dive into why BrandB is underperforming"

Claude calls: sla_missed_tickets(brand="BrandB", limit=20), 
             resolution_patterns()

Claude returns: 20 recent SLA-missed tickets from BrandB with patterns,
               shows most common issues are billing_problem and login_issue

You: "What if we could prevent 10% of BrandB's SLA misses?"

Claude: "That would improve BrandB's SLA compliance from 45.2% to ~49.7%, 
         closing the gap with other brands. Recommend focusing on 
         billing_problem and login_issue resolution speed."
```

---

## Part 4: Architecture Summary

### Full Data Flow

```
Raw Support Ticket Systems (7 programs, messy data)
                ↓
        Raw Layer (DuckDB tables)
        - Different schemas
        - Inconsistent naming
        - Mixed timezones
                ↓
        Staging Layer (dbt models)
        - Schema normalization
        - Timezone conversion to UTC
        - Status value mapping
        - Type conversion
                ↓
        Mart Layer (fct_unified_support_tickets)
        - 7,000 tickets unified
        - Single source of truth
        - AI-ready schema
                ↓
        Metrics Store (dbt models)
        - Pre-calculated SLA metrics
        - Volume distributions
        - Escalation & compensation
        - Daily trends
                ↓
        MCP Server (Python/DuckDB)
        - Natural language interface
        - Tool definitions for Claude
        - Query translation & formatting
                ↓
        Claude Desktop
        - Plain English questions
        - Instant metric insights
        - Drill-down capabilities
```

### Why This Architecture?

- **Scalability:** Metrics are pre-computed, not calculated per query
- **Performance:** Claude gets instant results
- **Flexibility:** Add new metrics by creating new dbt models
- **Auditability:** All transformations are version-controlled SQL
- **Maintainability:** Clear separation of concerns

---

## Part 5: Extending the Metrics Store

### Adding a New Metric

Let's say you want to add "average resolution time by issue type":

1. **Create a dbt model** (`models/metrics/metrics_resolution_speed.sql`):
   ```sql
   SELECT
       primary_issue,
       COUNT(*) as total_tickets,
       ROUND(AVG(EXTRACT(EPOCH FROM (resolution_date - received_date)) / 3600.0), 2) as avg_hours,
       ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (resolution_date - received_date)) / 3600.0), 2) as median_hours
   FROM {{ ref('fct_unified_support_tickets') }}
   GROUP BY primary_issue
   ORDER BY avg_hours
   ```

2. **Run dbt:**
   ```bash
   dbt run --profiles-dir . --select metrics_resolution_speed
   ```

3. **Add a tool to MCP server** (in `mcp_server.py`):
   ```python
   {
       "name": "resolution_speed_by_issue",
       "description": "Get average resolution time by issue type",
       "input_schema": {...}
   }
   ```

4. **Add the tool handler**:
   ```python
   elif name == "resolution_speed_by_issue":
       query = "SELECT * FROM main.metrics_resolution_speed"
       # ...format and return results
   ```

5. **Restart MCP server** and Claude can immediately query it

---

## Part 6: Querying Directly

If you want to bypass the MCP server and query metrics directly:

```python
import duckdb

conn = duckdb.connect('unified_support_tickets.duckdb', read_only=True)

# Get SLA metrics
result = conn.execute("""
    SELECT brand, sla_compliance_pct 
    FROM main.metrics_sla_resolution 
    ORDER BY sla_compliance_pct DESC
""").df()

print(result)
```

Or use dbt directly:

```bash
dbt run-operation execute --args '{"sql": "SELECT * FROM main.metrics_sla_resolution"}'
```

---

## Performance Notes

### Metrics Caching

Since metrics are pre-computed views, they're always fresh but only recalculated when:
- New tickets are added to the fact table
- You explicitly run `dbt run`

### Query Speed

- **SLA compliance:** Instant (~50ms)
- **Volume breakdown:** Instant (~50ms)
- **SLA-missed tickets with limit 20:** ~100ms
- **Resolution patterns top 15:** ~150ms

All metrics are sub-500ms even for the largest queries.

---

## Troubleshooting

### MCP Server Returns Empty Results

1. Check that dbt models were created:
   ```bash
   dbt run --profiles-dir .
   ```

2. Verify metrics table exists:
   ```bash
   python -c "import duckdb; conn = duckdb.connect('unified_support_tickets.duckdb'); print(conn.execute('SELECT COUNT(*) FROM main.metrics_sla_resolution').df())"
   ```

3. Check database path in `mcp_server.py`:
   ```python
   DB_PATH = os.path.join(os.path.dirname(__file__), "unified_support_tickets.duckdb")
   ```

### Claude Desktop Can't Find MCP Server

1. Make sure server is running: `python mcp_server.py`
2. Check configuration in Claude Desktop settings
3. Verify localhost:3000 is accessible

### Metrics Show Unexpected Values

Run data quality checks on the fact table:

```bash
python -c "
import duckdb
conn = duckdb.connect('unified_support_tickets.duckdb')
# Check for nulls
print('Null values:', conn.execute('SELECT SUM(CASE WHEN brand IS NULL THEN 1 ELSE 0 END) FROM main_mart.fct_unified_support_tickets').fetchall())
# Check row count
print('Total rows:', conn.execute('SELECT COUNT(*) FROM main_mart.fct_unified_support_tickets').fetchall())
"
```

---

## Next Steps

1. ✅ **Setup complete** — You have raw data, staging, mart, metrics, and MCP
2. 📊 **Start querying** — Ask Claude Desktop questions about your support metrics
3. 📈 **Add more metrics** — Follow "Extending the Metrics Store" section
4. 🔄 **Setup automation** — Use Goose Desktop recipes to run `dbt run` on a schedule
5. 📋 **Create dashboards** — Feed metrics into Looker/Tableau for visualization

---

**Your data is now AI-ready and natural-language queryable!**
