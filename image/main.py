from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI()


response = client.responses.create(
    model = "gpt-4.1-mini",
    input = [
        {
            "role": "user",
            "content": [
                { "type": "input_text", "text": "Generate a caption for this image in about 50 words"},
                { "type": "input_image", "image_url": "https://images.pexels.com/photos/879109/pexels-photo-879109.jpeg"}
            ]
        }
    ]
)

print("Response:", response.output_text)

print('*' * 15)

print(response.output[0].content[0].text)