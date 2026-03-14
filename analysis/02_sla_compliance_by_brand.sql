-- analysis/02_sla_compliance_by_brand.sql
-- Compare SLA compliance across all brands - shows new cross-brand metrics

select
    brand,
    count(*) as total_tickets,
    sum(case when resolved_within_sla then 1 else 0 end) as sla_compliant,
    round(sum(case when resolved_within_sla then 1 else 0 end) * 100.0 / count(*), 2) as sla_compliance_pct,
    round(avg(case when financial_compensation > 0 then financial_compensation else null end), 2) as avg_compensation_when_issued
from {{ ref('fct_unified_support_tickets') }}
group by brand
order by sla_compliance_pct desc
