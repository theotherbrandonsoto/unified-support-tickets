-- models/metrics/metrics_volume_distribution.sql
-- Ticket volume and distribution metrics by brand, status, and issue type

with by_brand_status as (
    select
        'by_brand_status' as metric_type,
        brand,
        ticket_status,
        null as primary_issue,
        count(*) as ticket_count,
        round(count(*) * 100.0 / sum(count(*)) over (partition by brand), 2) as pct_of_brand,
        round(avg(case when financial_compensation > 0 then financial_compensation else null end), 2) as avg_compensation
    from {{ ref('fct_unified_support_tickets') }}
    group by brand, ticket_status
),

by_brand_issue as (
    select
        'by_brand_issue' as metric_type,
        brand,
        null as ticket_status,
        primary_issue,
        count(*) as ticket_count,
        round(count(*) * 100.0 / sum(count(*)) over (partition by brand), 2) as pct_of_brand,
        round(avg(case when financial_compensation > 0 then financial_compensation else null end), 2) as avg_compensation
    from {{ ref('fct_unified_support_tickets') }}
    group by brand, primary_issue
),

combined as (
    select * from by_brand_status
    union all
    select * from by_brand_issue
)

select * from combined
