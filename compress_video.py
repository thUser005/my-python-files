import os
import subprocess

def compress_video_and_replace(original_file_path):
    # Check if the file exists
    if not os.path.exists(original_file_path):
        raise FileNotFoundError(f"Original file not found: {original_file_path}")

    # Get the original file name and directory
    dir_name, original_file_name = os.path.split(original_file_path)
    output_file_path = os.path.join(dir_name, 'compressed_' + original_file_name)

    # Get the original file size (in bytes)
    original_file_size = os.path.getsize(original_file_path)
    original_file_size = int(original_file_size / (1024 * 1024))
    print(f"Original file size: {original_file_size / (1024 * 1024):.2f} MB")

    if original_file_size <= 160:
      return original_file_path
    # Run FFmpeg command to compress the video
    ffmpeg_command = [
        'ffmpeg', '-i', original_file_path, '-vcodec', 'libx264', '-crf', '28', output_file_path
    ]

    try:
        # Execute the compression command
        subprocess.run(ffmpeg_command, check=True)

        # Get the compressed file size (in bytes)
        compressed_file_size = os.path.getsize(output_file_path)
        print(f"Compressed file size: {compressed_file_size / (1024 * 1024):.2f} MB")

        # Remove the original file
        os.remove(original_file_path)

        # Rename the output file to the original file name
        os.rename(output_file_path, original_file_path)

        # Check if the file exists after renaming
        if os.path.exists(original_file_path):
            return original_file_name
        else:
            raise FileNotFoundError(f"Compressed file was not found after renaming: {original_file_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error during FFmpeg processing: {e}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
