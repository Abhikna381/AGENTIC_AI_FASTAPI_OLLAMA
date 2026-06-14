# Chain of Thought prompting
from dotenv import load_dotenv
from openai import OpenAI
import requests
import json
import time
from openai import RateLimitError
from pydantic import BaseModel, Field
from typing import Optional

import asyncio
import speech_recognition as sr
from openai.helpers import LocalAudioPlayer
from openai import AsyncOpenAI


load_dotenv()


client = OpenAI()
async_client = AsyncOpenAI()

async def tts(speech: str):
    async with async_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts", # Specify the model to use for text-to-speech conversion
        input=speech, # Provide the text input to be converted to speech
        voice="alloy", # Specify the voice to be used for the generated speech
        instructions="Always speak in a friendly tone.", # Provide instructions for the voice agent to follow when generating speech
        response_format="wav" # Specify the audio format for the output
    ) as response:# Create a speech audio using the OpenAI API with the provided text input
        await LocalAudioPlayer().play(response)



def get_weather(city: str):
    url = f"https://wttr.in/{city.lower().strip().replace(" ", "+")}?format=%C+%t"
    response = requests.get(url)


    if response.status_code == 200:
        return f"The Weather in {city} is {response.text}"
    
    return "Something went wrong"


available_tools = {
    "get_weather" : get_weather
}





SYSTEM_PROMPT = """
    You're an expert AI Assistant in resolving user queries using chain of the thought.
    You work on START, PLAN and OUTPUT steps.
    You need to first PLAN what needs to be done. The PLAN can be multiple steps.
    Once you think enough PLAN has been done, finally you can give an OUTPUT.
    You can also call a tool if required from the list of availabe tools.
    For every tool call wait for the observe step which is the output from the called tool.

    Rules:
    - Strictly Follow the given JSON output format
    - Only run one step at a time.
    - The sequence of steps is START (where user gives an input), PLAN (That can be multiple times) and finally we will get OUTPUT.

    Output JSON Format:
    { "step": "START" | "PLAN" | "OUTPUT" | "TOOL", "content": "string", "tool": "string", "input": "string"}


    Availabe Tools:
    - get_weather(city: str): Takes city name as an input string and return the weather information about the city


    Example 1:
    START: hey, can you solve 2 + 3 * 5 / 10
    PLAN: {"step": "PLAN": "content": "Seems like user is interested in math problem"}
    PLAN: {"step": "PLAN": "content": "looking at the problem, we should solve this using BODMAS method "}
    PLAN: {"step": "PLAN": "content": "Yes, The BODMAS is correct thing to be done here"}
    PLAN: {"step": "PLAN": "content": "First, we must multiply 3 * 5 which is 15"}
    PLAN: {"step": "PLAN": "content": "Now the new equation is 2 + 15 / 10"}
    PLAN: {"step": "PLAN": "content": "We must perform divide that is 15 / 10 = 1.5"}
    PLAN: {"step": "PLAN": "content": "Now the new equation is 2 + 1.5"}
    PLAN: {"step": "PLAN": "content": "Now finallty lets perform the add 3.5"}
    PLAN: {"step": "PLAN": "content": "Great, we have solved and finally left with 3.5 as ANSWER"}
    OUTPUT: {"step": "OUTPUT": "content": "3.5"}


    Example 2:
    START: What is the weather of Delhi ?
    PLAN: {"step": "PLAN": "content": "Seems like user is interested in getting weather of Delhi in India"}
    PLAN: {"step": "PLAN": "content": "Let's see if we have any available tool from the list of available tools"}
    PLAN: {"step": "PLAN": "content": "Great, we have get_weather tool availabe for this query"}
    PLAN: {"step": "PLAN": "content": "i need to call get_weather tool for Delhi as input for city"}
    PLAN: {"step": "TOOL": "tool": "get_weather", "input": "Delhi"}
    PLAN: {"step": "OBSERVE": "tool": "get_weather", "output": "The temperature of delhi is cloudy with 20 C"}
    PLAN: {"step": "PLAN": "content": "Great, I got the weather info about delhi"}
    OUTPUT: {"step": "OUTPUT": "content": "The current weather in delhi is 20 C with some cloudy sky"}


"""

print("\n\n\n")


message_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]


r = sr.Recognizer() # Create a Recognizer object

with sr.Microphone() as source: # Use the default microphone as the audio source
    r.adjust_for_ambient_noise(source) # Adjust for ambient noise
    r.pause_threshold = 2 # Set the pause threshold for speech recognition


    while True:
        print("Speak Something....")
        audio = r.listen(source) # Listen for audio input

        print("Processing.... Please wait... (STT)")
        try:
            user_query = r.recognize_google(audio)
            print(f"You Said: {user_query}")

        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            continue

        except sr.RequestError as e:
            print(f"❌ Google STT Error: {e}")
            continue
        message_history.append({"role": "user", "content": user_query})


        while True:
            try:
                response = client.chat.completions.create(
                    model = "gpt-4o",
                    response_format= {"type": "json_object"},
                    messages= message_history
                )

            except RateLimitError as e:
                print(f"⏳ Rate limit hit. Waiting 5 seconds... (Error: {e})")
                time.sleep(5)
                continue # Retry the same request   


            raw_result = response.choices[0].message.content
            
            message_history.append({"role": "assistant", "content": raw_result})
            


            parsed_result = json.loads(raw_result)
            


            if parsed_result.get("step") == "START":
                print("🔥", parsed_result.get("content"))
                continue

            if parsed_result.get("step") == "TOOL":
                tool_to_call = parsed_result.get("tool")
                tool_input = parsed_result.get("input")
                print(f"🤫: {tool_to_call} ({tool_input})")

                tool_response = available_tools[tool_to_call](tool_input)
                print(f"🤫: {tool_to_call} ({tool_input}) = {tool_response}")

                message_history.append({"role": "developer","content": json.dumps(
                    {"step":"OBSERVE","tool": tool_to_call,"input": tool_input, "output": tool_response}
                )})
                continue


            if parsed_result.get("step") == "PLAN":
                print("🧠", parsed_result.get("content"))
                continue

            if parsed_result.get("step") == "OUTPUT":
                print("🕯️", parsed_result.get("content"))
                asyncio.run(tts(speech = parsed_result.get("content"))) # Call the text-to-speech function to convert the response to speech and play it to the user
                break

print("\n\n\n")