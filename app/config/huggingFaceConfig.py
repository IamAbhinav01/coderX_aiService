from huggingface_hub import InferenceClient
from config import Settings

settings = Settings()

api_key = settings.HF_TOKEN

client = InferenceClient(
    provider="fal-ai",
    api_key=api_key,
)

image = client.text_to_image(
    "Astronaut riding a horse",
    model="ideogram-ai/ideogram-4-fp8",
)

image.save("astronaut_horse.png")

print("Image saved successfully!")