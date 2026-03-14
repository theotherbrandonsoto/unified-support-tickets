-- models/metrics/metrics_quality_escalation.sql
-- Escalation, compensation, and resolution quality metrics

with by_brand as (
    select
        brand,
        count(*) as total_tickets,
        sum(case when escalated_to_management then 1 else 0 end) as escalated_tickets,
        round(sum(case when escalated_to_management then 1 else 0 end) * 100.0 / count(*), 2) as escalation_rate_pct,
        sum(financial_compensation) as total_compensation,
        round(avg(financial_compensation), 2) as avg_compensation_per_ticket,
        count(distinct case when financial_compensation > 0 then 1 end) as tickets_with_compensation,
        round(count(distinct case when financial_compensation > 0 then 1 end) * 100.0 / count(*), 2) as compensation_rate_pct
    from {{ ref('fct_unified_support_tickets') }}
    group by brand
),

by_issue_resolution as (
    select
        'issue_resolution_quality' as analysis_type,
        primary_issue,
        resolution_label,
        count(*) as ticket_count,
        round(sum(case when escalated_to_management then 1 else 0 end) * 100.0 / count(*), 2) as escalation_rate_pct,
        round(sum(case when resolved_within_sla then 1 else 0 end) * 100.0 / count(*), 2) as sla_compliance_pct,
        round(avg(financial_compensation), 2) as avg_compensation
    from {{ ref('fct_unified_support_tickets') }}
    group by primary_issue, resolution_label
    having count(*) > 20
)

select
    *
from by_brand
union all
select
    null as brand,
    null as total_tickets,
    null as escalated_tickets,
    null as escalation_rate_pct,
    null as total_compensation,
    null as avg_compensation_per_ticket,
    null as tickets_with_compensation,
    null as compensation_rate_pct
from by_issue_resolution
where false  -- placeholder to match schema
