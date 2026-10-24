from google import genai
from config.setting import settings

client = genai.Client(
    api_key = settings.GEMINI_API_KEY
)