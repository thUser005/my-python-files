import requests
import json


def upload_video(api_key, video_title, video_path):
    BASE_UPLOAD_URL = f"https://voe.sx/api/upload/server?key={api_key}"
    video_data = []

    try:
        print("Fetching delivery node URL...")
        server_response = requests.get(BASE_UPLOAD_URL)
        if server_response.status_code != 200:
            print(f"Error fetching delivery node: HTTP {server_response.status_code} - {server_response.text}")
            return None

        server_data = server_response.json()
        delivery_node_url = server_data.get("result") or server_data.get("url")
        if not delivery_node_url:
            print("Error: No delivery node URL returned from server")
            return None

        print("Delivery node URL fetched successfully")

        upload_url = f"{delivery_node_url}?key={api_key}"
        with open(video_path, "rb") as video_file:
            files = {"file": (video_path.split("/")[-1], video_file, "video/mp4")}
            data = {"title": video_title}

            print(f"Uploading video: {video_path}")
            upload_response = requests.post(upload_url, files=files, data=data)

            if upload_response.status_code == 200:
                result = upload_response.json()
                if result.get("success"):
                    print("Upload successful")
                    file_data = {
                        "file_name": video_path.split("/")[-1],
                        "path": video_path,
                        "file_code": result['file']['file_code'],
                        "direct_link": f"https://voe.sx/{result['file']['file_code']}",
                        "embed_link": f"https://voe.sx/e/{result['file']['file_code']}"
                    }
                    video_data.append(file_data)
                else:
                    print(f"Upload failed: {result.get('message', 'Details missing')}")
            else:
                print(f"Error: HTTP {upload_response.status_code} - {upload_response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")

    except FileNotFoundError:
        print(f"File not found at: {video_path}")

    except json.JSONDecodeError:
        print("Error decoding JSON response")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        if video_data:
            try:
                with open("videos_data.json", "a") as file:
                    json.dump(video_data, file, indent=4)
                    print("Video data saved successfully")
            except IOError as e:
                print(f"Error writing to file: {e}")
