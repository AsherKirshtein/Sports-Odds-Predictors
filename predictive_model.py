import boto3
import pandas as pd
from io import StringIO

# Initialize the S3 client
s3 = boto3.client('s3')

# Specify the bucket name and base prefix
bucket_name = 'sportspredictionbucket'
base_prefix = 'CSV/'

# Function to read CSV file from S3 and return it as a pandas DataFrame
def read_csv_from_s3(bucket, key):
    try:
        s3_object = s3.get_object(Bucket=bucket, Key=key)
        content = s3_object['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(content))
        return df
    except Exception as e:
        print(f"Error reading {key}: {e}")
        return None

# Loop through folders from 1955 to 2024 and read the CSV files
for year in range(2023, 2025):
    prefix = f'{base_prefix}{year}/'
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    # Check if there are files in the folder
    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            if key.endswith('.csv'):  # Only process CSV files
                print(f"Reading CSV file: {key}")
                df = read_csv_from_s3(bucket_name, key)
                if df is not None:
                    print(df.head())  # Print the first few rows of each CSV file
    else:
        print(f"No files found for the year {year}")