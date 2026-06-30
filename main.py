# main.py
import os
import sys
import subprocess

def check_file_structure():
    print("\n--- Current Working Directory Scan ---")
    current_dir = os.getcwd()
    print(f"Current Directory: {current_dir}")
    print("Files found in this directory:", os.listdir(current_dir))
    
    # Check if files exist, if not search in subdirectories
    required_files = ["story_generator.py", "blender_render_pipeline.py"]
    paths = {}
    
    for file in required_files:
        if os.path.exists(file):
            paths[file] = file
        else:
            # Search one level deep if GitHub Actions nested the folder
            found = False
            for root, dirs, files in os.walk("."):
                if file in files:
                    full_path = os.path.join(root, file)
                    paths[file] = full_path
                    found = True
                    print(f"[FOUND] {file} located at: {full_path}")
                    break
            if not found:
                print(f"[CRITICAL ERROR] {file} is completely missing from the repository!")
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
            print(output.strip(), flush=True)
            
    rc = process.poll()
    print(f"==================== FINISHED: {description} (Exit Code: {rc}) ====================\n")
    return rc

def main():
    print("Initiating Procedural Animation Workflow...")
    
    # Auto-detect file paths to prevent "No such file or directory" error
    file_paths = check_file_structure()
    
    # Step 1: Generate Story using the auto-detected path
    story_cmd = f"python {file_paths['story_generator.py']}"
    rc = run_step(story_cmd, "Gemini Story Generation")
    if rc != 0:
        print("Story generation failed. Exiting workflow.")
        sys.exit(1)
        
    # Step 2: Blender Render
    blender_command = f"timeout 270m blender -b -P {file_paths['blender_render_pipeline.py']} -- --blender"
    rc = run_step(blender_command, "Blender Procedural Core Render Engine")
    if rc == 124:
        print("[WATCHDOG TIMEOUT] Blender hung or took too long. Forcing compilation with partial frames.")
        
    # Step 3: FFmpeg Audio/Video Compile
    merge_cmd = f"python {file_paths['blender_render_pipeline.py']}"
    run_step(merge_cmd, "FFmpeg AV Assembly Audio/Video Merger")
    
    print("Pipeline Complete.")

if __name__ == "__main__":
    main()
