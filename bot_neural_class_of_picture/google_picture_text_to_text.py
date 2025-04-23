from transformers import Blip2Processor, Blip2ForConditionalGeneration, BitsAndBytesConfig
import torch
from PIL import Image
import requests

def picture_to_text(url):
    # Determine the device to use (GPU if available, otherwise CPU)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Create a BitsAndBytesConfig object for 8-bit quantization
    quantization_config = None  # Убираем квантование

    # Load the BLIP2 processor and model with updated quantization configuration
    processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
    model = Blip2ForConditionalGeneration.from_pretrained(
        "Salesforce/blip2-opt-2.7b", 
        quantization_config=quantization_config,
        device_map="auto",  # Automatically handle device mapping
        torch_dtype=torch.float16
    )

    # Load the image from the URL
    image = Image.open(url)

    # Preprocess the image and send it to the correct device
    inputs = processor(images=image, return_tensors="pt").to(device, torch.float16)

    # Generate text based on the image
    generated_ids = model.generate(**inputs)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

    return generated_text
