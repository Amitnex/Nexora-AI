import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load voice settings from .env
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-JennyNeural")

# Async function to generate audio file
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"
    if os.path.exists(file_path):
        os.remove(file_path)

    communicate = edge_tts.Communicate(
        text=text,
        voice=AssistantVoice,
        rate="+13%",
        pitch="+5Hz"
    )
    await communicate.save(file_path)

# Function to play audio
def TTS(text, on_done=lambda r=None: True):
    while True:
        try:
            asyncio.run(TextToAudioFile(text))
            pygame.mixer.init()
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if on_done() is False:
                    break
                pygame.time.Clock().tick(10)
            return True

        except Exception as e:
            print(f"❌ Error in TTS: {e}")

        finally:
            try:
                if callable(on_done):
                    on_done(False)
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
            except Exception as e:
                print(f"Error in cleanup: {e}")

# Function to decide if speech should be split
def TextToSpeech(text, on_done=lambda r=None: True):
    sentences = str(text).split(".")
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir."
    ]

    if len(sentences) > 4 and len(text) > 250:
        intro_part = ". ".join(sentences[:2]).strip()
        extra_line = random.choice(responses)
        TTS(f"{intro_part}. {extra_line}", on_done)
    else:
        TTS(text, on_done)

# Standalone test
if __name__ == "__main__":
    while True:
        user_input = input("Enter the text: ").strip()
        if user_input:
            TextToSpeech(user_input)
