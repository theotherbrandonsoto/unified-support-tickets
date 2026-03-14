-- models/metrics/metrics_trends.sql
-- Daily trends for ticket volume and resolution

select
    cast(received_date as date) as trend_date,
    'daily_volume' as metric_type,
    count(*) as ticket_count,
    sum(case when resolved_within_sla then 1 else 0 end) as sla_compliant,
    round(sum(case when resolved_within_sla then 1 else 0 end) * 100.0 / count(*), 2) as sla_pct,
    count(distinct brand) as brands_represented,
    round(avg(financial_compensation), 2) as avg_compensation
from {{ ref('fct_unified_support_tickets') }}
group by cast(received_date as date)
order by trend_date desc
