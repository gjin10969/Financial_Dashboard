import os
import json
from supabase import create_client, Client

# Set up Supabase client
url: str = "https://tcdqezqrmqylbgbbzegp.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRjZHFlenFybXF5bGJnYmJ6ZWdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTc4MDQxMjEsImV4cCI6MjAzMzM4MDEyMX0.J6k2V7wyhjmSPAqt25eoE8fnTIO4K5kV_CfYX_Wo2uE"
supabase: Client = create_client(url, key)

def read_and_print_json_from_supabase(bucket_name: str, file_name: str):
    response = supabase.storage.from_(bucket_name).download(file_name)
    
    if response:
        json_data = json.loads(response.decode("utf-8"))
        print(json_data)
    else:
        print(f"Failed to read JSON from Supabase storage.")

# Usage
bucket_name = "fetch_data"
file_name = "data.json"

read_and_print_json_from_supabase(bucket_name, file_name)
