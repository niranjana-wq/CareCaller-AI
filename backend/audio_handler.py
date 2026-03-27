import os
import requests
from dotenv import load_dotenv
from gtts import gTTS
from backend.llm_agent import groq_client

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

def transcribe_audio(audio_file_path: str) -> str:
    """Uses Groq's high-speed Whisper API to transcribe audio file to text."""
    if not groq_client:
        return "Audio transcription disabled during setup."
    try:
        with open(audio_file_path, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=(os.path.basename(audio_file_path), file.read()),
                model="whisper-large-v3",
                language="en"
            )
            return transcription.text.strip()
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""

def generate_tts_elevenlabs(text: str, output_path: str) -> bool:
    """Primary TTS using ElevenLabs - Rachel voice (female)."""
    if not ELEVENLABS_API_KEY:
        return False
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"ElevenLabs error: {response.text}")
            return False
    except Exception as e:
        print(f"ElevenLabs request error: {e}")
        return False

def generate_tts_gtts(text: str, output_path: str) -> bool:
    """
    Female-sounding TTS using Google TTS.
    tld='co.uk' gives a clear female British-English voice.
    """
    try:
        tts = gTTS(text=text, lang="en", tld="co.uk", slow=False)
        tts.save(output_path)
        return True
    except Exception as e:
        print(f"gTTS error: {e}")
        return False

def generate_speech(text: str, output_path: str) -> bool:
    """
    Try ElevenLabs first (best quality female voice).
    Fall back to gTTS female voice if ElevenLabs is unavailable.
    """
    if ELEVENLABS_API_KEY:
        success = generate_tts_elevenlabs(text, output_path)
        if success:
            return True
    return generate_tts_gtts(text, output_path)