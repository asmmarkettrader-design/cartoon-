# main.py
import os
import sys
import subprocess

def run_step(command, description):
    print(f"\n==================== STARTING: {description} ====================")
    # Using dynamic flushing to output Blender frames directly to GitHub Action logs
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
    
    # Step 1: Generate Story
    rc = run_step("python story_generator.py", "Gemini Story Generation")
    if rc != 0:
        print("Story generation failed. Exiting workflow.")
        sys.exit(1)
        
    # Step 2: Blender Render (Wrapped with logs enabled)
    # Using standard timeout to stop Blender if it hangs past 4.5 hours
    blender_command = "timeout 270m blender -b -P blender_render_pipeline.py -- --blender"
    rc = run_step(blender_command, "Blender Procedural Core Render Engine")
    if rc == 124:
        print("[WATCHDOG TIMEOUT] Blender hung or took too long. Forcing compilation with partial frames.")
        
    # Step 3: FFmpeg Audio/Video Compile
    run_step("python blender_render_pipeline.py", "FFmpeg AV Assembly Audio/Video Merger")
    
    print("Pipeline Complete.")

if __name__ == "__main__":
    main()
