from groq import Groq

import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Temperature: 0 = very predictable, 1 = very creative
temperatures = [0.0, 0.5, 1.0]

for temp in temperatures:
    print(f"\n--- Temperature: {temp} ---")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=temp,
        messages=[
            {"role": "system", "content": "You are a creative writer."},
            {"role": "user", "content": "Write one sentence about the ocean."}
        ]
    )
    print(response.choices[0].message.content)