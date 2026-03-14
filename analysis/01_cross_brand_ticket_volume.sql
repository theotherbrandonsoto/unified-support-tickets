-- analysis/01_cross_brand_ticket_volume.sql
-- Show ticket volume by brand and status - demonstrates cross-brand visibility

select
    brand,
    ticket_status,
    count(*) as ticket_count,
    round(count(*) * 100.0 / sum(count(*)) over (partition by brand), 2) as pct_of_brand
from {{ ref('fct_unified_support_tickets') }}
group by brand, ticket_status
order by brand, ticket_count desc
