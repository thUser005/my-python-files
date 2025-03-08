# Suppress ALSA errors
import os,sys
from datetime import datetime
import traceback
os.environ["SDL_AUDIODRIVER"] = "dummy"

import time,pytz,gdown
import json, re, os, shutil, random
from pymongo import MongoClient
from cut_pdf import split_pdf
from compress_video import compress_video_and_replace
from file_to_drive import upload_large_file
from pdf_to_audio import pdf_to_audio
from pdf_to_images import create_video_from_pdf
from file_to_youtube import upload_video


def main(MONGO_URL, pickle_file_name,start,end):
    print("Connecting to MongoDB...")

    overal_time = 0


    DB_NAME = "links_pdf_all"
    COLLECTION_NAME = "pickle_files"

    # Connect to MongoDB Atlas
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Fetch the document where file_name = "pdf_file"
    document = collection.find_one({"file_name": "pdf_files"}, {"_id": 0, "data": 1})
    url_obj = None
    if document:
        url_obj = document.get("data", None)
        if url_obj:
            print("Fetched Data:")
        else:
            print("No data found in the document.")
    else:
        print("No document found with file_name='pdf_file'.")



    # start = int(start) if isinstance(start, int) else 0
    url_obj = url_obj[start:end]

    def download_drive_file(drive_url, filename):
        try:
            match = re.search(r"/d/([a-zA-Z0-9_-]+)", drive_url)
            if not match:
                print("Invalid Google Drive URL!")
                return False
            file_id = match.group(1)
            download_url = f"https://drive.google.com/uc?id={file_id}"
            print(f"Downloading {filename} from {drive_url}...")
            gdown.download(download_url, filename, quiet=False)
            print("Download complete!")
            return True
        except Exception as e:
            print("Error downloading file:", e)
            return False




    upload_videos_count = 0
    quata_limit_reached = False
    videos_upload_limit_reached  = False

    print("Starting processing loop...")
    for index, obj in enumerate(url_obj):
        if upload_videos_count >= 50 and quata_limit_reached == False and videos_upload_limit_reached == False:
            print("Upload limit reached breaking the system..")
            return

        print(f"{30*'-'}\n\nProcessing {index + 1}/{len(url_obj)}...")
        start_time = time.time()
        pdf_file = obj.get("file_name", "file.pdf")
        pdf_url = obj.get("link")
        audio_folder = f"audio_pages_{index}"
        pdf_folder = "pdf_images"
        srt_file = "srt_files/subtitles.ass"
        output_video_file = f"{os.path.splitext(pdf_file)[0]}.mp4"

        try:
            print(f"Downloading file: {pdf_file}")
            if not download_drive_file(pdf_url, pdf_file):
                print("Skipping file due to download failure.")
                continue

            if os.path.exists(pdf_file):
                try:
                    size_pdf = split_pdf(pdf_file)
                    if size_pdf >=200:
                      os.remove(pdf_file)
                      print("File pages greather than 200 skipping...")
                      continue



                    print("Processing PDF...")
                    pdf_to_audio(pdf_file, audio_folder)
                    video_file_path = create_video_from_pdf(pdf_file, audio_folder, output_video_file)
                except Exception as e:
                    print("Error processing PDF:", e)
                    traceback.print_exc()

                    continue

                if video_file_path:
                    # try:
                    #     print("Uploading to YouTube...")
                    #     YT_TOKEN_FILE = get_token()
                    #     clear_output(wait=True)
                    #     video_upload_to_yt = upload_video(YT_TOKEN_FILE, video_file_path)
                    #     if video_upload_to_yt:
                    #         print("Upload successful, skipping file upload.")
                    #         upload_videos_count += 1
                    #         continue
                    #     elif "limit_reached" in str(video_upload_to_yt):
                    #         videos_upload_limit_reached = True
                    #     elif "quata_limit_reached" in str(video_upload_to_yt):
                    #         quota_limit_reached = True
                    # except Exception as e:
                    #     print("Error uploading video:", e)
                    #     traceback.print_exc()


                    try:
                        video_file_path = compress_video_and_replace(video_file_path)
                        file_link = upload_large_file(video_file_path,MONGO_URL,pickle_file_name)

                        if file_link:
                            print("Removing uploaded video file...")
                            os.remove(video_file_path)
                            print(f"File uploaded: {file_link}")
                            for f in os.listdir():
                              if '.jpg' in f:os.remove(f)
                    except Exception as e:
                        print("Error uploading large file:", e)


        except Exception as e:
            print("Error during processing:", e)
        finally:
            print("Cleaning up files...")
            for file in os.listdir():
                if '.' in file and file.endswith((".pdf",".mp4",".mp3")):
                    os.remove(file)
                    print("removed file : ",file)
                    
                if '.' not in file and "__" not in file:
                    shutil.rmtree(file)
                    print("removed folder : ",file)

            print("Removing all files in /drive/trash folder")

            end_time = time.time()
            iteration_time = int(end_time - start_time) // 60
            overal_time += iteration_time
            print(f"Iteration {index} took {iteration_time} MIN \n Overall Time: {overal_time} MIN")

    print("^" * 50)
    print("\n Up to specified index items completed.. \n")
    print("^" * 50)