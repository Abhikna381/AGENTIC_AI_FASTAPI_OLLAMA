import os
import asyncio
import pygame
import speech_recognition as sr

from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

# =========================
# OPENAI CLIENTS
# =========================
client = OpenAI()
async_client = AsyncOpenAI()

# =========================
# INITIALIZE PYGAME
# =========================
pygame.mixer.init()

# =========================
# CONVERSATION MEMORY
# =========================
conversation_history = [
    {
        "role": "system",
        "content": """
        You are Jarvis, a real-time conversational AI voice assistant.

        Rules:
        - Speak naturally like a human
        - Keep responses short
        - Maximum 2 short sentences
        - Be friendly and helpful
        - Respond fast like a voice assistant
        """
    }
]


# =========================
# TEXT TO SPEECH
# =========================
async def tts(speech: str):

    try:

        # Stop previous audio
        pygame.mixer.music.stop()

        # Remove old file
        if os.path.exists("output.mp3"):
            os.remove("output.mp3")

        # Generate speech
        response = await async_client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=speech,
            response_format="mp3"
        )

        # Read audio bytes
        audio_data = await response.aread()

        # Save audio
        with open("output.mp3", "wb") as f:
            f.write(audio_data)

        # Load audio
        pygame.mixer.music.load("output.mp3")

        # Play audio
        pygame.mixer.music.play()

        # Wait until speaking completes
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

    except Exception as e:
        print("TTS Error:", e)


# =========================
# ASK AI
# =========================
async def ask_ai(user_input):

    try:

        # Store user message
        conversation_history.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        # Generate AI response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            max_tokens=60
        )

        ai_response = response.choices[0].message.content

        # Store assistant response
        conversation_history.append(
            {
                "role": "assistant",
                "content": ai_response
            }
        )

        return ai_response

    except Exception as e:
        print("AI Error:", e)
        return "Sorry, something went wrong."


# =========================
# MAIN FUNCTION
# =========================
async def main():

    print("\n🤖 Conversational AI Assistant Started")
    print("Say 'exit' or 'bye' to stop.\n")

    recognizer = sr.Recognizer()

    # =========================
    # MICROPHONE SETUP
    # =========================
    with sr.Microphone() as source:

        print("🎤 Calibrating microphone once...")

        # Calibrate ONLY ONCE
        recognizer.adjust_for_ambient_noise(source, duration=2)

        # Better microphone settings
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = False
        recognizer.pause_threshold = 1

        print("✅ Microphone ready!\n")

        # =========================
        # CONVERSATION LOOP
        # =========================
        while True:

            try:

                print("🎤 Listening...")

                # Listen to microphone
                audio = recognizer.listen(
                    source,
                    timeout=None,
                    phrase_time_limit=8
                )

                print("⚡ Processing speech...")

                # Convert speech to text
                user_input = recognizer.recognize_google(audio)

                print(f"\n🧑 You: {user_input}")

                # =========================
                # EXIT COMMANDS
                # =========================
                if user_input.lower() in [
                    "exit",
                    "quit",
                    "bye",
                    "stop"
                ]:

                    goodbye = "Goodbye! Have a great day."

                    print(f"\n🤖 AI: {goodbye}")

                    await tts(goodbye)

                    break

                # =========================
                # ASK AI
                # =========================
                ai_response = await ask_ai(user_input)

                print(f"\n🤖 AI: {ai_response}")

                # =========================
                # SPEAK RESPONSE
                # =========================
                await tts(ai_response)

            except sr.UnknownValueError:
                print("❌ Could not understand audio")

            except sr.RequestError as e:
                print("❌ Speech Recognition Error:", e)

            except Exception as e:
                print("❌ Error:", e)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    asyncio.run(main())