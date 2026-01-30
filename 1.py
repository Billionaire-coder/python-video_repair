import subprocess
import os
import sys

# --- Configuration ---
# You must have FFmpeg installed and accessible in your system's PATH.

def repair_video(input_path):
    """
    Attempts a more aggressive repair by re-encoding the video.
    This is necessary when essential metadata (like the moov atom) is missing
    and a simple stream copy fails.

    Args:
        input_path (str): The full path to the potentially corrupt video file.
    """
    # 1. Check if the input file exists
    if not os.path.exists(input_path):
        print(f"Error: The file '{input_path}' was not found.")
        return

    # 2. Determine the output path
    directory = os.path.dirname(input_path)
    filename_without_ext, extension = os.path.splitext(os.path.basename(input_path))

    # Construct the new filename
    output_filename = f"{filename_without_ext}_noncorrupt{extension}"
    output_path = os.path.join(directory, output_filename)

    print("-" * 70)
    print(f"Input file: {input_path}")
    print(f"Output file will be saved as: {output_path}")
    print("Attempting repair using FFmpeg (THIS IS A SLOW RE-ENCODING PROCESS)...")
    print("-" * 70)

    # 3. Construct the FFmpeg command for RE-ENCODING (Aggressive Repair)
    # -i: Input file
    # -c:v libx264: Force video re-encoding to H.264 (robust standard)
    # -preset medium: A good balance of encoding speed and file size/quality
    # -crf 23: Constant Rate Factor 23 is generally considered a good, visually lossless quality default
    # -c:a aac: Force audio re-encoding to AAC
    # -b:a 128k: Set audio bitrate to a standard quality (128 kbps)
    # -movflags faststart: Optimizes file structure
    # -y: Overwrite output file without asking

    command = [
        'ffmpeg',
        '-i', input_path,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', 'faststart',
        '-y',
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
            print("-" * 70)
            print(f"✅ Success: Video successfully processed and saved to:\n{output_path}")
            print("Please check the new file for playback issues.")
            print("-" * 70)
        else:
            print("-" * 70)
            print(f"❌ Error: FFmpeg failed to process the file (Return Code: {process.returncode}).")
            print("Check the output above for FFmpeg error messages.")
            print("This type of corruption may not be fixable.")
            print("-" * 70)

    except FileNotFoundError:
        print("-" * 70)
        print("❌ CRITICAL ERROR: FFmpeg command not found.")
        print("Please ensure FFmpeg is installed and added to your system's PATH.")
        print("-" * 70)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """Main function to handle user input."""
    print("--- Video Corruption Repair Tool (FFmpeg Required) ---")
    print("This tool attempts to fix video file corruption by re-encoding the streams to force a new container rebuild.")
    input_video_path = input("Please enter the full path to the video file (e.g., C:\\Videos\\corrupt.mp4 or /home/user/corrupt.mov): ")
    
    # Clean up the path (remove quotes if user pasted them)
    input_video_path = input_video_path.strip().replace('"', '').replace("'", "")

    if input_video_path:
        repair_video(input_video_path)
    else:
        print("No path provided. Exiting.")

if __name__ == "__main__":
    main()