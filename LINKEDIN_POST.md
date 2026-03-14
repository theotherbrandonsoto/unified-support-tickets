📊 New portfolio project: Unified Support Tickets

I just shipped a data consolidation project that demonstrates how to take siloed, messy data and make it unified, queryable, and AI-ready.

**The Problem:**
Seven independent support ticket programs. Seven different data structures. Seven different teams you had to ask for answers.

No way to compare brands. No cross-program visibility. The support ops team couldn't analyze the data themselves.

**The Solution:**
🔧 Built a dbt + SQL pipeline that:
• Consolidated 7 disparate sources (7,000 tickets total)
• Normalized schemas across different column naming conventions
• Mapped status values (IN_PROGRESS → in_progress → normalized)
• Converted everything to UTC for accurate SLA calculations
• Enforced lowercase + null checks → production-ready data

**The Result:**
✅ 7,000 tickets unified into one canonical fact table
✅ Support ops can now self-serve (no more asking 7 people for data)
✅ Cross-brand SLA comparisons show BrandA2 @ 52.9% vs BrandB @ 45.2%
✅ Data is now AI-ready for plain-English queries
✅ Single source of truth

**The Stack:**
SQL, dbt, DuckDB, Python

**Key Skills Demonstrated:**
- ETL/data consolidation at scale
- Schema & semantic heterogeneity handling
- Analytics engineering best practices (raw → staging → mart)
- Reference data management (lookup tables for status mapping)
- Data quality enforcement

Check it out: github.com/theotherbrandonsoto/unified-support-tickets

#analytics #dataengineering #dbt #sql #dataconsolidation
