# AEGIS Data Dictionary

**Description:** AEGIS Transaction Schema — Single Source of Truth

## Features

### Numeric Features
- `amount_inr`: Numeric
- `hour_of_day`: Numeric
- `day_of_week`: Numeric
- `sender_account_age_days`: Numeric
- `sender_avg_monthly_txn_count`: Numeric
- `sender_avg_monthly_spend_inr`: Numeric
- `sender_credit_score`: Numeric
- `txn_count_last_1h`: Numeric
- `txn_count_last_24h`: Numeric
- `txn_amount_last_24h`: Numeric
- `unique_receivers_last_24h`: Numeric
- `unique_devices_last_7d`: Numeric
- `amount_zscore`: Numeric
- `time_since_last_txn_seconds`: Numeric

### Boolean Features
- `is_weekend`: Boolean
- `is_festival_period`: Boolean
- `is_international`: Boolean
- `is_new_receiver`: Boolean
- `is_new_device`: Boolean

### Categorical Features
- `payment_rail`: Categorical
- `mcc_code`: Categorical
- `sender_persona`: Categorical
- `channel`: Categorical
- `sender_city`: Categorical

## Target Label
- `is_fraud`
