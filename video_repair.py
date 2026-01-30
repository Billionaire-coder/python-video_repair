import subprocess
import os
import sys

# --- Configuration ---
# You must have FFmpeg installed and accessible in your system's PATH.

def repair_video(input_path):
    """
    Attempts to repair a video file by using FFmpeg to remux and copy streams.
    This often fixes issues related to broken headers or index tables.

    Args:
        input_path (str): The full path to the potentially corrupt video file.
    """
    # 1. Check if the input file exists
    if not os.path.exists(input_path):
        print(f"Error: The file '{input_path}' was not found.")
        return

    # 2. Determine the output path
    # Get the directory, base filename, and extension
    directory = os.path.dirname(input_path)
    filename_without_ext, extension = os.path.splitext(os.path.basename(input_path))

    # Construct the new filename
    output_filename = f"{filename_without_ext}_noncorrupt{extension}"
    output_path = os.path.join(directory, output_filename)

    print("-" * 50)
    print(f"Input file: {input_path}")
    print(f"Output file will be saved as: {output_path}")
    print("Attempting repair using FFmpeg (This may take a few moments)...")
    print("-" * 50)

    # 3. Construct the FFmpeg command
    # -i: Input file
    # -c copy: Copy the existing video and audio streams without re-encoding (faster)
    # -movflags faststart: Optimizes file structure for web streaming (good practice)
    # -map 0:0 -map 0:1: Explicitly map the first video and audio stream (optional, but robust)
    
    # We use 'copy' to preserve quality and speed up the process.
    # If a deeper repair (re-encoding) is needed, you might replace '-c copy'
    # with '-c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k'

    command = [
        'ffmpeg',
        '-i', input_path,
        '-c', 'copy',
        '-movflags', 'faststart',
        '-y',  # Overwrite output file without asking
        output_path
    ]

    # 4. Execute the FFmpeg command
    try:
        # We run the command and capture/stream output to the console
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # Print FFmpeg output in real-time
        for line in process.stderr:
            sys.stderr.write(line)

        process.wait()

        if process.returncode == 0:
            print("-" * 50)
            print(f"✅ Success: Video successfully processed and saved to:\n{output_path}")
            print("Please check the new file for playback issues.")
            print("-" * 50)
        else:
            print("-" * 50)
            print(f"❌ Error: FFmpeg failed to process the file (Return Code: {process.returncode}).")
            print("Check the output above for FFmpeg error messages.")
            print("This type of corruption may not be fixable.")
            print("-" * 50)

    except FileNotFoundError:
        print("-" * 50)
        print("❌ CRITICAL ERROR: FFmpeg command not found.")
        print("Please ensure FFmpeg is installed and added to your system's PATH.")
        print("-" * 50)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """Main function to handle user input."""
    print("--- Video Corruption Repair Tool (FFmpeg Required) ---")
    print("This tool attempts to fix video file corruption by remuxing the container.")
    input_video_path = input("Please enter the full path to the video file (e.g., C:\\Videos\\corrupt.mp4 or /home/user/corrupt.mov): ")
    
    # Clean up the path (remove quotes if user pasted them)
    input_video_path = input_video_path.strip().replace('"', '').replace("'", "")

    if input_video_path:
        repair_video(input_video_path)
    else:
        print("No path provided. Exiting.")

if __name__ == "__main__":
    main()