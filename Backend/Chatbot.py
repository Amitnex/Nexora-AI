from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Nexora")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Setup Groq client
client = Groq(api_key=GroqAPIKey)

# System instruction
System = f"""Hello, I am {Username}. You are an advanced AI chatbot named {Assistantname} with access to real-time information.
- Only speak English.
- Answer only if asked.
- Do not mention training data or give extra notes.
"""

SystemChatBot = [{"role": "system", "content": System}]

# Load chat history
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f)

def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Real-time info:\nDay: {now.strftime('%A')}, "
        f"Date: {now.strftime('%d')} {now.strftime('%B')} {now.strftime('%Y')}, "
        f"Time: {now.strftime('%H:%M:%S')}\n"
    )

def AnswerModifier(answer):
    return '\n'.join([line for line in answer.split('\n') if line.strip()])

def ChatBot(query):
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        answer = answer.replace("</s>", "")

        messages.append({"role": "assistant", "content": answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(answer)
    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return "Sorry, something went wrong."

# Direct run
if __name__ == "__main__":
    while True:
        user_input = input("Ask: ")
        print(ChatBot(user_input))
