-- models/mart/fct_unified_support_tickets.sql
-- Final unified support tickets table
-- Combines all 7 staging models into a single canonical fact table
-- Primary key: brand + ticket_id

with silo_a_program_a1 as (
    select * from {{ ref('stg_silo_a_program_a1') }}
),

silo_a_program_a2 as (
    select * from {{ ref('stg_silo_a_program_a2') }}
),

silo_a_program_a3 as (
    select * from {{ ref('stg_silo_a_program_a3') }}
),

silo_b_program_b as (
    select * from {{ ref('stg_silo_b_program_b') }}
),

silo_c_program_c as (
    select * from {{ ref('stg_silo_c_program_c') }}
),

silo_d_program_d as (
    select * from {{ ref('stg_silo_d_program_d') }}
),

silo_e_program_e as (
    select * from {{ ref('stg_silo_e_program_e') }}
),

unified as (
    select * from silo_a_program_a1
    union all
    select * from silo_a_program_a2
    union all
    select * from silo_a_program_a3
    union all
    select * from silo_b_program_b
    union all
    select * from silo_c_program_c
    union all
    select * from silo_d_program_d
    union all
    select * from silo_e_program_e
),

final as (
    select
        brand,
        ticket_id,
        received_date,
        resolution_date,
        ticket_status,
        primary_issue,
        root_cause_label,
        resolution_label,
        financial_compensation,
        escalated_to_management,
        resolved_within_sla,
        customer_id
    from unified
)

select * from final
