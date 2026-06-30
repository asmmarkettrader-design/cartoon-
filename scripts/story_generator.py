# story_generator.py
import os
import json
import google.generativeai as genai
from characters_config import SYSTEM_PROMPT_BASE

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_new_episode():
    print("Generating a brand new cartoon story from Gemini...")
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"}
    )
    prompt = SYSTEM_PROMPT_BASE + "\nGenerate a unique episode now. Make sure the threat is totally unexpected."
    response = model.generate_content(prompt)
    story_data = json.loads(response.text)
    
    os.makedirs("output", exist_ok=True)
    with open("output/story.json", "w") as f:
        json.dump(story_data, f, indent=4)
    print(f"Story generated successfully: {story_data.get('title')}")

if __name__ == "__main__":
    generate_new_episode()
