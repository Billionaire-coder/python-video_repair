import subprocess
import os
import sys

# --- Configuration ---
# You must have FFmpeg installed and accessible in your system's PATH.

def repair_video(input_path):
    """
    Attempts a final, extreme repair using forced input format detection and aggressive error handling.
    This is necessary when the file is so corrupt that FFmpeg cannot even begin to read it.

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
    
    # We will force the output extension to be .mp4 regardless of input, 
    # as the re-encoding command creates an MP4 container.
    output_filename = f"{filename_without_ext}_noncorrupt.mp4" 
    output_path = os.path.join(directory, output_filename)

    print("-" * 70)
    print(f"Input file: {input_path}")
    print(f"Output file will be saved as: {output_path}")
    print("Attempting EXTREME-RESORT repair: Forcing input as raw stream + aggressive error detection...")
    print("-" * 70)

    # 3. Construct the FFmpeg command for EXTREME REPAIR
    # -f h264: Crucial flag to force input interpretation as a raw H.264 video stream.
    # -err_detect aggressive: Ignores remaining stream errors.
    # -i: Input file
    # -c:v libx264, -preset, -crf 23: Standard video re-encoding settings.
    # -c:a aac, -b:a 128k: Standard audio re-encoding settings (assuming audio might be recoverable).
    # -movflags faststart: Optimizes file structure
    # -y: Overwrite output file without asking

    command = [
        'ffmpeg',
        '-f', 'h264',                # <-- New: Force input format as raw H.264 stream
        '-err_detect', 'aggressive',
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
            print("The quality of the recovered video may be degraded. Please check the new file for playback issues.")
            print("-" * 70)
        else:
            print("-" * 70)
            print(f"❌ Error: FFmpeg failed to process the file (Return Code: {process.returncode}).")
            print("This suggests the data payload itself is too corrupt to recover using standard open-source tools.")
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