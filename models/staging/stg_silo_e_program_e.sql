-- models/staging/stg_silo_e_program_e.sql
-- Normalize Silo E Program E data: standardize column names, convert to UTC, map status values

with source as (
    select * from {{ source('raw', 'raw_silo_E_program_e') }}
),

normalized as (
    select
        brand,
        ticket_id,
        received_date_utc as received_date_raw,
        resolved_date_utc as resolution_date_raw,
        status as ticket_status_raw,
        issue as primary_issue,
        root_cause as root_cause_label,
        resolution as resolution_label,
        refund as financial_compensation,
        escalated as escalated_to_management,
        sla_met as resolved_within_sla,
        customer_id
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
        and sm.source_program = 'raw_silo_E_program_e'
)

select * from with_status_mapping
