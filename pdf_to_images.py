import fitz, os, subprocess, random, cv2, numpy as np
import shutil,zipfile
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_audioclips

from PIL import Image
from pydub import AudioSegment

def resize_with_padding(img, target_size):
    """Resize the image while maintaining aspect ratio and adding padding."""
    w, h = img.size
    scale = min(target_size[0] / w, target_size[1] / h)
    new_w, new_h = int(w * scale), int(h * scale)

    resized_img = img.resize((new_w, new_h), Image.LANCZOS)

    # Create a blank white image with the target size
    padded_img = Image.new("RGB", target_size, (255, 255, 255))
    x_offset = (target_size[0] - new_w) // 2
    y_offset = (target_size[1] - new_h) // 2
    padded_img.paste(resized_img, (x_offset, y_offset))

    return padded_img



def extract_pdf_images(pdf_path, output_folder, target_size=(800, 1000)):
    """Extracts all pages from a PDF and saves them as images, then combines page 1 and 2 into 'img.png'."""
    try:
        os.makedirs(output_folder, exist_ok=True)
        print(f"Output folder '{output_folder}' is ready.")

        doc = fitz.open(pdf_path)
        print(f"Opened PDF: {pdf_path}")

        image_files = []
        total_pages = len(doc)
        print(f"Total pages to process: {total_pages}")

        for i in range(total_pages):
            try:
                page = doc[i]
                pix = page.get_pixmap()
                img_path = os.path.join(output_folder, f"page{i+1}.png")

                # Convert pixmap to a PIL image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # Resize while maintaining aspect ratio
                img_resized = resize_with_padding(img, target_size)

                # Save image
                img_resized.save(img_path, "PNG")
                image_files.append(img_path)

            except Exception as e:
                print(f"Error processing page {i+1}: {e}")

        print("PDF pages successfully converted to images.")


      # Combine the first two pages
        if total_pages >= 2:
            img1 = Image.open(image_files[0])
            img2 = Image.open(image_files[1])

            # Create a new blank image with double the width
            combined_width = img1.width + img2.width
            combined_height = max(img1.height, img2.height)

            combined_img = Image.new("RGB", (combined_width, combined_height), (255, 255, 255))
            combined_img.paste(img1, (0, 0))
            combined_img.paste(img2, (img1.width, 0))

            # Reduce size while keeping it under 2MB
            quality = 95  # Start with high quality
            save_path = "img.jpg"  # Save as JPEG to control quality

            while True:
                combined_img.save(save_path, "JPEG", quality=quality)
                if os.path.getsize(save_path) < 2 * 1024 * 1024 or quality <= 10:
                    break  # Stop when below 2MB or too low quality
                quality -= 5  # Reduce quality step by step

            print(f"Combined image '{save_path}' created successfully under 2MB (Quality: {quality}).")


        return image_files

    except Exception as e:
        print(f"Failed to process PDF: {e}")
        return []
    finally:
        doc.close()


def get_audio_duration(audio_path):
    """Gets the duration of an audio file using pydub and adds 2 extra seconds."""
    audio = AudioSegment.from_file(audio_path)
    duration = len(audio) / 1000  # Convert milliseconds to seconds
    return duration + 2  # Add 2 extra seconds



def add_watermark_to_folder(folder_path):
    # Check if the folder exists
    if not os.path.isdir(folder_path):
        print(f"Folder {folder_path} not found!")
        return False

    # Get all image files in the folder
    image_files = [f for f in os.listdir(folder_path) if f.startswith("page") and f.endswith(".png")]

    # Sort files based on the numeric part after "page" (e.g., page1.png, page2.png, ...)
    image_files.sort(key=lambda x: int(x.replace("page", "").replace(".png", "")))

    if not image_files:
        print(f"No PNG images found in folder {folder_path}!")
        return False
    sub_lst = ['Subscribe @TimeForEpics','Subscribe @TimeForEpics_01','Subscribe @TimeForEpics_02']

    for index, image_file in enumerate(image_files, start=1):
        image_path = os.path.join(folder_path, image_file)
        page_number = os.path.splitext(image_file)[0]  # Extract "pageX"

        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Unable to read the image {image_path}! Skipping...")
            continue

        # Get image dimensions
        height, width, _ = image.shape

        # Create a transparent overlay for the watermark
        overlay = image.copy()

        # Extract page number
        page = page_number.replace("page", "")

        # Define font
        font = cv2.FONT_HERSHEY_SIMPLEX

        # **Page Number Properties**
        page_font_scale = 3
        page_font_thickness = 3
        page_color = (255, 0, 0)  # Blue
        page_shadow_color = (0, 0, 0)  # Black
        page_opacity = 0.3

        # **Fixed position for page number watermark** (Bottom-right corner)
        page_text = page_number
        (page_text_width, page_text_height), _ = cv2.getTextSize(page_text, font, page_font_scale, page_font_thickness)
        page_x = width - page_text_width - 50
        page_y = height - 50

        random.shuffle(sub_lst)
        sub_text = f"Like / Comment / {sub_lst[0]}"

        # **List of "Subscribe" watermarks**
        subscribe_texts = [
            (sub_text, (0, 0, 255), 1),  # Red, Font 1.5
            (sub_text, (0, 0, 255), 1),  # Blue, Font 1.8
            (sub_text, (0, 0,255), 1),  # Green, Font 2.0
        ]

        # **Generate 3 distinct Y positions**
        y_positions = random.sample(range(50, height - 50, 100), 3)

        for i, (text, color, scale) in enumerate(subscribe_texts):
            text_width, text_height = cv2.getTextSize(text, font, scale, 2)[0]
            text_x = (width - text_width) // 2
            text_y = y_positions[i]

            # Add shadow
            cv2.putText(overlay, text, (text_x + 2, text_y + 2), font, scale, (0, 0, 0), 3, cv2.LINE_AA)
            # Add actual text
            cv2.putText(overlay, text, (text_x, text_y), font, scale, color, 2, cv2.LINE_AA)

        # Add page number watermark (Bottom-right corner)
        cv2.putText(overlay, page_text, (page_x + 2, page_y + 2), font, page_font_scale, page_shadow_color, page_font_thickness + 1, cv2.LINE_AA)
        cv2.putText(overlay, page_text, (page_x, page_y), font, page_font_scale, page_color, page_font_thickness, cv2.LINE_AA)

        # Blend the overlay with the original image
        watermarked_image = cv2.addWeighted(overlay, page_opacity, image, 1 - page_opacity, 0)

        # Save the watermarked image
        temp_output_path = os.path.join(folder_path, f"temp_{image_file}")
        cv2.imwrite(temp_output_path, watermarked_image)

        # Replace original image
        os.remove(image_path)
        os.rename(temp_output_path, image_path)

    print(f"Watermarking completed for all images in {folder_path}")
    return True




def create_opencv_video(image_files, durations, output_video="silent_video.mp4", fps=2):
    """Create a silent video using images with specified durations using OpenCV."""
    try:
        print("Starting video creation using OpenCV...")

        if not image_files or not durations:
            raise ValueError("Error: The image list or durations list is empty!")

        if len(image_files) != len(durations):
            raise ValueError("Error: The number of images and durations must be the same!")

        print(f"Total images: {len(image_files)}")
        print(f"Durations: {len(durations)}")

        # Read the first image to get dimensions
        first_image = cv2.imread(image_files[0])
        if first_image is None:
            raise FileNotFoundError(f"Error: Could not read the first image {image_files[0]}")

        height, width, layers = first_image.shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 output
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

        print("Processing images...")
        for img_path, duration in zip(image_files, durations):
            img = cv2.imread(img_path)
            if img is None:
                raise FileNotFoundError(f"Error: Could not read image {img_path}")

            num_frames = int(duration * fps)  # Convert duration to frame count
            for _ in range(num_frames):
                out.write(img)  # Write image frame multiple times

        out.release()
        print(f"✅ Video created successfully: {output_video}")

    except ValueError as ve:
        print(f"❌ ValueError: {ve}")

    except FileNotFoundError as fe:
        print(f"❌ FileNotFoundError: {fe}")

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

    return output_video


def merge_audio_files(audio_folder, output_audio="final_audio.mp3"):
    """Merge all audio files into a single track using FFmpeg."""
    list_file = "audio_list.txt"
    try:
        print("Searching for audio files...")
        audio_files_lst = os.listdir(audio_folder)
        audio_files = []

        for i in range(len(audio_files_lst)):
            audio_file = f"page{i+1}.mp3"
            audio_file = os.path.join(audio_folder,audio_file)

            audio_files.append(audio_file)

        if not audio_files:
            print("No audio files found.")
            return None

        print(f"Found {len(audio_files)} audio files. Creating list file...")
        with open(list_file, "w") as f:
            for audio in audio_files:
                f.write(f"file '{audio}'\n")
        print(f"Audio list file '{list_file}' created successfully.")

        print("Merging audio files using FFmpeg...")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output_audio],
            stdout=subprocess.DEVNULL,  # Suppress standard output
            stderr=subprocess.DEVNULL   # Suppress error messages
        )
        print(f"Audio merged successfully into '{output_audio}'.")
        return output_audio
    except Exception as e:
        print("Error : 205", e)
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)
            print(f"Temporary file '{list_file}' deleted.")


def combine_video_audio(video_path, audio_path, output_final="final_video.mp4"):
    """Merge the silent video with the final audio track and show FFmpeg output."""
    print("Checking video and audio files...")
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' is missing!")
        return None
    if not os.path.exists(audio_path):
        print(f"Error: Audio file '{audio_path}' is missing!")
        return None

    print("Merging video and audio using FFmpeg...")

    process = subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", output_final],
        stdout=subprocess.DEVNULL,  # Discards stdout
        stderr=subprocess.DEVNULL,  # Discards stderr
    )


    print(f"Final video '{output_final}' created successfully.")
    return output_final



def create_video_from_pdf(pdf_path, audio_folder="audio_pages", output_prefix="output_part"):
    """Creates a video from a PDF where each page is displayed based on the duration of its audio and zips the output files."""

    try:
        output_folder = "pdf_images"
        print("Starting video creation process...")

        # Step 1: Extract images from the PDF
        image_files = extract_pdf_images(pdf_path, output_folder)
        print(f"Extracted {len(image_files)} images from PDF.")

        add_watermark_to_folder(output_folder)
        print("Watermark added to images.")

        image_files_temp = os.listdir(output_folder)
        image_files = []
        for i in range(len(image_files_temp)):

            img = os.path.join(output_folder, f"page{i+1}.png")
            image_files.append(img)

        print("Fetcing audio duration list..")
        durations = []
        for i in range(len(image_files)):
            audio_path = os.path.join(audio_folder, f"page{i+1}.mp3")
            duration = get_audio_duration(audio_path)
            durations.append(duration)
        print("Fetcing audio duration list sucessflly fetched..")

        # Step 3: Divide pages into parts

        print("Creating silent video with FFmpeg...")
        silent_video = create_opencv_video(image_files, durations)

        silent_video = 'silent_video.mp4'

        print("Merging audio files...")
        final_audio = merge_audio_files(audio_folder)

        final_audio = 'final_audio.mp3'

        print("Combining video and audio...")
        # Remove extra spaces and strip trailing spaces
        output_prefix = " ".join(output_prefix.split()).strip()

        final_video = combine_video_audio(silent_video, final_audio, output_prefix)

        print(f"Video creation completed: {final_video}")

        return final_video if os.path.exists(final_video) else None


    except Exception as e:
        print(f"Unexpected error: {e}")
        return None




# Example usage
# create_video_from_pdf("example.pdf", "audio_pages", "output_video")

