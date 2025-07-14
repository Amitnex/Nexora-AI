from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
import subprocess
import requests
import keyboard
import asyncio
import os
from groq import Groq

# Load API key
env_vars = dotenv_values(".env")
client = Groq(api_key=env_vars.get("GroqAPIKey"))

messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'Nexora')}, a content assistant."}]

def GoogleSearch(topic):
    search(topic)
    return True

def Content(topic):
    def OpenNotepad(file):
        subprocess.Popen(['notepad.exe', file])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True
        )
        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        messages.append({"role": "assistant", "content": answer})
        return answer

    topic = topic.replace("content", "").replace("write", "").replace("in notepad", "").strip()
    content_text = ContentWriterAI(topic)

    filename = rf"Data\{topic.lower().replace(' ', '')}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content_text)
    OpenNotepad(filename)
    return True

def YouTubeSearch(topic):
    webopen(f"https://www.youtube.com/results?search_query={topic}")
    return True

def PlayYouTube(query):
    playonyt(query)
    return True

def OpenApp(app):
    try:
        appopen(app, output=True, throw_error=True)
        return True
    except:
        html = requests.get(f"https://www.google.com/search?q={app}", headers={"User-Agent": "Mozilla/5.0"}).text
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', {'jsname': 'UWckNb'})
        if links:
            webopen(links[0].get('href'))
        return True

def CloseApp(app):
    if "chrome" in app:
        return True
    try:
        close(app, output=True, throw_error=True)
        return True
    except:
        return False

def System(command):
    def mute(): keyboard.press_and_release("volume mute")
    def volume_up(): keyboard.press_and_release("volume up")
    def volume_down(): keyboard.press_and_release("volume down")

    actions = {
        "mute": mute,
        "unmute": mute,
        "volume up": volume_up,
        "volume down": volume_down
    }
    if command in actions:
        actions[command]()
        return True
    return False

async def TranslateAndExecute(commands: list[str]):
    tasks = []
    for command in commands:
        c = command.lower().strip()
        if c.startswith("open "): tasks.append(asyncio.to_thread(OpenApp, c[5:]))
        elif c.startswith("close "): tasks.append(asyncio.to_thread(CloseApp, c[6:]))
        elif c.startswith("play "): tasks.append(asyncio.to_thread(PlayYouTube, c[5:]))
        elif "write" in c and "notepad" in c: tasks.append(asyncio.to_thread(Content, c))
        elif c.startswith("content "): tasks.append(asyncio.to_thread(Content, c[8:]))
        elif c.startswith("google search "): tasks.append(asyncio.to_thread(GoogleSearch, c[14:]))
        elif c.startswith("youtube search "): tasks.append(asyncio.to_thread(YouTubeSearch, c[15:]))
        elif c.startswith("system "): tasks.append(asyncio.to_thread(System, c[7:]))
        else: print(f"[Ignored] Unknown command: {c}")

    results = await asyncio.gather(*tasks)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True

if __name__ == "__main__":
    while True:
        try:
            query = input(">>> ").strip().lower()
            if query in ["exit", "quit"]: break
            for sep in [" and ", ","]:
                query = query.replace(sep, ";")
            cmds = [cmd.strip() for cmd in query.split(";") if cmd.strip()]
            asyncio.run(Automation(cmds))
        except KeyboardInterrupt:
            break
