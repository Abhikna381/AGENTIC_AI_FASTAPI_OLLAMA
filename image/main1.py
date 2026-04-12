import base64
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI()


# import os

#BASE_DIR = os.path.dirname(__file__)

#image_path = os.path.join(BASE_DIR, "hanuman-chromebook-wallpaper.jpg")"""

#with open(r"C:\Users\abhij\PROJECT\FASTAPI\image\hanuman-chromebook-wallpaper.jpg", "rb") as f:
#    img_base64 = base64.b64encode(f.read()).decode("utf-8")

#response = client.responses.create(
#    model="gpt-4.1-mini",
#    input=[
#        {
#           "role": "user",
#            "content": [
#                {"type": "input_text", "text": "What is in this image?"},
#                {
#                    "type": "input_image",
#                    "image_base64": {img_base64}
#                }
#            ],
#       }
#    ],
#)

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your image
image_path = r"C:\Users\abhij\PROJECT\FASTAPI\image\hanuman-chromebook-wallpaper.jpg"

# Getting the Base64 string
base64_image = encode_image(image_path)


response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "user",
            "content": [
                { "type": "input_text", "text": "what's in this image?" },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        }
    ],
)
print(response.output[0].content[0].text)
print(response.output_text)