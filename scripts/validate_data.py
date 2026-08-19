import pandas as pd
def validate(file_path):
    df = pd.read_csv(file_path)
    print(f"Validating {len(df)} rows. Found {df['is_fraud'].sum()} fraud cases.")
    
if __name__ == "__main__":
    validate("data/generated/test_txns.csv")
