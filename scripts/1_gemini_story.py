# scripts/1_gemini_story.py
import os
import json
import sys

# Handling both legacy and new google-genai imports to prevent crashes
try:
    from google import genai
    USE_NEW_SDK = True
except ImportError:
    import google.generativeai as genai
    USE_NEW_SDK = False

from characters_config import SYSTEM_PROMPT_BASE

def generate_new_episode():
    print("Generating a brand new cartoon story from Gemini...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[CRITICAL ERROR] GEMINI_API_KEY environment variable is missing!")
        sys.exit(1)

    prompt = SYSTEM_PROMPT_BASE + "\nGenerate a unique episode now. Make sure the threat is totally unexpected."
    
    # AUTO-FALLBACK SYSTEM:
    # Yeh list sabse naye aur stable models ki hai. Script baari baari sab ko try karegi.
    # Jo model aapki API key par available hoga, yeh usay pick kar legi aur error nahi degi.
    fallback_models = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-1.5-flash-002',
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro'
    ]

    story_text = None
    
    if USE_NEW_SDK:
        client = genai.Client(api_key=api_key)
        for model_name in fallback_models:
            try:
                print(f"[TRYING MODEL] -> {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={'response_mime_type': 'application/json'}
                )
                story_text = response.text
                print(f"[SUCCESS] Story generated using {model_name}!")
                break # Agar chal gaya to loop rok do
            except Exception as e:
                print(f"[FAILED] {model_name} did not work. Moving to next...")
    else:
        genai.configure(api_key=api_key)
        for model_name in fallback_models:
            try:
                print(f"[TRYING MODEL] -> {model_name}...")
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config={"response_mime_type": "application/json"}
                )
                response = model.generate_content(prompt)
                story_text = response.text
                print(f"[SUCCESS] Story generated using {model_name}!")
                break
            except Exception as e:
                print(f"[FAILED] {model_name} did not work. Moving to next...")
                
    if not story_text:
        print("\n[CRITICAL ERROR] All Gemini models failed! Please check your API key permissions in Google AI Studio.")
        sys.exit(1)
    
    story_data = json.loads(story_text)
    
    os.makedirs("output", exist_ok=True)
    with open("output/story.json", "w") as f:
        json.dump(story_data, f, indent=4)
        
    print(f"Story saved successfully: {story_data.get('title')}")

if __name__ == "__main__":
    generate_new_episode()
