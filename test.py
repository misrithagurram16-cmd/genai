from groq import Groq

client = Groq(api_key="REMOVED")

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello and tell me what you can do."}
    ]
)

print(response.choices[0].message.content)

