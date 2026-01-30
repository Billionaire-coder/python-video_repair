import subprocess
import os
import sys

# --- Configuration ---
# NOTE: This version requires FFmpeg installed and accessible in your system's PATH.
# It attempts to fix common corruption (like missing/misplaced metadata) 
# by rebuilding the container structure without re-encoding the video stream.

def repair_video_ffmpeg(corrupt_path):
    """
    Attempts repair using FFmpeg's stream copy feature, which often fixes files 
    where the video data is present but the file header (moov atom) is missing or corrupted.

    Args:
        corrupt_path (str): The full path to the corrupt video file.
    """
    # 1. Check if the input file exists
    if not os.path.exists(corrupt_path):
        print(f"Error: The corrupt file '{corrupt_path}' was not found.")
        return

    # 2. Determine the output path (e.g., video.mp4 -> video.fixed.mp4)
    directory = os.path.dirname(corrupt_path)
    filename, ext = os.path.splitext(os.path.basename(corrupt_path))
    
    output_filename = f"{filename}.fixed{ext}" 
    output_path = os.path.join(directory, output_filename)
    
    # Ensure the output file is not the same as the input (should be guaranteed by the suffix)
    if corrupt_path == output_path:
        print("Error: Input and output paths are identical. Cannot proceed.")
        return

    print("-" * 70)
    print(f"Corrupt Input file: {corrupt_path}")
    print(f"Output file will be saved as: {output_path}")
    print("Attempting header/container repair using FFmpeg (No reference file needed)...")
    print("-" * 70)

    # 3. Construct the FFmpeg command
    # -i: input file
    # -c copy: stream copy (no re-encoding, fast operation)
    command = [
        'ffmpeg',
        '-i', corrupt_path,
        '-c', 'copy',
        output_path
    ]

    # 4. Execute the FFmpeg command
    try:
        # Use subprocess.run for simpler execution and error checking
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False # Do not raise exception on non-zero exit code immediately
        )
        
        # Print FFmpeg output (it often writes progress/info to stderr)
        sys.stdout.write(process.stdout)
        sys.stderr.write(process.stderr)

        if process.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print("-" * 70)
            print(f"✅ Success: Video repair attempt finished and new file created.")
            print(f"Please check the repaired file at:\n{output_path}")
            print("-" * 70)
        else:
            print("-" * 70)
            print(f"❌ Error: FFmpeg failed to create a valid output file (Return Code: {process.returncode}).")
            print("The video might be too severely corrupted, or 'ffmpeg' may not be installed/in your PATH.")
            print("-" * 70)

    except FileNotFoundError:
        print("-" * 70)
        print("❌ CRITICAL ERROR: 'ffmpeg' command not found.")
        print("You must install the 'ffmpeg' utility for this tool to work.")
        print("-" * 70)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """Main function to handle user input."""
    print("--- Video Corruption Repair Tool (FFmpeg Required, No Reference File) ---")
    print("This method tries to fix video metadata/structure without a reference file.")
    
    # Using sys.argv allows passing paths directly via command line for convenience
    if len(sys.argv) > 1:
        corrupt_path = sys.argv[1].strip().replace('"', '').replace("'", "")
        print(f"Using command line input: {corrupt_path}")
    else:
        corrupt_path = input("1. Enter the full path to the CORRUPT video file: ")
        
    # Clean up the path (remove quotes if user pasted them)
    corrupt_path = corrupt_path.strip().replace('"', '').replace("'", "")

    if corrupt_path:
        repair_video_ffmpeg(corrupt_path)
    else:
        print("The path to the corrupt file is required. Exiting.")

if __name__ == "__main__":
    # Ensure the script is run in an environment where FFmpeg is available
    if sys.platform.startswith('win'):
        print("NOTE: On Windows, ensure 'ffmpeg.exe' is in your System PATH.")
    elif sys.platform.startswith('linux') or sys.platform == 'darwin':
        print("NOTE: On Linux/macOS, install via 'sudo apt install ffmpeg' or 'brew install ffmpeg'.")
        
    main()