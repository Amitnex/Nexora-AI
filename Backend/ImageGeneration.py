import os
import requests
from dotenv import get_key
from PIL import Image
from io import BytesIO
from time import sleep
import base64

# === Speak ===
try:
    from Backend.TextToSpeech import Speak
except:
    def Speak(text): print("[TTS]", text)

# === Save Directory ===
SAVE_DIR = "Data"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# === API Keys from .env ===
OpenAI_API = get_key(".env", "OpenAIAPIKey")
HuggingFace_API = get_key(".env", "HuggingFaceAPIKey")
Replicate_API = get_key(".env", "ReplicateAPIKey")
Stability_API = get_key(".env", "StabilityAIKey")

# === Save image from raw bytes ===
def save_image_from_bytes(image_bytes, filename):
    image = Image.open(BytesIO(image_bytes))
    path = os.path.join(SAVE_DIR, filename)
    image.save(path)
    print(f"[✔] Image saved as {path}")

# === OpenAI Image Generation ===
def openai_generate(prompt):
    print("[OpenAI] Generating image...")
    endpoint = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OpenAI_API}",
        "Content-Type": "application/json"
    }
    payload = {"prompt": prompt, "n": 1, "size": "512x512"}
    res = requests.post(endpoint, json=payload, headers=headers)
    if res.status_code == 200:
        image_url = res.json()['data'][0]['url']
        image_data = requests.get(image_url).content
        save_image_from_bytes(image_data, f"{prompt.replace(' ', '_')}_openai.jpg")
        return True
    else:
        print("OpenAI error:", res.json())
        return False

# === Hugging Face Image Generation ===
def huggingface_generate(prompt):
    print("[HuggingFace] Generating image...")
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {"Authorization": f"Bearer {HuggingFace_API}"}
    payload = {"inputs": prompt}
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200 and "image" in res.headers.get("content-type", ""):
        save_image_from_bytes(res.content, f"{prompt.replace(' ', '_')}_hf.jpg")
        return True
    else:
        print("HuggingFace error:", res.text)
        return False

# === Replicate Image Generation ===
def replicate_generate(prompt):
    print("[Replicate] Generating image...")
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {Replicate_API}",
        "Content-Type": "application/json"
    }
    payload = {
        "version": "cc201f83ebc43eb9c47aa2a632f243e9a6f46c65bdc0dcb4f1a5761e3f0d315e",
        "input": {"prompt": prompt}
    }
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=30)
        if res.status_code == 201:
            prediction_url = res.json()["urls"]["get"]
            for _ in range(10):
                prediction = requests.get(prediction_url, headers=headers, timeout=10).json()
                if prediction["status"] == "succeeded":
                    image_url = prediction["output"][0]
                    image_data = requests.get(image_url).content
                    save_image_from_bytes(image_data, f"{prompt.replace(' ', '_')}_replicate.jpg")
                    return True
                sleep(3)
            print("Replicate timeout or failure.")
        else:
            print("Replicate error:", res.text)
    except Exception as e:
        print("Replicate failed:", e)
    return False

# === Stability AI Image Generation ===
def stability_generate(prompt):
    print("[Stability AI] Generating image...")
    url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
    headers = {
        "Authorization": f"Bearer {Stability_API}",
        "Content-Type": "application/json"
    }
    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30
    }
    res = requests.post(url, json=payload, headers=headers)
    if res.status_code == 200:
        image_base64 = res.json()["artifacts"][0]["base64"]
        image_bytes = base64.b64decode(image_base64)
        save_image_from_bytes(image_bytes, f"{prompt.replace(' ', '_')}_stability.jpg")
        return True
    else:
        print("Stability AI error:", res.text)
        return False

# === Beep 5 times if all fail ===
def beep_failure_alert():
    for _ in range(5):
        print('\a', end='', flush=True)
        sleep(0.5)

# === Run all available image generation APIs ===
def generate_all_images(prompt):
    success = False
    try: success |= openai_generate(prompt)
    except Exception as e: print("OpenAI failed:", e)
    try: success |= huggingface_generate(prompt)
    except Exception as e: print("HuggingFace failed:", e)
    try: success |= replicate_generate(prompt)
    except Exception as e: print("Replicate failed:", e)
    try: success |= stability_generate(prompt)
    except Exception as e: print("Stability AI failed:", e)

    if success:
        Speak("Image created, Boss")
    else:
        print("[❌] All image generation APIs failed!")
        beep_failure_alert()

# === Main execution ===
if __name__ == "__main__":
    try:
        path = "Frontend/Files/ImageGeneration.data"
        prompt = ""

        if os.path.exists(path):
            with open(path, "r", encoding='utf-8') as file:
                content = file.read().strip()
                if content and "," in content:
                    prompt_part, flag = content.split(",", 1)
                    if flag.strip().lower() == "true":
                        prompt = prompt_part.strip()

        if not prompt:
            prompt = input("Enter prompt >>> ").strip()

        if prompt:
            print("Generating image for prompt:", prompt)
            generate_all_images(prompt)

            # ✅ Auto-reset the flag after generation
            if os.path.exists(path):
                with open(path, "w", encoding='utf-8') as file:
                    file.write(f"{prompt},false")
        else:
            print("No prompt provided. Exiting.")
    except Exception as e:
        print("Fatal error in ImageGeneration.py:", e)
