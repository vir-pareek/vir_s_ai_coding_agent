import os
import yaml
import google.generativeai as genai

# Load config to get API key
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

api_key = config.get("api_keys", {}).get("google")
if not api_key:
    print("No API key found in config.yaml")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
