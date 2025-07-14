import speech_recognition as sr
from mtranslate import translate
from dotenv import dotenv_values
import os

# Load language from .env
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-IN")

# Status file path
TempDirPath = os.path.join(os.getcwd(), "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

# Update assistant status
def SetAssistantStatus(status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as file:
        file.write(status)

# Fix punctuation and casing
def QueryModifier(query):
    query = query.strip()
    question_words = [
        "how", "what", "who", "where", "when", "why", "which", "whose", "whom",
        "can you", "could you", "what's", "where's", "how's"
    ]
    if any(word in query.lower() for word in question_words):
        query = query.rstrip(".?!") + "?"
    else:
        query = query.rstrip(".?!") + "."

    return query.capitalize()

# Translate to English if needed
def UniversalTranslator(text):
    return translate(text, "en", "auto").capitalize()

# Recognize speech
def SpeechRecognition():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(">>>")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        if "en" in InputLanguage.lower():
            text = recognizer.recognize_google(audio, language=InputLanguage)
        else:
            native_text = recognizer.recognize_google(audio, language=InputLanguage)
            SetAssistantStatus("Translating...")
            text = UniversalTranslator(native_text)

        return QueryModifier(text)

    except sr.UnknownValueError:
        return "Sorry, could not understand."
    except sr.RequestError as e:
        return f"API error: {e}"

# Direct run test
if __name__ == "__main__":
    while True:
        result = SpeechRecognition()
        print("You said>>>", result)
