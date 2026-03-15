import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Connect to DuckDB
conn = duckdb.connect('./unified_support_tickets.duckdb')

# Helper function to generate dates
def generate_dates(n, start_date='2024-01-01', end_date='2024-12-31'):
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    dates = [start + timedelta(days=random.randint(0, (end - start).days)) for _ in range(n)]
    return sorted(dates)

# Resolution labels (will vary by source, then get mapped)
resolution_labels_raw = [
    'refund_issued', 'password_reset', 'account_restored', 
    'escalated_to_engineering', 'no_action_needed', 'billing_adjustment',
    'technical_support_provided', 'data_correction'
]

# Issues (will vary by source naming)
issues = [
    'login_issue', 'billing_problem', 'feature_request', 'data_access', 
    'payment_failed', 'account_locked', 'performance_issue', 'data_export'
]

root_causes = [
    'user_error', 'system_bug', 'database_issue', 'integration_failure',
    'third_party_api', 'user_misconfiguration', 'system_maintenance', 'unclear_process'
]

# ============================================================================
# SILO A: 3 COMPLAINT PROGRAMS (bundled together but with different naming)
# ============================================================================

print("Generating Silo A - Program A1...")
n_rows = 1000
received_dates_a1 = generate_dates(n_rows)
resolution_dates_a1 = [rd + timedelta(hours=random.randint(1, 168)) for rd in received_dates_a1]

data_a1 = {
    'ticket_number': [f'TKT-A1-{i:06d}' for i in range(n_rows)],
    'brand_name': ['BrandA1'] * n_rows,
    'date_received': received_dates_a1,
    'date_resolved': resolution_dates_a1,
    'ticket_state': [random.choice(['open', 'closed', 'in_progress', 'pending']) for _ in range(n_rows)],
    'issue_category': [random.choice(issues) for _ in range(n_rows)],
    'root_cause': [random.choice(root_causes) for _ in range(n_rows)],
    'resolution_type': [random.choice(resolution_labels_raw) for _ in range(n_rows)],
    'refund_amount': [round(random.uniform(0, 500), 2) if random.random() > 0.7 else 0.0 for _ in range(n_rows)],
    'escalated': [random.choice([True, False]) for _ in range(n_rows)],
    'within_sla': [random.choice([True, False]) for _ in range(n_rows)],
    'cust_id': [f'CUST-{random.randint(1000, 9999)}' for _ in range(n_rows)],
}
df_a1 = pd.DataFrame(data_a1)
conn.execute("CREATE OR REPLACE TABLE raw_silo_a_program_a1 AS SELECT * FROM df_a1")
print(f"✓ Created raw_silo_a_program_a1 with {len(df_a1)} rows")

print("Generating Silo A - Program A2...")
received_dates_a2 = generate_dates(n_rows)
resolution_dates_a2 = [rd + timedelta(hours=random.randint(1, 168)) for rd in received_dates_a2]

data_a2 = {
    'request_id': [f'REQ-A2-{i:06d}' for i in range(n_rows)],
    'brand': ['BrandA2'] * n_rows,
    'created_at': received_dates_a2,
    'closed_at': resolution_dates_a2,
    'status': [random.choice(['OPEN', 'CLOSED', 'IN_PROGRESS', 'WAITING']) for _ in range(n_rows)],  # Different naming!
    'issue_type': [random.choice(issues) for _ in range(n_rows)],
    'cause_analysis': [random.choice(root_causes) for _ in range(n_rows)],
    'how_resolved': [random.choice(resolution_labels_raw) for _ in range(n_rows)],
    'credit_amount': [round(random.uniform(0, 500), 2) if random.random() > 0.7 else 0.0 for _ in range(n_rows)],
    'is_escalated': [random.choice([1, 0]) for _ in range(n_rows)],  # Boolean as int
    'met_sla': [random.choice([1, 0]) for _ in range(n_rows)],
    'user_id': [f'USER-{random.randint(10000, 99999)}' for _ in range(n_rows)],
}
df_a2 = pd.DataFrame(data_a2)
conn.execute("CREATE OR REPLACE TABLE raw_silo_a_program_a2 AS SELECT * FROM df_a2")
print(f"✓ Created raw_silo_a_program_a2 with {len(df_a2)} rows")

print("Generating Silo A - Program A3...")
received_dates_a3 = generate_dates(n_rows)
resolution_dates_a3 = [rd + timedelta(hours=random.randint(1, 168)) for rd in received_dates_a3]

data_a3 = {
    'support_ticket_id': [f'SUP-A3-{i:06d}' for i in range(n_rows)],
    'merchant_name': ['BrandA3'] * n_rows,
    'ticket_received_timestamp': [rd.isoformat() for rd in received_dates_a3],  # ISO format string
    'ticket_closed_timestamp': [rd.isoformat() for rd in resolution_dates_a3],
    'ticket_status_current': [random.choice(['open', 'closed', 'wip', 'hold']) for _ in range(n_rows)],  # Different again!
    'primary_issue': [random.choice(issues) for _ in range(n_rows)],
    'identified_root_cause': [random.choice(root_causes) for _ in range(n_rows)],
    'resolution_action': [random.choice(resolution_labels_raw) for _ in range(n_rows)],
    'compensation_paid': [round(random.uniform(0, 500), 2) if random.random() > 0.7 else 0.0 for _ in range(n_rows)],
    'flagged_for_escalation': [random.choice([True, False]) for _ in range(n_rows)],
    'sla_compliant': [random.choice([True, False]) for _ in range(n_rows)],
    'customer_identifier': [f'CID-{random.randint(100000, 999999)}' for _ in range(n_rows)],
}
df_a3 = pd.DataFrame(data_a3)
conn.execute("CREATE OR REPLACE TABLE raw_silo_a_program_a3 AS SELECT * FROM df_a3")
print(f"✓ Created raw_silo_a_program_a3 with {len(df_a3)} rows")

# ============================================================================
# SILOS B, C, D, E: 4 STANDALONE PROGRAMS (completely independent)
# ============================================================================

for silo_name, program_name in [('B', 'program_b'), ('C', 'program_c'), ('D', 'program_d'), ('E', 'program_e')]:
    print(f"Generating Silo {silo_name}...")
    received_dates = generate_dates(n_rows)
    resolution_dates = [rd + timedelta(hours=random.randint(1, 168)) for rd in received_dates]
    
    data = {
        'ticket_id': [f'TKT-{silo_name}-{i:06d}' for i in range(n_rows)],
        'brand': [f'Brand{silo_name}'] * n_rows,
        'received_date_utc': received_dates,
        'resolved_date_utc': resolution_dates,
        'status': [random.choice(['NEW', 'ACTIVE', 'RESOLVED', 'PENDING_REVIEW']) for _ in range(n_rows)],  # Yet another format!
        'issue': [random.choice(issues) for _ in range(n_rows)],
        'root_cause': [random.choice(root_causes) for _ in range(n_rows)],
        'resolution': [random.choice(resolution_labels_raw) for _ in range(n_rows)],
        'refund': [round(random.uniform(0, 500), 2) if random.random() > 0.7 else 0.0 for _ in range(n_rows)],
        'escalated': [random.choice([True, False]) for _ in range(n_rows)],
        'sla_met': [random.choice([True, False]) for _ in range(n_rows)],
        'customer_id': [f'CUST-{silo_name}-{random.randint(1000, 9999)}' for _ in range(n_rows)],
    }
    df = pd.DataFrame(data)
    table_name = f'raw_silo_{silo_name}_{program_name}'
    conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
    print(f"✓ Created {table_name} with {len(df)} rows")

print("\n✅ All raw data tables created successfully!")
conn.close()
