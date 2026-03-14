-- analysis/03_resolution_patterns.sql
-- Analyze how different issues are resolved across the business

select
    primary_issue,
    resolution_label,
    count(*) as frequency,
    round(sum(case when escalated_to_management then 1 else 0 end) * 100.0 / count(*), 2) as escalation_rate_pct,
    round(avg(financial_compensation), 2) as avg_compensation
from {{ ref('fct_unified_support_tickets') }}
group by primary_issue, resolution_label
having count(*) > 50
order by frequency desc
limit 15
