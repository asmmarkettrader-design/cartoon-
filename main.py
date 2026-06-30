# main.py
import os
import sys
import subprocess

def check_file_structure():
    print("\n--- Deep Repository Scan ---")
    current_dir = os.getcwd()
    print(f"Current Directory: {current_dir}")
    
    # Updated the expected name to match your actual file: blender_render.py
    required_files = ["story_generator.py", "blender_render.py"]
    paths = {}
    
    for file in required_files:
        found = False
        # Searches through all folders (like scripts/)
        for root, dirs, files in os.walk("."):
            if file in files:
                full_path = os.path.join(root, file)
                paths[file] = full_path
                found = True
                print(f"[FOUND] {file} located at: {full_path}")
                break
        if not found:
            print(f"[CRITICAL ERROR] {file} is completely missing from the repository structure!")
            print("Please check your 'scripts' folder and verify the filename.")
            sys.exit(2)
    return paths

def run_step(command, description):
    print(f"\n==================== STARTING: {description} ====================")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip(), flush=True) # Real-time logs printing
            
    rc = process.poll()
    print(f"==================== FINISHED: {description} (Exit Code: {rc}) ====================\n")
    return rc

def main():
    print("Initiating Procedural Animation Workflow...")
    
    # Auto-detect the exact paths
    file_paths = check_file_structure()
    
    # Step 1: Generate Story
    story_cmd = f"python {file_paths['story_generator.py']}"
    rc = run_step(story_cmd, "Gemini Story Generation")
    if rc != 0:
        print("Story generation failed. Exiting workflow.")
        sys.exit(1)
        
    # Step 2: Blender Render (Using blender_render.py)
    blender_command = f"timeout 270m blender -b -P {file_paths['blender_render.py']} -- --blender"
    rc = run_step(blender_command, "Blender Procedural Core Render Engine")
    if rc == 124:
        print("[WATCHDOG TIMEOUT] Blender hung or took too long. Forcing compilation with partial frames.")
        
    # Step 3: FFmpeg Audio/Video Compile
    merge_cmd = f"python {file_paths['blender_render.py']}"
    run_step(merge_cmd, "FFmpeg AV Assembly Audio/Video Merger")
    
    print("Pipeline Complete.")

if __name__ == "__main__":
    main()
