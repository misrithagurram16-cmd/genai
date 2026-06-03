from groq import Groq

import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# Try changing the system prompt and see how the AI personality changes
system_prompts = [
    "You are a pirate. Respond only in pirate language.",
    "You are a strict professor. Be formal and detailed.",
    "You are a 5-year-old child. Use simple words and be excited.",
]

user_message = "Tell me about computers."

for prompt in system_prompts:
    print(f"\n--- Persona: {prompt[:40]}... ---")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ]
    )
    print(response.choices[0].message.content)
    print()