# scripts/3_blender_render.py
import os
import sys
import subprocess

def optimize_blender_settings():
    """Optimizes Blender so it renders frames fast and stays within GitHub Actions CPU limits."""
    try:
        import bpy
        scene = bpy.context.scene
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
        
        # Performance Tweaks for GitHub Actions
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.resolution_percentage = 70 # High-quality downscaled for speed
        
        scene.eevee.taa_render_samples = 32
        print("[BLENDER LOG] Engine and render parameters successfully optimized.")
    except ImportError:
        print("[ERROR] Not running inside Blender environment.")

def merge_audio_video():
    """Compiles individual frames and audio files into a single finalized high-quality MP4 file."""
    os.makedirs("output/video_folder", exist_ok=True)
    print("[FFMPEG LOG] Starting Audio and Video multiplexing...")
    
    # Ensuring output files are fully integrated and merged seamlessly
    ffmpeg_cmd = (
        "ffmpeg -y -framerate 24 -i output/frames/%04d.png "
        "-i output/temp_full_audio.wav -c:v libx264 -pix_fmt yuv420p "
        "-c:a aac -b:a 192k output/video_folder/final_cartoon_episode.mp4"
    )
    
    result = subprocess.run(ffmpeg_cmd, shell=True)
    if result.returncode == 0:
        print("[SUCCESS] final_cartoon_episode.mp4 generated inside 'output/video_folder/'.")
    else:
        print("[ERROR] FFmpeg multiplexing failed.")

if __name__ == "__main__":
    # Checks if execution is internal to Blender or standard Python shell
    if "bpy" in sys.modules or (len(sys.argv) > 1 and sys.argv[1] == "--blender"):
        optimize_blender_settings()
    else:
        merge_audio_video()
