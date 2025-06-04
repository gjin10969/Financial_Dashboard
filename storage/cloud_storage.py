import os
from supabase import create_client, Client

# Set up Supabase client
url: str = "https://tcdqezqrmqylbgbbzegp.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRjZHFlenFybXF5bGJnYmJ6ZWdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTc4MDQxMjEsImV4cCI6MjAzMzM4MDEyMX0.J6k2V7wyhjmSPAqt25eoE8fnTIO4K5kV_CfYX_Wo2uE"
supabase: Client = create_client(url, key)

def upload_file_to_supabase(bucket_name: str, file_path: str, file_name: str):
    # Check if the file already exists and delete it
    existing_files = supabase.storage.from_(bucket_name).list()
    for existing_file in existing_files:
        if existing_file['name'] == file_name:
            supabase.storage.from_(bucket_name).remove([file_name])
            break
    
    with open(file_path, "rb") as file:
        file_content = file.read()
        
        # Upload the file
        response = supabase.storage.from_(bucket_name).upload(file_name, file_content)
        
        # Check response status and content
        if response.status_code == 200:
            print("File uploaded successfully!")
        else:
            print(f"Failed to upload file: {response.json()}")

# Usage
bucket_name = "fetch_data"
file_path = r"../AlgoforceDashboard/data.json"
file_name = "data.json"

upload_file_to_supabase(bucket_name, file_path, file_name)
