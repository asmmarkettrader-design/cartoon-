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

from scripts.characters_config import SYSTEM_PROMPT_BASE

def generate_new_episode():
    print("Generating a brand new cartoon story from Gemini...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[CRITICAL ERROR] GEMINI_API_KEY environment variable is missing!")
        sys.exit(1)

    prompt = SYSTEM_PROMPT_BASE + "\nGenerate a unique episode now. Make sure the threat is totally unexpected."

    if USE_NEW_SDK:
        # Code logic for new google-genai SDK
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        story_text = response.text
    else:
        # Fallback for google-generativeai legacy library
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(prompt)
        story_text = response.text
    
    story_data = json.loads(story_text)
    
    os.makedirs("output", exist_ok=True)
    with open("output/story.json", "w") as f:
        json.dump(story_data, f, indent=4)
        
    print(f"Story generated successfully: {story_data.get('title')}")

if __name__ == "__main__":
    generate_new_episode()
