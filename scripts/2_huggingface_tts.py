import os
import json
import requests
import time

def generate_voiceovers():
    # .strip() lagaya hai taaki whitespace ya new-line ka error hamesha ke liye khatam ho jaye
    hf_token = os.getenv("HF_API_TOKEN", "").strip()
    
    with open("video/current_script.json", "r") as f:
        script = json.load(f)

    os.makedirs("video/audio", exist_ok=True)
    
    # Hugging Face TTS Free Inference API Setup
    API_URL = "https://api-inference.huggingface.co/models/microsoft/speecht5_tts"
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}

    dialogue_counter = 0
    
    # Agar token missing ho ya galat ho, toh automatic gTTS standard system chalega
    use_fallback = False
    if not hf_token:
        print("HF_API_TOKEN is missing or empty. Using gTTS alternative...")
        use_fallback = True

    for scene in script["scenes"]:
        for dialogue in scene["dialogues"]:
            character = dialogue["character"]
            text = dialogue["text"]
            audio_path = f"video/audio/dialogue_{dialogue_counter}.wav"
            
            if not use_fallback:
                payload = {"inputs": text}
                try:
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
                    
                    # Agar model load ho raha ho (503), toh wait karein
                    if response.status_code == 503:
                        print(f"Hugging Face model is loading... waiting 10 seconds.")
                        time.sleep(10)
                        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)

                    if response.status_code == 200 and len(response.content) > 100:
                        with open(audio_path, "wb") as f_audio:
                            f_audio.write(response.content)
                        print(f"Generated HF audio for {character}")
                        dialogue_counter += 1
                        continue
                    else:
                        print(f"HF failed or returned empty for {character} (Status: {response.status_code}). Falling back to gTTS...")
                        use_fallback = True
                except Exception as e:
                    print(f"HF Connection error: {e}. Switching to gTTS backup system...")
                    use_fallback = True
            
            # === FALLBACK BACKUP TTS SYSTEM (gTTS) ===
            if use_fallback:
                try:
                    from gtts import gTTS
                except ImportError:
                    # Agar gtts library installed nahi hai runtime par, toh manually pip block trigger karenge
                    import subprocess
                    import sys
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "gTTS"])
                    from gtts import gTTS
                
                # English language with US/UK clear style support
                tts = gTTS(text=text, lang='en', tld='com')
                tts.save(audio_path)
                print(f"Generated Backup gTTS audio for {character}")
                dialogue_counter += 1

    print(f"\n=== Successfully generated {dialogue_counter} voiceover tracks. ===")

if __name__ == "__main__":
    generate_voiceovers()
