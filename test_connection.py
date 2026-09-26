import os
from dotenv import load_dotenv
from google import genai

# Load the API key from our .env file
load_dotenv()
api_key = os.getenv("sustainability_rag")

# Create a client using our key
client = genai.Client(api_key=api_key)

# Ask the model something simple
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Say hello and confirm you're working, in one short sentence."
)

print(response.text)