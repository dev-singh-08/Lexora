from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_answer(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    return response.text.strip()