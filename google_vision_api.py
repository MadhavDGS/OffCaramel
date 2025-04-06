import os
import google.generativeai as genai
from PIL import Image
import io
import absl.logging

absl.logging.set_verbosity(absl.logging.ERROR)

# Set your API key
GOOGLE_API_KEY = "AIzaSyBOauDlaYrpmADTFDBnb3l6ybfmEUSpygw"  # Replace with your actual API key
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Initialize Google Generative AI client
genai.configure(api_key=GOOGLE_API_KEY)

# Model selection
model_name = "gemini-2.0-flash"

# Image selection (update the correct path)
image_path = "/Users/sreemadhav/PycharmProjects/PythonProject1/Screenshot 2025-03-07 at 1.02.30 AM.png"  # Update with your local image path
prompt = "Explain what is in the image."

try:
    # Load and resize image
    im = Image.open(image_path)
    im.thumbnail([640, 640], Image.Resampling.LANCZOS)

    # Convert image to bytes for API processing
    img_byte_arr = io.BytesIO()
    im.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    # Create model instance
    model = genai.GenerativeModel(model_name)

    # Run model to generate description
    response = model.generate_content(
        [prompt, {"mime_type": "image/png", "data": img_bytes}],
        generation_config=genai.types.GenerationConfig(
            temperature=0.5
        )
    )

    # Print output
    print("Description of the image:", response.text)

except Exception as e:
    print(f"Error processing the image: {str(e)}") 