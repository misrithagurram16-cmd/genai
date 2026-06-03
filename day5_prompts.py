from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask(system, user, temperature=0.7):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    )
    return response.choices[0].message.content

print("=" * 60)
print("TECHNIQUE 1: Zero-shot vs Few-shot")
print("=" * 60)

# Zero-shot - no examples given
zero_shot = ask(
    "Classify the sentiment of the text as Positive, Negative or Neutral. Reply with one word only.",
    "The product broke after one day and support never responded."
)
print(f"Zero-shot: {zero_shot}")

# Few-shot - give examples first
few_shot = ask(
    """Classify sentiment as Positive, Negative or Neutral. Reply with one word only.

Examples:
Text: "I love this product!" → Positive
Text: "Worst experience ever." → Negative  
Text: "It arrived on time." → Neutral""",
    "The product broke after one day and support never responded."
)
print(f"Few-shot: {few_shot}")

print("\n" + "=" * 60)
print("TECHNIQUE 2: Chain of Thought")
print("=" * 60)

# Without chain of thought
without_cot = ask(
    "Answer math questions directly.",
    "If a store has 50 apples, sells 30%, then receives 20 more, how many apples are there?",
    temperature=0
)
print(f"Without CoT: {without_cot}")

# With chain of thought
with_cot = ask(
    "Answer math questions by thinking step by step. Show your reasoning.",
    "If a store has 50 apples, sells 30%, then receives 20 more, how many apples are there?",
    temperature=0
)
print(f"With CoT: {with_cot}")

print("\n" + "=" * 60)
print("TECHNIQUE 3: Role + Constraint Prompting")
print("=" * 60)

constrained = ask(
    """You are a senior software engineer reviewing code.
Rules:
- Be concise, max 3 bullet points
- Focus only on critical issues
- Always suggest one improvement""",
    "Review this: for i in range(len(mylist)): print(mylist[i])"
)
print(f"Constrained review:\n{constrained}")

print("\n" + "=" * 60)
print("TECHNIQUE 4: Output Formatting")
print("=" * 60)

formatted = ask(
    """You are a tech job analyzer. Always respond in this exact format:
ROLE: [job title]
SKILLS: [comma separated skills]
SALARY: [range]
DIFFICULTY: [Easy/Medium/Hard to get]
TIP: [one sentence advice]""",
    "Analyze: Junior AI Engineer position at a startup"
)
print(formatted)