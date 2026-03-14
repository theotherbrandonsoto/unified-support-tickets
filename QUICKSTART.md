## Quick Start Guide

### ⚡ **FASTEST WAY: One Command Setup** (Recommended)

**macOS/Linux:**
```bash
bash setup.sh
```

**Windows:**
```bash
setup.bat
```

This single command will:
- ✅ Create a virtual environment
- ✅ Install all dependencies from `requirements.txt`
- ✅ Generate 7,000 synthetic support tickets
- ✅ Run the complete dbt pipeline (raw → staging → mart)
- ✅ Verify the setup is working

**That's it!** Everything is ready to use.

---

### 📋 **Manual Setup** (if you prefer step-by-step)

#### 1. Clone & Setup
```bash
git clone https://github.com/theotherbrandonsoto/unified-support-tickets.git
cd unified-support-tickets
```

#### 2. Create Virtual Environment (Optional but Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- dbt-core & dbt-duckdb (analytics engineering)
- duckdb (database)
- pandas & numpy (data processing)
- mcp & uvicorn (Claude Desktop integration)

#### 4. Generate Synthetic Data
```bash
python generate_raw_data.py
```

Output:
```
✓ Created raw_silo_a_program_a1 with 1000 rows
✓ Created raw_silo_a_program_a2 with 1000 rows
✓ Created raw_silo_a_program_a3 with 1000 rows
✓ Created raw_silo_B_program_b with 1000 rows
✓ Created raw_silo_C_program_c with 1000 rows
✓ Created raw_silo_D_program_d with 1000 rows
✓ Created raw_silo_E_program_e with 1000 rows
✅ All raw data tables created successfully!
```

#### 5. Load Seeds & Execute dbt Models
```bash
dbt seed --profiles-dir .
dbt run --profiles-dir .
```

This will:
1. Load `status_mapping.csv` (lookup table for status normalization)
2. Execute 7 staging models (raw → normalized)
3. Execute 1 mart model (unified fact table)
4. Create `main_mart.fct_unified_support_tickets` with 7,000 rows

#### 6. Verify the Results
```bash
python3 -c "
import duckdb
conn = duckdb.connect('./unified_support_tickets.duckdb')
result = conn.execute('SELECT COUNT(*) as total_tickets, COUNT(DISTINCT brand) as brands FROM main_mart.fct_unified_support_tickets').df()
print(result)
"
```

Expected output:
```
   total_tickets  brands
            7000       7
```

### 6. Run Analysis Queries
```bash
dbt run-operation sql_execute --args '{"sql": "SELECT brand, COUNT(*) FROM main_mart.fct_unified_support_tickets GROUP BY brand ORDER BY COUNT(*) DESC"}'
```

Or query directly:
```bash
python -c "
import duckdb
conn = duckdb.connect('./unified_support_tickets.duckdb')
print(conn.execute('''
    SELECT
        brand,
        COUNT(*) as tickets,
        ROUND(SUM(CASE WHEN resolved_within_sla THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as sla_pct
    FROM main_mart.fct_unified_support_tickets
    GROUP BY brand
    ORDER BY sla_pct DESC
''').df())
"
```

---

## Project Files

- `generate_raw_data.py` — Creates 7 synthetic messy raw tables
- `models/staging/stg_*.sql` — 7 staging models (one per source)
- `models/mart/fct_unified_support_tickets.sql` — Final unified table
- `seeds/status_mapping.csv` — Lookup table for status normalization
- `analysis/*.sql` — Example analysis queries
- `dbt_project.yml` — dbt configuration
- `profiles.yml` — dbt DuckDB profile
- `README.md` — Full project documentation

---

## What Gets Created

### Raw Layer (Raw data as-is from sources)
- `raw_silo_a_program_a1` — Different column names, different types
- `raw_silo_a_program_a2` — Int booleans, UPPERCASE status values
- `raw_silo_a_program_a3` — ISO string timestamps
- `raw_silo_B_program_b` through `raw_silo_E_program_e` — Varying schemas

### Staging Layer (Normalized, cleaned)
- `stg_silo_a_program_a1` → `stg_silo_e_program_e` — All schemas unified
- Fields normalized
- Timezones converted to UTC
- Status values mapped to canonical form
- All lowercase + null-safe

### Mart Layer (Unified fact table)
- `fct_unified_support_tickets` — 7,000 rows, 12 columns
- Single source of truth
- AI-ready schema
- No data quality issues

---

## Troubleshooting

**Error: "Catalog 'main' does not exist"**
- Make sure you ran `python generate_raw_data.py` first to create the DuckDB database

**Error: "Model not found"**
- Check that `profiles-dir` is set to `.` (current directory)
- Run `dbt debug --profiles-dir .` to verify connection

**DuckDB file lock**
- Close any other connections to `unified_support_tickets.duckdb`
- Delete `unified_support_tickets.duckdb` and restart if needed

---

## Next Steps

1. **Explore the data:**
   ```sql
   SELECT * FROM main_mart.fct_unified_support_tickets LIMIT 10;
   ```

2. **Run the example analyses** in `analysis/` folder

3. **Add your own tests** using dbt:
   ```yaml
   models:
     - name: fct_unified_support_tickets
       columns:
         - name: brand
           tests:
             - not_null
             - unique_combination_of_columns:
                 combination_of_columns:
                   - brand
                   - ticket_id
   ```

4. **Build on top** — Create downstream models, dashboards, etc.

---

**Questions?** See the full README.md for detailed documentation.
