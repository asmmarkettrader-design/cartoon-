import os
import json
import time
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

def generate_story():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY secret is missing in GitHub Secrets!")

    client = genai.Client(api_key=api_key)
    
    prompt = """
    You are an expert 3D Animation Scriptwriter for US/UK kids audience.
    Generate a 10-minute cartoon script in ENGLISH. Output MUST be in raw JSON format ONLY. Do not wrap in markdown or backticks.
    
    CRITICAL CHARACTER CONSISTENCY:
    - Main Character: Leo (10-year-old tech genius, wears a glowing wrist-gadget).
    - Leo's Family: His Mom, Dad, and older Sister (Lily - always tries to stop Leo from doing crazy experiments).
    - Leo's Best Friends: Max (Athletic, brave) and Maya (Creative artist).
    - Location: 'Neo-City' (A futuristic high-tech city with flying cars and neon buildings).
    
    STORY GENERATION RULE:
    Every time you are called, create a completely NEW threat or adventure. Leo must invent a tool to solve it.
    The threat can be: Rogue AI/Robots, Aliens invading Neo-City, or Ancient Magical Curses accidentally activated.
    
    Expected JSON format:
    {
      "title": "Episode Title Here",
      "description": "YouTube Description text with hashtags",
      "tags": ["cartoon", "leo", "robots", "animation"],
      "scenes": [
        {
          "scene_id": 1,
          "environment": "city",
          "dialogues": [
            {"character": "Leo", "text": "Look at this new gadget I made!"},
            {"character": "Lily", "text": "Leo, stop! You will break something!"}
          ]
        }
      ]
    }
    """

    models_to_try = []

    # STEP 1: DYNAMIC DISCOVERY (Google se live models uthana)
    try:
        print("Fetching live available models from Google Gemini API...")
        live_models = client.models.list()
        for model in live_models:
            m_name = model.name.lower()
            # Sirf text generation wale Gemini (Flash/Pro) models filter karna
            if "gemini" in m_name and ("flash" in m_name or "pro" in m_name):
                clean_name = model.name.replace("models/", "")
                if clean_name not in models_to_try:
                    models_to_try.append(clean_name)
                    
        # Naye models (3.5, 3.0, 2.5, 2.0) ko list mein sabse pehle rakhna
        models_to_try.sort(key=lambda x: any(v in x for v in ["3.5", "3.0", "2.5", "2.0"]), reverse=True)
        print(f"Successfully discovered {len(models_to_try)} live Gemini models.")
    except Exception as e:
        print(f"Dynamic model listing skipped or unavailable ({e}). Using smart prediction list...")

    # STEP 2: FUTURE-PROOF FALLBACK LIST (Agar live list fail ho jaye ya empty ho)
    future_predicted_models = [
        'gemini-2.0-flash',
        'gemini-2.5-flash',
        'gemini-3.0-flash',
        'gemini-3.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-1.5-flash',
        'gemini-1.5-flash-8b',
        'gemini-2.0-pro',
        'gemini-1.5-pro-latest'
    ]

    # Dono lists ko merge karna bina duplicates ke
    for model in future_predicted_models:
        if model not in models_to_try:
            models_to_try.append(model)

    print(f"Final prioritized pipeline execution order: {models_to_try}")

    # STEP 3: EXECUTION LOOP (Ek ek karke models par try karna)
    response = None
    for model_name in models_to_try:
        print(f"Attempting story generation with model: {model_name}...")
        
        # Har model ko 2 baar chance dena agar temporary demand issue (503) ho
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )
                break # Success! Inner loop se bahar niklein
                
            except ClientError as e:
                # 404 yani model is version/region mein block ya invalid hai, skip to next model
                if "404" in str(e) or "not found" in str(e).lower():
                    print(f"Model '{model_name}' returned 404 (Not Found/Supported). Skipping...")
                    break 
                else:
                    raise e
                    
            except ServerError as e:
                # 503 yani server busy hai, thoda ruk kar dobara try karein
                if "503" in str(e) or "high demand" in str(e).lower():
                    print(f"Model '{model_name}' is busy (503). Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    raise e
        
        if response:
            print(f"🎉 Successfully generated story using: {model_name}!")
            break

    if not response:
        raise RuntimeError("Critical Error: All discovered and predicted Gemini models are currently unavailable.")

    # STEP 4: DATA CLEANING & SAVING
    script_text = response.text.strip()
    os.makedirs("video", exist_ok=True)
    
    if script_text.startswith("```json"):
        script_text = script_text.split("```json")[1].split("```")[0].strip()
    elif script_text.startswith("```"):
        script_text = script_text.split("```")[1].split("```")[0].strip()

    try:
        json_data = json.loads(script_text)
        with open("video/current_script.json", "w") as f:
            json.dump(json_data, f, indent=4)
        print("Story file updated successfully at video/current_script.json")
    except json.JSONDecodeError:
        print("Error: Invalid JSON syntax returned by the model. Raw response:")
        print(script_text)
        raise

if __name__ == "__main__":
    generate_story()
