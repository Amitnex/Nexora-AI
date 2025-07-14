import os
import requests
from dotenv import get_key
from PIL import Image
from io import BytesIO
from time import sleep

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
    else:
        print("OpenAI error:", res.json())

# === Hugging Face Image Generation ===
def huggingface_generate(prompt):
    print("[HuggingFace] Generating image...")
    url = "https://api-inference.huggingface.co/models/stabilityai/sdxl-turbo"
    headers = {"Authorization": f"Bearer {HuggingFace_API}"}
    payload = {"inputs": prompt}
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200 and "image" in res.headers.get("content-type", ""):
        save_image_from_bytes(res.content, f"{prompt.replace(' ', '_')}_hf.jpg")
    else:
        print("HuggingFace error:", res.text)

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
    res = requests.post(url, json=payload, headers=headers)
    if res.status_code == 201:
        prediction_url = res.json()["urls"]["get"]
        for _ in range(10):
            prediction = requests.get(prediction_url, headers=headers).json()
            if prediction["status"] == "succeeded":
                image_url = prediction["output"][0]
                image_data = requests.get(image_url).content
                save_image_from_bytes(image_data, f"{prompt.replace(' ', '_')}_replicate.jpg")
                return
            sleep(3)
        print("Replicate timeout or failure.")
    else:
        print("Replicate error:", res.text)

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
        image_data = BytesIO(bytes(res.json()["artifacts"][0]["base64"], 'utf-8'))
        save_image_from_bytes(image_data, f"{prompt.replace(' ', '_')}_stability.jpg")
    else:
        print("Stability AI error:", res.text)

# === Run all available image generation APIs ===
def generate_all_images(prompt):
    try: openai_generate(prompt)
    except Exception as e: print("OpenAI failed:", e)
    try: huggingface_generate(prompt)
    except Exception as e: print("HuggingFace failed:", e)
    try: replicate_generate(prompt)
    except Exception as e: print("Replicate failed:", e)
    try: stability_generate(prompt)
    except Exception as e: print("Stability AI failed:", e)

# === Main execution when run by subprocess (from main.py) ===
if __name__ == "__main__":
    try:
        path = "Frontend/Files/ImageGeneration.data"
        if os.path.exists(path):
            with open(path, "r", encoding='utf-8') as file:
                content = file.read().strip()
                if content and "," in content:
                    prompt, flag = content.split(",", 1)
                    if flag.strip().lower() == "true":
                        print("Generating image for prompt:", prompt.strip())
                        generate_all_images(prompt.strip())
                    else:
                        print("Flag is not true. Skipping generation.")
                else:
                    print("Invalid content in ImageGeneration.data.")
        else:
            print("ImageGeneration.data file not found.")
    except Exception as e:
        print("Fatal error in ImageGeneration.py:", e)
