-- models/metrics/metrics_quality_escalation.sql
-- Escalation and compensation metrics by brand

select
    brand,
    count(*) as total_tickets,
    sum(case when escalated_to_management then 1 else 0 end) as escalated_tickets,
    round(
        sum(case when escalated_to_management then 1 else 0 end) * 100.0 / count(*), 2
    ) as escalation_rate_pct,
    round(sum(financial_compensation), 2) as total_compensation,
    round(avg(financial_compensation), 2) as avg_compensation_per_ticket,
    round(
        sum(case when financial_compensation > 0 then 1 else 0 end) * 100.0 / count(*), 2
    ) as compensation_rate_pct
from {{ ref('fct_unified_support_tickets') }}
group by brand
order by escalation_rate_pct desc