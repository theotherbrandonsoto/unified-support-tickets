-- models/metrics/metrics_sla_resolution.sql
-- SLA compliance and resolution time metrics by brand

select
    brand,
    count(*) as total_tickets,
    sum(case when resolved_within_sla then 1 else 0 end) as sla_compliant_tickets,
    sum(case when not resolved_within_sla then 1 else 0 end) as sla_missed_tickets,
    round(sum(case when resolved_within_sla then 1 else 0 end) * 100.0 / count(*), 2) as sla_compliance_pct
from {{ ref('fct_unified_support_tickets') }}
group by brand
order by sla_compliance_pct desc
