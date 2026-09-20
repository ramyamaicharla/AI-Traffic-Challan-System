import os
import base64

from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()

# Get Groq API key from .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Check API key
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set. Please add it to your .env file.")

# Create Groq client
client = Groq(api_key=GROQ_API_KEY)

# 1. Read and encode the image
image_path = r"D:\PROJECTS\traffic_challan\traffic_challan\Traffic_Chalan\images\triple riding.jpg"

with open(image_path, "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

# 2. Call Groq Vision model
response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Detect the car number plate and give one word answer. Do not give any new information. Only give the car plate number."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        }
    ]
)

# 3. Print result
print(response.choices[0].message.content)