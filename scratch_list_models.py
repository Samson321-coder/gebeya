import os
import google.generativeai as genai
from dotenv import load_dotenv

# Hardcode the path to .env in the project root
load_dotenv(os.path.join(os.getcwd(), ".env"))
api_key = os.getenv("GEMINI_API_KEY")

with open("models_debug.txt", "w") as f:
    if not api_key:
        f.write("Error: GEMINI_API_KEY not found in .env\n")
        f.write(f"CWD: {os.getcwd()}\n")
    else:
        try:
            genai.configure(api_key=api_key)
            f.write(f"Testing key starting with: {api_key[:10]}...\n")
            models = genai.list_models()
            f.write("Available models:\n")
            for m in models:
                f.write(f"- {m.name}\n")
        except Exception as e:
            f.write(f"Error listing models: {type(e).__name__}: {e}\n")
            if hasattr(e, 'message'):
                f.write(f"Message: {e.message}\n")
            if hasattr(e, 'code'):
                f.write(f"Code: {e.code}\n")
