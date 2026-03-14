-- models/staging/stg_silo_a_program_a2.sql
-- Normalize Silo A Program A2 data: standardize column names, handle int booleans, convert to UTC, map status values

with source as (
    select * from {{ source('raw', 'raw_silo_a_program_a2') }}
),

normalized as (
    select
        'BrandA2' as brand,
        request_id as ticket_id,
        created_at as received_date_raw,
        closed_at as resolution_date_raw,
        status as ticket_status_raw,
        issue_type as primary_issue,
        cause_analysis as root_cause_label,
        how_resolved as resolution_label,
        credit_amount as financial_compensation,
        -- Convert int booleans (1/0) to proper booleans
        is_escalated::boolean as escalated_to_management,
        met_sla::boolean as resolved_within_sla,
        user_id as customer_id
    from source
),

with_utc_conversion as (
    select
        brand,
        ticket_id,
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
        and sm.source_program = 'raw_silo_a_program_a2'
)

select * from with_status_mapping
