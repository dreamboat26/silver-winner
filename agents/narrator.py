import os

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs


async def narrate(text: str, voice: str, model: str, output_file: str):
    load_dotenv()
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    response = client.text_to_speech.convert(text=text, voice_id=voice, model_id=model)
    with open(output_file, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
