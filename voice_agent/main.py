import asyncio

from dotenv import load_dotenv
import speech_recognition as sr
from openai.helpers import LocalAudioPlayer
from openai import AsyncOpenAI
from openai import OpenAI


load_dotenv() # Load environment variables from a .env file


client = OpenAI()

async_client = AsyncOpenAI() # Create an asynchronous OpenAI client

async def tts(speech: str):

    # Stop previous audio
    # try:
    #     pygame.mixer.music.stop()
    #     pygame.mixer.quit()
    # except:
    #     pass

    # Remove old file if exists
    # if os.path.exists("output.wav"):
    #     os.remove("output.wav")


    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts", # Specify the model to use for text-to-speech conversion
        input=speech, # Provide the text input to be converted to speech
        voice="alloy", # Specify the voice to be used for the generated speech
        instructions="Always speak in a friendly tone.", # Provide instructions for the voice agent to follow when generating speech
        response_format="wav" # Specify the audio format for the output
    ) as response:# Create a speech audio using the OpenAI API with the provided text input
        await LocalAudioPlayer().play(response)
        

#    # Read audio bytes
#     audio_data = await response.aread()

#     # Save audio file
#     with open("output.wav", "wb") as f:
#         f.write(audio_data)

#     # Initialize player
#     pygame.mixer.init()

#     # Load audio
#     pygame.mixer.music.load("output.wav")

#     # Play audio
#     pygame.mixer.music.play()

#     # Wait until audio finishes
#     while pygame.mixer.music.get_busy():
#         await asyncio.sleep(1)

#     # Cleanup
#     pygame.mixer.quit()



def main():
    r = sr.Recognizer() # Create a Recognizer object

    with sr.Microphone() as source: # Use the default microphone as the audio source
        r.adjust_for_ambient_noise(source) # Adjust for ambient noise
        r.pause_threshold = 2 # Set the pause threshold for speech recognition

        SYSTEM_PROMPT = f"""
            You are an expert voice agent. You are given the transcript of what 
            user has said using voice.
            You need to output as if you are an voice agent and whatever you speak
            will be converted to voice using AI and played to user.
        """


        messages = [{"role": "system", "content": SYSTEM_PROMPT}] # Define the system message to set the behavior of the assistant] # Initialize an empty list to store messages for the chat completion


        while True: # Start an infinite loop to continuously listen for audio input

            print("Speak Something....")
            audio = r.listen(source) # Listen for audio input

            print("Processing.... Please wait... (STT)")
            stt = r.recognize_google(audio) # Use Google's speech recognition to convert audio to text


            print(f"You said: {stt}") # Print the recognized text

            messages.append({"role": "user", "content": stt}) # Append the user message with the recognized text to the messages list

            

            response = client.chat.completions.create(
                model="gpt-4.1-mini", # Specify the model to use for the chat completion
                messages=messages
            ) # Create a chat completion using the OpenAI API with the recognized text as input

            print(f"AI Agent: {response.choices[0].message.content}") # Print the response from the voice agent
            
            asyncio.run(tts(speech = response.choices[0].message.content)) # Call the text-to-speech function to convert the response to speech and play it to the user

main() # Call the main function to run the voice agent






