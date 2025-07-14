import cohere
from rich import print
from dotenv import dotenv_values

# Load API key
env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")
co = cohere.Client(api_key=CohereAPIKey)

# Known function tags
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

# AI instructions
preamble = """
You are a highly accurate Decision-Making Model.
You will decide what kind of command the user gives.
Do NOT answer queries—just classify them.

→ Use format:
    - 'general (query)' for LLM questions.
    - 'open app', 'play song', 'google search topic', etc. for automation.
    - Combine them if needed: 'open chrome, general who is kalidas'.

Examples:
- who is Ram? → general who is Ram?
- open chrome and play hanuman chalisa → open chrome, play hanuman chalisa
"""

# Training history
ChatHistory = [
    {"role": "USER", "message": "how are you?"},
    {"role": "CHATBOT", "message": "general how are you?"},
    {"role": "USER", "message": "open chrome and search gandhi"},
    {"role": "CHATBOT", "message": "open chrome, google search gandhi"},
    {"role": "USER", "message": "set reminder for 5th Aug at 7pm"},
    {"role": "CHATBOT", "message": "reminder 7pm 5th Aug"},
]

# Classifier function
def FirstLayerDMM(prompt: str = "test") -> list:
    messages = ChatHistory + [{"role": "USER", "message": prompt}]

    try:
        stream = co.chat_stream(
            model='command-r-plus',
            message=prompt,
            temperature=0.3,
            chat_history=messages,
            prompt_truncation='OFF',
            connectors=[],
            preamble=preamble
        )
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        return []

    response = ""
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text

    # Cleanup
    response = response.replace("\n", "").split(",")
    response = [r.strip() for r in response]

    # Filter allowed commands
    final_response = []
    for task in response:
        for func in funcs:
            if task.startswith(func):
                final_response.append(task)
                break

    return final_response

# Run it directly
if __name__ == "__main__":
    print(" Please type your query below")
    while True:
        user_input = input(">>> ")
        print("Classifying...")
        result = FirstLayerDMM(prompt=user_input)
        print("[green]Detected Tasks:[/green]", result)
