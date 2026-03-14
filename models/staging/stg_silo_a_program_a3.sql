-- models/staging/stg_silo_a_program_a3.sql
-- Normalize Silo A Program A3 data: parse ISO strings, convert to UTC, map status values

with source as (
    select * from {{ source('raw', 'raw_silo_a_program_a3') }}
),

normalized as (
    select
        'BrandA3' as brand,
        support_ticket_id as ticket_id,
        strptime(ticket_received_timestamp, '%Y-%m-%dT%H:%M:%S') as received_date_raw,
        strptime(ticket_closed_timestamp, '%Y-%m-%dT%H:%M:%S') as resolution_date_raw,
        ticket_status_current as ticket_status_raw,
        primary_issue,
        identified_root_cause as root_cause_label,
        resolution_action as resolution_label,
        compensation_paid as financial_compensation,
        flagged_for_escalation as escalated_to_management,
        sla_compliant as resolved_within_sla,
        customer_identifier as customer_id
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
        and sm.source_program = 'raw_silo_a_program_a3'
)

select * from with_status_mapping
