from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle
import os
from datetime import datetime, timedelta
from pymongo import MongoClient

# MongoDB Atlas connection details
   # Replace with your actual MongoDB Atlas URL
DB_NAME = "links_pdf_all"
COLLECTION_NAME = "pickle_files"

def get_token_from_db(MONGO_URI, TOKEN_ACCOUNT_NUM):
    """Fetch token pickle data from MongoDB and convert it back to a Credentials object."""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    document = collection.find_one({"account_num": TOKEN_ACCOUNT_NUM})
    print(document)
    client.close()

    if document and "data" in document:
        pickled_data = document["data"]

        print(f"Retrieved data type from MongoDB: {type(pickled_data)}")

        if not pickled_data:
            print("Error: Retrieved empty data from MongoDB.")
            return None

        try:
            # Ensure the data is in bytes format
            if not isinstance(pickled_data, bytes):
                print("Error: Data is not in bytes format. Cannot deserialize.")
                return None

            # Convert pickled data back to Credentials object
            credentials = pickle.loads(pickled_data)
            print("Successfully loaded credentials from MongoDB.")
            return credentials
        except Exception as e:
            print(f"Error converting pickled data to Credentials object: {e}")
            return None
    else:
        print("Token not found in MongoDB or data field is missing.")
        return None



def save_token_to_db(creds, MONGO_URI, TOKEN_ACCOUNT_NUM):
    """Save updated token pickle data back to MongoDB as binary."""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Store the raw binary pickle data (no decoding)
    updated_data = pickle.dumps(creds)  # Keep it as bytes
    collection.update_one(
        {"account_num": TOKEN_ACCOUNT_NUM},
        {"$set": {"data": updated_data}},
        upsert=True
    )
    client.close()
    print("Token updated in MongoDB.")

def check_and_refresh_token(MONGO_URI,pickle_file_name):
    """Check if token is expired and refresh if needed."""
    try:
        creds = get_token_from_db(MONGO_URI,pickle_file_name)
        if not creds:
            return None

        if creds.expired or creds.expiry - datetime.utcnow() < timedelta(minutes=20):
            print("Token is about to expire or expired. Refreshing token...")
            if creds.refresh_token:
                creds.refresh(Request())
                save_token_to_db(creds,MONGO_URI,pickle_file_name)  # Save refreshed token
                print("Token refreshed successfully.")
            else:
                print("No refresh token available. Please authorize again.")
                return None
        else:
            print("Token is still valid.")

        return creds
    except Exception as e:
        print(f"Error checking or refreshing token: {e}")
        return None

def upload_large_file(file_path,MONGO_URI,pickle_file_name, chunk_size=50 * 1024 * 1024):
    """Upload a large file to Google Drive."""
    try:

        print(f"Preparing to upload file: {file_path}/{pickle_file_name}")
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None

        creds = check_and_refresh_token(MONGO_URI,pickle_file_name)
        if not creds:
            print("Token refresh failed. Cannot upload file.")
            return None

        service = build('drive', 'v3', credentials=creds)

        file_name = os.path.basename(file_path)
        print(f"File name: {file_name}")

        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_path, mimetype='application/zip', chunksize=chunk_size, resumable=True)

        print(f"Uploading {file_name} in chunks of {chunk_size // (1024 * 1024)} MB...")
        request = service.files().create(body=file_metadata, media_body=media, fields='id')

        response = None
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    print(f"Uploaded {int(status.progress() * 100)}%")
            except Exception as e:
                print(f"Error uploading chunk: {e}")
                break

        if response is not None:
            file_id = response.get("id")
            print(f"Upload complete. File ID: {file_id}")

            try:
                print(f"Making file with ID {file_id} public...")
                service.permissions().create(
                    fileId=file_id,
                    body={"role": "reader", "type": "anyone"},
                ).execute()
                print("File made public.")
            except Exception as e:
                print(f"Error setting file permissions: {e}")
                return None

            file_link = f"https://drive.google.com/file/d/{file_id}/view?usp=drivesdk"
            print(f"File link: {file_link}")
            return file_link
        else:
            print("Upload failed. No response from server.")
            return None

    except Exception as e:
        print(f"Error uploading file: {e}")
        return None
