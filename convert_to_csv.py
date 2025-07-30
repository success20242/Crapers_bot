import pandas as pd
import json

# Path to your saved JSON file
json_file = "data/predictions_20250730.json"

# Load the JSON data
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert to a DataFrame
df = pd.DataFrame(data)

# Save to CSV
csv_file = "data/predictions_20250730.csv"
df.to_csv(csv_file, index=False)

print(f"✅ CSV file saved to {csv_file}")
