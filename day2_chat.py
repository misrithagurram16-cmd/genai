from groq import Groq

import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("🤖 AI Chat — type 'quit' to exit\n")

# This stores the full conversation history
messages = [
    {"role": "system", "content": "You are a helpful AI career coach for someone learning GenAI development."}
]

while True:
    user_input = input("You: ")
    
    if user_input.lower() == "quit":
        print("Goodbye!")
        break
    
    # Add user message to history
    messages.append({"role": "user", "content": user_input})
    
    # Get AI response
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    
    ai_reply = response.choices[0].message.content
    
    # Add AI reply to history so it remembers context
    messages.append({"role": "assistant", "content": ai_reply})
    
    print(f"\nAI: {ai_reply}\n")