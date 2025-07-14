from googlesearch import search
from groq import Groq 
from json import load, dump
import datetime 
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Nexora")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Groq client setup
client = Groq(api_key=GroqAPIKey)

# System prompt
System = f"""Hello, I am {Username}. You are a professional assistant named {Assistantname} with access to real-time internet data.
Answer questions clearly and grammatically using the search result. Don’t add unrelated or unnecessary info.
"""

# Chat log history
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    messages = []
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# Google search wrapper
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"Search results for '{query}':\n[start]\n"
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    Answer += "[end]"
    return Answer

# Clean answer
def AnswerModifier(answer):
    return '\n'.join([line for line in answer.split('\n') if line.strip()])

# System context
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"},
]

# Realtime clock
def Information():
    now = datetime.datetime.now()
    return (
        f"Use this real-time info:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d %B %Y')}\n"
        f"Time: {now.strftime('%H:%M:%S')}\n"
    )

# Main search engine logic
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)

    messages.append({"role": "user", "content": prompt})
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        stream=True
    )

    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    SystemChatBot.pop()
    return AnswerModifier(Answer)

# Direct test
if __name__ == "__main__":
    while True:
        prompt = input("Enter query: ")
        print(RealtimeSearchEngine(prompt))
