# main.py
import os
import sys
import subprocess

def check_file_structure():
    print("\n--- Smart Deep Repository Scan ---")
    current_dir = os.getcwd()
    print(f"Current Directory: {current_dir}")
    
    paths = {}
    
    # 1. Look for Story Generator
    for root, dirs, files in os.walk("."):
        for f in files:
            if "story" in f.lower() and f.endswith(".py"):
                paths["story_generator.py"] = os.path.join(root, f)
                print(f"[FOUND STORY SCRIPT] -> {paths['story_generator.py']}")
                break
                
    # 2. Look for Blender script with fuzzy matching (chahay naam kuch bhi ho, agar 'blender' shamil hai)
    for root, dirs, files in os.walk("."):
        for f in files:
            if "blender" in f.lower() and (f.endswith(".py") or "." not in f):
                paths["blender_render.py"] = os.path.join(root, f)
                print(f"[FOUND BLENDER SCRIPT] -> {paths['blender_render.py']}")
                break

    # Critical Checks
    if "story_generator.py" not in paths:
        print("[CRITICAL ERROR] Story generator script (containing 'story') missing!")
        sys.exit(2)
    if "blender_render.py" not in paths:
        print("\n[CRITICAL ERROR] Blender script missing!")
        print(f"Files actually present in your directory structure are:")
        for root, dirs, files in os.walk("."):
            if "git" not in root:
                print(f" Folder {root}: {files}")
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
    
    file_paths = check_file_structure()
    
    # Step 1: Generate Story
    story_cmd = f"python {file_paths['story_generator.py']}"
    rc = run_step(story_cmd, "Gemini Story Generation")
    if rc != 0:
        print("Story generation failed. Exiting workflow.")
        sys.exit(1)
        
    # Step 2: Blender Render
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
