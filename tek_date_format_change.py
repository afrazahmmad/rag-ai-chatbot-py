import pandas as pd

# Load file
file_path = "VS_471249.csv"
df = pd.read_csv(file_path)

# List of date columns
date_columns = ['SoldTime', 'dealCreatedTime', 'closedTime']

# Convert formats
for col in date_columns:
    df[col] = pd.to_datetime(df[col], format='%m-%d-%y').dt.strftime('%Y-%m-%d')

# Save back to same file
df.to_csv(file_path, index=False)

print("Date columns updated and file saved successfully!")
