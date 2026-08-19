import json
import os

def generate_dictionary():
    schema_path = "data/schemas/transaction_schema.json"
    if not os.path.exists(schema_path):
        print(f"❌ Schema not found at {schema_path}")
        return
        
    with open(schema_path, "r") as f:
        schema = json.load(f)
        
    md_content = f"""# AEGIS Data Dictionary

**Description:** {schema.get('description', 'AEGIS Transaction Schema')}

## Features

### Numeric Features
"""
    for feat in schema.get('numeric_features', []):
        md_content += f"- `{feat}`: Numeric\n"

    md_content += "\n### Boolean Features\n"
    for feat in schema.get('boolean_features', []):
        md_content += f"- `{feat}`: Boolean\n"
        
    md_content += "\n### Categorical Features\n"
    for feat in schema.get('categorical_features', []):
        md_content += f"- `{feat}`: Categorical\n"

    md_content += f"\n## Target Label\n- `{schema.get('label', 'is_fraud')}`\n"
    
    out_dir = "docs"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "data_dictionary.md")
    
    with open(out_path, "w") as f:
        f.write(md_content)
        
    print(f"✅ Generated Data Dictionary at: {out_path}")

if __name__ == "__main__":
    generate_dictionary()
