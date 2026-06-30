# main.py
import os
import sys
import subprocess

def check_file_structure():
    print("\n--- Smart Deep Repository Scan ---")
    paths = {}
    
    # 1. Fuzzy match for story generator
    for root, dirs, files in os.walk("."):
        for f in files:
            if "story" in f.lower() and f.endswith(".py"):
                paths["story_generator.py"] = os.path.join(root, f)
                print(f"[FOUND STORY SCRIPT] -> {paths['story_generator.py']}")
                break
                
    # 2. Fuzzy match for blender renderer
    for root, dirs, files in os.walk("."):
        for f in files:
            if "blender" in f.lower() and f.endswith(".py"):
                paths["blender_render.py"] = os.path.join(root, f)
                print(f"[FOUND BLENDER SCRIPT] -> {paths['blender_render.py']}")
                break

    if "story_generator.py" not in paths or "blender_render.py" not in paths:
        print("[CRITICAL ERROR] Required workflow scripts are missing from the repository structure.")
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
            print(output.strip(), flush=True) # Forces immediate execution prints to terminal
            
    rc = process.poll()
    print(f"==================== FINISHED: {description} (Exit Code: {rc}) ====================\n")
    return rc

def main():
    print("Initiating Procedural Animation Workflow...")
    file_paths = check_file_structure()
    
    # Step 1: Run Story Script
    story_cmd = f"python {file_paths['story_generator.py']}"
    rc = run_step(story_cmd, "Gemini Story Generation")
    if rc != 0:
        print("Story generation failed. Exiting pipeline.")
        sys.exit(1)
        
    # Step 2: Run Blender Render with Auto-Kill Safeguard at 4.5 hours
    blender_command = f"timeout 270m blender -b -P {file_paths['blender_render.py']} -- --blender"
    rc = run_step(blender_command, "Blender Procedural Core Render Engine")
    if rc == 124:
        print("[WATCHDOG TIMEOUT] Blender engine hung or runtime exceeded. Safe falling back to AV Merger.")
        
    # Step 3: Run FFmpeg Compilations via Blender Script
    merge_cmd = f"python {file_paths['blender_render.py']}"
    run_step(merge_cmd, "FFmpeg AV Assembly Audio/Video Merger")
    
    print("Pipeline Execution Finished Successfully.")

if __name__ == "__main__":
    main()
