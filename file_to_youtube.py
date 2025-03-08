import os
import shutil
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from datetime import datetime, timezone, timedelta

SCOPES = ["https://www.googleapis.com/auth/youtube"]
CATEGORY_ID = "22"  # People & Blogs
INITIAL_PRIVACY_STATUS = "private"  # Start as private for scheduling
IS_FOR_KIDS = False

def force_delete(file_path):
    """Forcefully delete the video file after upload."""
    try:
        print(f"🗑️ Attempting to delete {file_path}")
        shutil.rmtree(file_path, ignore_errors=True)
        print(f"✅ Successfully deleted {file_path}")
    except PermissionError:
        print(f"⚠️ Permission denied while deleting {file_path}")

def authenticate_youtube(token_file):
    """Authenticate with YouTube API using the token file."""
    print("🔑 Authenticating YouTube API...")
    credentials = None
    if os.path.exists(token_file):
        credentials = Credentials.from_authorized_user_file(token_file, SCOPES)
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    print("✅ Authentication successful!")
    return build("youtube", "v3", credentials=credentials)

def get_scheduled_time():
    """Schedules YouTube uploads 45 minutes from the current time."""
    now = datetime.now(timezone.utc)
    scheduled_time = now + timedelta(minutes=45)
    print(f"⏳ Scheduling video for: {scheduled_time.isoformat()}")
    return scheduled_time.isoformat().replace("+00:00", "Z")



def upload_video(token_file, video_path):
    """Upload a single video with scheduling and cleanup, returning False if upload fails."""
    print("🚀 Starting upload process...")
    video_data = extract_video_data(video_path)
    seo_name, video_description, video_full_path, img_full_path, seo_keywords = video_data
    youtube = authenticate_youtube(token_file)

    if not os.path.exists(video_full_path):
        print(f"❌ Error: Video file '{video_full_path}' not found!")
        return False

    # Ensure tags fit within YouTube's 500-character limit
    max_tag_length = 500
    filtered_tags = []
    total_length = 0

    for tag in seo_keywords:
        if total_length + len(tag) + 2 > max_tag_length:  # +2 for comma + space
            break
        filtered_tags.append(tag)
        total_length += len(tag) + 2

    print(f"📤 Uploading video: {seo_name}")
    scheduled_time = get_scheduled_time()
    request_body = {
        "snippet": {
            "title": seo_name,
            "description": video_description,  # Use fetched description
            "categoryId": CATEGORY_ID,
            "tags": filtered_tags,  # Include only allowed tags
        },
        "status": {
            "privacyStatus": INITIAL_PRIVACY_STATUS,
            "publishAt": scheduled_time,
            "selfDeclaredMadeForKids": IS_FOR_KIDS,
        },
    }

    media = MediaFileUpload(video_full_path, chunksize=1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)

    try:
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.resumable_progress * 100 / os.path.getsize(video_full_path))
                print(f"\r📊 Progress: {progress}%", end="", flush=True)

        print(f"\n✅ Video uploaded! ID: {response['id']}")
        print(f"📅 Scheduled for: {scheduled_time}")
        print(f"📺 Watch here: https://www.youtube.com/watch?v={response['id']}")

        # Upload thumbnail if available
        if img_full_path and os.path.exists(img_full_path):
            print(f"🖼️ Uploading thumbnail: {img_full_path}")
            try:
                youtube.thumbnails().set(videoId=response['id'], media_body=MediaFileUpload(img_full_path)).execute()
                print("✅ Thumbnail uploaded successfully!")
            except HttpError as thumbnail_error:
                print(f"⚠️ Thumbnail upload failed: {str(thumbnail_error)}")

        # Cleanup video file after successful upload
        force_delete(video_full_path)
        return True

    except HttpError as e:
        error_msg = str(e).lower()
        print(f"❌ HTTP error encountered: {error_msg}")

        try:
            reason = e.error_details[0].get("reason", "Unknown reason")
            print(f"🛑 Error Reason: {reason}\n{e}")
            if "uploadlimitexceeded" in reason or "daily limit" in error_msg:
                print("🚨 Quota limit reached. Stopping further uploads.")
                return "limit_reached"
            elif "quato" in reason or "forbidden" in error_msg:
                print(f"🚨 token quato limit reached..\n{e}")
                return "quato_limit_reached"
            elif "invalid" in error_msg or "forbidden" in error_msg:
                print(f"🚨 Authentication or permission error. Check API credentials.\n{e}")
                return False
            else:
                print("🚨 Unknown HTTP error occurred.")
                return False
        except (AttributeError, IndexError, KeyError):
            print("🛑 Could not extract error reason.")




    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False
