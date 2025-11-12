import os
import json
import sys
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_gdrive(file_path, folder_id=None):
    creds_json = os.environ.get("GDRIVE_CREDENTIALS")
    if not creds_json:
        raise RuntimeError("GDRIVE_CREDENTIALS environment variable not set")

    creds_info = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_info)
    service = build("drive", "v3", credentials=creds)

    file_metadata = {"name": os.path.basename(file_path)}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)
    uploaded = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    print(f"Uploaded file ID: {uploaded.get('id')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_to_gdrive.py <file_path> [folder_id]")
        sys.exit(1)
    upload_to_gdrive(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
