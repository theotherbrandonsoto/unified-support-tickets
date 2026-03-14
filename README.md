# Unified Support Tickets: Data Consolidation & AI-Readiness

> **Demonstrating how to consolidate siloed support ticket data into a unified, self-service, AI-ready dataset**

## The Problem

Seven independent support ticket programs operated across multiple silos, each with their own systems, data structures, and metrics:

- **Silo A:** 3 bundled support programs (A1, A2, A3) with shared infrastructure but different schemas
- **Silos B, C, D, E:** 4 completely standalone programs with no coordination

### The Business Impact of Siloing

❌ **No business-wide visibility** — Support metrics existed separately for each program, not holistically  
❌ **No cross-brand comparison** — Couldn't analyze ticket patterns, volumes, or resolution times across brands  
❌ **Dependency on multiple teams** — The support team had to ask 7 different people for data  
❌ **No self-service access** — Support ops couldn't analyze the data themselves  
❌ **Not AI-ready** — The fragmented data couldn't feed into AI/ML workflows or plain-English query systems

---

## The Consolidation Challenge

Each of the 7 programs had different approaches to the same problems:

### 1. **Schema Heterogeneity** — Different Column Names, Different Types
| Program | Ticket ID | Received Date | Status Field | Customer ID |
|---------|-----------|---------------|--------------|-------------|
| A1 | `ticket_number` | `date_received` | `ticket_state` | `cust_id` |
| A2 | `request_id` | `created_at` | `status` | `user_id` |
| A3 | `support_ticket_id` | `ticket_received_timestamp` (ISO string) | `ticket_status_current` | `customer_identifier` |
| B-E | `ticket_id` | `received_date_utc` | `status` | `customer_id` |

### 2. **Semantic Heterogeneity** — Same Meaning, Different Values
```
Program A1:  open, closed, in_progress, pending
Program A2:  OPEN, CLOSED, IN_PROGRESS, WAITING
Program A3:  open, closed, wip, hold
Programs B-E: NEW, ACTIVE, RESOLVED, PENDING_REVIEW

↓ Consolidated to:
open, closed, in_progress, pending (all lowercase)
```

### 3. **Timezone Complexity** — Global Business Needs UTC
Each program tracked support tickets in different timezone formats. To calculate accurate SLAs and time-to-resolution metrics globally, all timestamps had to be converted to UTC in the staging layer.

### 4. **Type Inconsistencies** — Booleans as Different Types
- Program A1: `True/False` (native booleans)
- Program A2: `1/0` (integers)
- Programs A3, B-E: Native booleans

---

## The Solution: SQL + dbt + DuckDB

This project demonstrates a scalable pattern for consolidating messy, siloed data:

```
RAW LAYER (7 source tables)
        ↓
STAGING LAYER (7 normalized models)
  - Field mapping
  - Timezone conversion to UTC
  - Status value mapping via lookup table
  - Type normalization
  - Lowercase enforcement
        ↓
MART LAYER (1 unified fact table)
  - Union of all 7 staged sources
  - Single source of truth
  - AI-ready schema
        ↓
ANALYSIS (Business Insights)
  - Cross-brand comparisons
  - Company-wide SLA metrics
  - Self-service queries
```

---

## Project Structure

```
unified-support-tickets/
├── models/
│   ├── raw/                          # Raw source definitions
│   ├── staging/
│   │   ├── stg_silo_a_program_a1.sql
│   │   ├── stg_silo_a_program_a2.sql
│   │   ├── stg_silo_a_program_a3.sql
│   │   ├── stg_silo_b_program_b.sql
│   │   ├── stg_silo_c_program_c.sql
│   │   ├── stg_silo_d_program_d.sql
│   │   └── stg_silo_e_program_e.sql
│   ├── mart/
│   │   └── fct_unified_support_tickets.sql  # Final unified table
│   └── sources.yml                  # Source definitions
├── seeds/
│   └── status_mapping.csv           # Lookup table for status normalization
├── analysis/
│   ├── 01_cross_brand_ticket_volume.sql
│   ├── 02_sla_compliance_by_brand.sql
│   └── 03_resolution_patterns.sql
├── generate_raw_data.py             # Creates synthetic raw data
├── dbt_project.yml
├── profiles.yml
└── README.md
```

---

## Unified Schema

The final `fct_unified_support_tickets` table has this canonical schema:

| Column | Type | Description |
|--------|------|-------------|
| `brand` | string | Which of the 7 support programs |
| `ticket_id` | string | Unique identifier per ticket |
| `received_date` | timestamp | When ticket arrived (UTC) |
| `resolution_date` | timestamp | When ticket was closed (UTC) |
| `ticket_status` | string | Current state (open, closed, in_progress, pending) |
| `primary_issue` | string | Category of the issue |
| `root_cause_label` | string | Why it happened |
| `resolution_label` | string | How it was resolved |
| `financial_compensation` | float | Dollar amount issued |
| `escalated_to_management` | boolean | Escalated? |
| `resolved_within_sla` | boolean | Met SLA? |
| `customer_id` | string | Links to customer |

**Key guarantees:**
- ✅ All timestamps in UTC
- ✅ All string values lowercase
- ✅ All status values canonical (open, closed, in_progress, pending)
- ✅ No null values in critical fields
- ✅ 7,000 tickets (1,000 per program)

---

## Key Transformations

### Staging Models Handle:

1. **Field Mapping** — Normalize column names to canonical schema
2. **Type Conversion** — Cast int booleans to native booleans
3. **Timezone Conversion** — All dates normalized to UTC
4. **ISO String Parsing** — Handle timestamp strings (e.g., `2024-05-01T15:30:00`)
5. **Status Mapping** — Lookup table joins to canonicalize status values
6. **Lowercase Enforcement** — All text fields converted to lowercase

Example from `stg_silo_a_program_a2.sql`:
```sql
-- Convert int booleans (1/0) to proper booleans
is_escalated::boolean as escalated_to_management,

-- Lookup table join for status normalization
coalesce(sm.canonical_status, lower(wtc.ticket_status_raw)) as ticket_status,

-- Lowercase all text fields
lower(wtc.primary_issue) as primary_issue,
```

---

## Running the Project

### Prerequisites
```bash
pip install dbt-duckdb dbt-core duckdb pandas numpy
```

### Generate Raw Data
```bash
python generate_raw_data.py
```
Creates 7,000 synthetic support tickets (~1,000 per program) with intentionally messy data.

### Load Seeds & Execute Models
```bash
dbt seed --profiles-dir .
dbt run --profiles-dir .
```

This will:
1. Load the `status_mapping` lookup table
2. Execute all 7 staging models (raw → normalized)
3. Execute the mart model (union of all 7 stages)
4. Create the unified `fct_unified_support_tickets` table

### Run Analysis Queries
```bash
dbt run-operation exec --args '{"query": "SELECT * FROM main_mart.fct_unified_support_tickets LIMIT 5"}'
```

Or run the included analysis queries:
```bash
analysis/01_cross_brand_ticket_volume.sql
analysis/02_sla_compliance_by_brand.sql
analysis/03_resolution_patterns.sql
```

---

## Results: Business Insights Now Possible

### Before Consolidation ❌
- "What's the SLA compliance rate across the company?" → Ask 7 different teams
- "Which brands have the most high-severity issues?" → Not comparable
- "What's our total financial compensation exposure?" → Can't aggregate

### After Consolidation ✅

**1. Cross-Brand Ticket Volume**
```
Brand       | Total | Open | In Progress | Pending | Closed
BrandA1     | 1000  | 223  | 258         | 273     | 246
BrandA2     | 1000  | 213  | 266         | 258     | 263
BrandB      | 1000  | 226  | 244         | 265     | 265
...
```

**2. SLA Compliance Rankings**
```
Brand    | Total | SLA Compliant | Compliance %
BrandA2  | 1000  | 529           | 52.9%
BrandA1  | 1000  | 516           | 51.6%
BrandC   | 1000  | 516           | 51.6%
BrandB   | 1000  | 452           | 45.2%  ← Opportunity!
```

**3. Resolution Patterns**
```
Primary Issue     | Resolution      | Frequency | Escalation Rate
feature_request   | refund_issued   | 134       | 53%
billing_problem   | password_reset  | 127       | 42.5%
login_issue       | refund_issued   | 126       | 54%
```

---

## Key Insights

### Data Quality Achieved:
- ✅ 7,000 tickets unified from 7 sources
- ✅ 7 distinct brands now comparable
- ✅ 4 canonical status values (no data quality issues)
- ✅ 0% null values in critical columns
- ✅ 100% lowercase + UTC-normalized
- ✅ Ready for AI/ML workflows

### Business Outcomes:
- **Support ops can now self-serve** — No more dependency on 7 different teams
- **Company-wide visibility** — See patterns across all brands
- **AI-ready data** — Unified table can feed plain-English AI queries
- **SLA accountability** — Compare brands and identify improvement opportunities
- **Compensation analysis** — Aggregate financial exposure across all programs

---

## Technical Highlights

### Why This Approach?

1. **SQL + dbt is the right tool** — Designed exactly for this ETL work
2. **Staging layer isolation** — Each raw source has its own normalized stage
3. **Seed-based mapping** — Status values live in a reusable lookup table
4. **Idempotent & reproducible** — Run it 100 times, same results
5. **DuckDB for local development** — No external dependencies, everything runs locally

### What Makes This Production-Ready?

- ✅ Clear separation of concerns (raw → staging → mart)
- ✅ Reusable lookup tables (status_mapping)
- ✅ Type safety (explicit casting, null checks)
- ✅ Data quality checks (no uppercase values, no nulls in critical fields)
- ✅ Documented transformations (each staging model has clear comments)
- ✅ Scalable pattern (easy to add 8th program)

---

## How This Demonstrates Your Skills

This project shows:

**Data Integration & Consolidation:**
- Handled 7 different source schemas
- Mapped semantic differences (different status values)
- Unified disparate data into one canonical table

**Data Quality & Transformation:**
- Timezone handling (UTC conversion for global business)
- Type normalization (int to boolean)
- Semantic mapping (lookup tables)
- Lowercase enforcement & null checks

**Analytics Engineering:**
- Proper dbt structure (raw → staging → mart layers)
- Seed-based reference data
- Reusable, modular SQL
- Clear, documented transformations

**Business Acumen:**
- Identified the real problem (no cross-brand visibility)
- Understood the impact (compliance team couldn't self-serve)
- Designed a solution that enabled AI-ready, self-service analytics

---

## Extensions & Future Work

To make this even more production-grade:
- Add dbt tests (uniqueness, not-null, referential integrity)
- Add a fact table for time-to-resolution metrics
- Build a Looker dashboard on top of the unified table
- Add incremental loading for new tickets
- Set up automated dbt runs via Goose Desktop recipes

---

## License

This is a portfolio project demonstrating data consolidation patterns. Use freely for learning and adaptation.

---

**Built with:** dbt, DuckDB, SQL, Python  
**Skills demonstrated:** Data integration, ETL/transformation, analytics engineering, SQL, dbt
