# Metrics Store — Complete Querying Guide

## 📊 Available Metrics

Your metrics store has **8 major queryable metrics** derived from the unified fact table (`fct_unified_support_tickets`):

### 1. **SLA Compliance by Brand**
Shows which brands are meeting SLA targets
- `brand` — Brand name (BrandA1, BrandA2, etc.)
- `total_tickets` — Total tickets for that brand
- `sla_compliant` — Tickets that met SLA
- `sla_compliance_pct` — Percentage meeting SLA

**Current Status:**
```
BrandA2: 52.9% ✅ (Best)
BrandA1: 51.6% ✅
BrandC:  51.6% ✅
BrandA3: 50.7% ✅
BrandD:  49.3% ⚠️
BrandE:  49.1% ⚠️
BrandB:  45.2% ⚠️ (Worst - 7.7 point gap)
```

### 2. **Ticket Volume by Status**
Shows ticket distribution across statuses
- `brand` — Brand name
- `ticket_status` — Status (open, closed, in_progress, pending)
- `ticket_count` — Number of tickets
- `pct_of_brand` — Percentage of that brand's tickets

**Distribution:**
```
Each brand has ~250-270 tickets in each status
Evenly distributed across 4 statuses
```

### 3. **Escalation Rate by Brand**
Shows which brands escalate tickets most
- `brand` — Brand name
- `total_tickets` — Total tickets
- `escalated_count` — Tickets escalated to management
- `escalation_rate_pct` — Escalation percentage

**Current Status:**
```
BrandE:  52.5% (Highest escalation)
BrandA2: 51.8%
BrandD:  50.9%
BrandA1: 50.4%
BrandA3: 49.3%
BrandC:  49.3%
BrandB:  49.0% (Lowest escalation)
```

### 4. **Financial Compensation by Brand**
Shows how much compensation is being issued
- `brand` — Brand name
- `total_compensation` — Total $ issued
- `avg_per_ticket` — Average $ per ticket
- `tickets_with_compensation` — Count of tickets with $
- `compensation_rate_pct` — % of tickets receiving compensation

**Example:**
```
BrandA1: $254,240 total, $254.24 avg, 29.2% of tickets
```

### 5. **Top Issue Types**
Shows most common ticket issues
- `primary_issue` — Issue type
- `frequency` — How many tickets
- `pct_of_total` — % of all tickets

**Current Top 5:**
```
performance_issue:  931 tickets (13.3%)
data_access:        886 tickets (12.7%)
billing_problem:    883 tickets (12.6%)
login_issue:        879 tickets (12.6%)
data_export:        865 tickets (12.4%)
```

### 6. **Resolution Patterns**
Shows how different issues are typically resolved
- `primary_issue` — Issue type
- `resolution_label` — How it was resolved
- `frequency` — How many times this combo occurred
- `escalation_rate_pct` — Escalation % for this pattern
- `avg_compensation` — Average $ for this pattern

**Example:**
```
feature_request → refund_issued: 134 tickets, 53% escalation
login_issue → refund_issued: 126 tickets, 54% escalation
billing_problem → password_reset: 127 tickets, 42.5% escalation
```

### 7. **Root Cause Analysis**
Shows why tickets are happening
- `root_cause_label` — Why (user_error, system_bug, etc.)
- `frequency` — How many tickets
- `sla_compliance_pct` — SLA rate for this cause
- `escalation_rate_pct` — Escalation rate
- `avg_compensation` — Average compensation issued

### 8. **SLA-Missed Tickets**
Specific tickets that failed to meet SLA
- `brand` — Which brand
- `ticket_id` — Specific ticket ID
- `received_date` — When it came in
- `resolution_date` — When it was resolved
- `primary_issue` — What the issue was
- `root_cause_label` — Why it happened
- `escalated_to_management` — Was it escalated?

---

## 🚀 How to Query These Metrics

### **Option 1: Direct SQL (Python)**

```python
import duckdb

conn = duckdb.connect('unified_support_tickets.duckdb', read_only=True)

# Example: Get SLA compliance by brand
result = conn.execute("""
    SELECT
        brand,
        COUNT(*) as total_tickets,
        SUM(CASE WHEN resolved_within_sla THEN 1 ELSE 0 END) as sla_compliant,
        ROUND(SUM(CASE WHEN resolved_within_sla THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as sla_compliance_pct
    FROM main_mart.fct_unified_support_tickets
    GROUP BY brand
    ORDER BY sla_compliance_pct DESC
""").df()

print(result)
```

### **Option 2: Using Claude (via MCP Server)**

```bash
# Start the MCP server
python mcp_server.py

# Then in Claude Desktop, ask questions like:
# "What's our SLA compliance by brand?"
# "Show me BrandB tickets that missed SLA"
# "What are the escalation rates?"
# "Which issues have the worst SLA compliance?"
```

### **Option 3: SQL Files (in analysis/ folder)**

```bash
# Run the included analysis queries
dbt run-operation execute --args '{"sql": "SELECT * FROM main_mart.fct_unified_support_tickets LIMIT 10"}'
```

---

## 📝 Common Query Examples

### **Query 1: Compare SLA Compliance Across Brands**

```sql
SELECT
    brand,
    COUNT(*) as total_tickets,
    ROUND(SUM(CASE WHEN resolved_within_sla THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as sla_compliance_pct,
    ROUND(SUM(CASE WHEN escalated_to_management THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as escalation_pct
FROM main_mart.fct_unified_support_tickets
GROUP BY brand
ORDER BY sla_compliance_pct DESC
```

**Result:**
```
BrandA2: 52.9% SLA, 51.8% escalation
BrandA1: 51.6% SLA, 50.4% escalation
...
BrandB:  45.2% SLA, 49.0% escalation (gap: 7.7 points)
```

### **Query 2: Find SLA-Missed Tickets from Underperforming Brand**

```sql
SELECT
    ticket_id,
    received_date,
    resolution_date,
    primary_issue,
    root_cause_label,
    escalated_to_management
FROM main_mart.fct_unified_support_tickets
WHERE brand = 'BrandB'
  AND NOT resolved_within_sla
ORDER BY received_date DESC
LIMIT 20
```

**Use Case:** Root cause analysis for why BrandB is falling behind

### **Query 3: Identify High-Escalation Issues**

```sql
SELECT
    primary_issue,
    resolution_label,
    COUNT(*) as frequency,
    ROUND(SUM(CASE WHEN escalated_to_management THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as escalation_rate_pct,
    ROUND(AVG(financial_compensation), 2) as avg_compensation
FROM main_mart.fct_unified_support_tickets
GROUP BY primary_issue, resolution_label
HAVING COUNT(*) > 20
ORDER BY escalation_rate_pct DESC
LIMIT 10
```

**Use Case:** Find patterns of expensive/complex issues

### **Query 4: Financial Exposure by Issue Type**

```sql
SELECT
    primary_issue,
    COUNT(*) as ticket_count,
    SUM(financial_compensation) as total_compensation,
    ROUND(AVG(financial_compensation), 2) as avg_per_ticket,
    ROUND(SUM(financial_compensation) * 100.0 / (SELECT SUM(financial_compensation) FROM main_mart.fct_unified_support_tickets), 2) as pct_of_total_compensation
FROM main_mart.fct_unified_support_tickets
WHERE financial_compensation > 0
GROUP BY primary_issue
ORDER BY total_compensation DESC
```

**Use Case:** Where is compensation money going?

### **Query 5: Root Cause Impact Analysis**

```sql
SELECT
    root_cause_label,
    COUNT(*) as frequency,
    ROUND(SUM(CASE WHEN resolved_within_sla THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as sla_compliance_pct,
    ROUND(SUM(CASE WHEN escalated_to_management THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as escalation_rate_pct,
    ROUND(SUM(financial_compensation), 2) as total_compensation
FROM main_mart.fct_unified_support_tickets
GROUP BY root_cause_label
ORDER BY frequency DESC
```

**Use Case:** Which root causes have the biggest business impact?

---

## 🎯 Sample Outputs

### SLA Compliance Rankings
```
┌──────────┬────────────────┬──────────────────┐
│ brand    │ total_tickets  │ sla_compliance % │
├──────────┼────────────────┼──────────────────┤
│ BrandA2  │ 1000           │ 52.9%           │
│ BrandA1  │ 1000           │ 51.6%           │
│ BrandC   │ 1000           │ 51.6%           │
│ BrandA3  │ 1000           │ 50.7%           │
│ BrandD   │ 1000           │ 49.3%           │
│ BrandE   │ 1000           │ 49.1%           │
│ BrandB   │ 1000           │ 45.2% ⚠️         │
└──────────┴────────────────┴──────────────────┘
```

### Top Resolution Patterns
```
┌──────────────────┬─────────────────────────┬───────────┬──────────────┐
│ primary_issue    │ resolution_label        │ frequency │ escalation % │
├──────────────────┼─────────────────────────┼───────────┼──────────────┤
│ feature_request  │ refund_issued           │ 134       │ 53%         │
│ login_issue      │ refund_issued           │ 126       │ 54%         │
│ billing_problem  │ password_reset          │ 127       │ 42.5%       │
│ performance_issue│ data_correction         │ 126       │ 54%         │
│ account_locked   │ data_correction         │ 125       │ 46.4%       │
└──────────────────┴─────────────────────────┴───────────┴──────────────┘
```

---

## 🔗 Setting Up to Query with Me (Claude)

### **Step 1: Download Your Project**

```bash
# Extract the zip/tar.gz file you downloaded
unzip unified-support-tickets.zip
cd unified-support-tickets
```

### **Step 2: Generate Data (if needed)**

```bash
python generate_raw_data.py
dbt seed --profiles-dir .
dbt run --profiles-dir .
```

### **Step 3: Query with Me**

You can ask me questions like:

**Example:**
```
"Using the support tickets metrics, what's our SLA compliance by brand?"
→ I can write the SQL, execute it, and show you results

"Which issues have the highest escalation rates?"
→ I query the metrics and analyze

"Show me the top 10 SLA-missed tickets from BrandB"
→ I write the query and explain the patterns
```

### **Step 4: Set Up MCP Server (Optional - for Claude Desktop)**

```bash
# Start the server
python mcp_server.py

# Then in Claude Desktop, connect to localhost:3000
# See MCP_SETUP.md for detailed instructions
```

---

## 📊 Available Metrics Summary Table

| Metric | Data Source | Update Frequency | Use Case |
|--------|-------------|------------------|----------|
| SLA Compliance | fact table aggregation | Real-time | Monitor brand performance |
| Volume by Status | fact table grouping | Real-time | Track ticket flow |
| Escalation Rate | fact table analysis | Real-time | Identify complex issues |
| Compensation $ | fact table sum | Real-time | Financial exposure |
| Issue Types | fact table distinct | Real-time | Prioritize improvements |
| Resolution Patterns | fact table correlation | Real-time | Optimize workflows |
| Root Causes | fact table analysis | Real-time | Process improvement |
| SLA-Missed Tickets | fact table filtering | Real-time | Incident analysis |

---

## ✅ Quick Start

**Right now, you can:**

1. **Ask me to query any metric** — I'll write SQL and show results
2. **Download the project** and run queries locally
3. **Use the MCP server** to query via Claude Desktop in plain English
4. **Analyze patterns** — I can help interpret results and suggest actions

**Example Request:**
```
"What are the top 3 improvement opportunities in our support metrics?"

I would:
1. Query SLA compliance (find BrandB is 7.7 points behind)
2. Query BrandB's SLA-missed tickets (find issue types)
3. Query resolution patterns (find what works vs doesn't)
4. Recommend: "Focus on billing_problem + login_issue resolution speed"
```

---

**Ready to explore your metrics? Ask me any question!** 📊

