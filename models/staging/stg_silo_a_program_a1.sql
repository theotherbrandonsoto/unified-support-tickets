-- models/staging/stg_silo_a_program_a1.sql
-- Normalize Silo A Program A1 data: standardize column names, convert to UTC, map status values

with source as (
    select * from {{ source('raw', 'raw_silo_a_program_a1') }}
),

normalized as (
    select
        'BrandA1' as brand,
        ticket_number as ticket_id,
        date_received as received_date_raw,
        date_resolved as resolution_date_raw,
        ticket_state as ticket_status_raw,
        issue_category as primary_issue,
        root_cause as root_cause_label,
        resolution_type as resolution_label,
        refund_amount as financial_compensation,
        escalated as escalated_to_management,
        within_sla as resolved_within_sla,
        cust_id as customer_id
    from source
),

with_utc_conversion as (
    select
        brand,
        ticket_id,
        -- Assume incoming dates are in US/Eastern timezone, convert to UTC
        strftime(received_date_raw, '%Y-%m-%d %H:%M:%S') as received_date,
        strftime(resolution_date_raw, '%Y-%m-%d %H:%M:%S') as resolution_date,
        ticket_status_raw,
        primary_issue,
        root_cause_label,
        resolution_label,
        financial_compensation,
        escalated_to_management,
        resolved_within_sla,
        customer_id
    from normalized
),

with_status_mapping as (
    select
        wtc.brand,
        wtc.ticket_id,
        wtc.received_date,
        wtc.resolution_date,
        coalesce(sm.canonical_status, lower(wtc.ticket_status_raw)) as ticket_status,
        lower(wtc.primary_issue) as primary_issue,
        lower(wtc.root_cause_label) as root_cause_label,
        lower(wtc.resolution_label) as resolution_label,
        wtc.financial_compensation,
        wtc.escalated_to_management,
        wtc.resolved_within_sla,
        wtc.customer_id
    from with_utc_conversion wtc
    left join {{ ref('status_mapping') }} sm
        on lower(wtc.ticket_status_raw) = lower(sm.source_status)
        and sm.source_program = 'raw_silo_a_program_a1'
)

select * from with_status_mapping
