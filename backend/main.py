from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
import base64
import tempfile
from pydantic import BaseModel

from state_machine import process_turn
from audio_handler import transcribe_audio, generate_speech

app = FastAPI(title="Healthcare Voice Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_text: str
    state: dict
    chat_history: list

@app.post("/chat_text")
async def chat_text(req: ChatRequest):
    """Handles text-based interaction from frontend"""
    agent_reply, new_state = process_turn(req.user_text, req.state, req.chat_history)
    
    # Try TTS
    audio_b64 = None
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp_path = tmp.name
    tmp.close()  # Close so Windows allows writing from generate_speech
    try:
        success = generate_speech(agent_reply, tmp_path)
        if success:
            with open(tmp_path, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"Audio generation error: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
            
    return {
        "agent_text": agent_reply,
        "state": new_state,
        "audio_b64": audio_b64
    }

@app.post("/chat_audio")
async def chat_audio(
    audio: UploadFile = File(...),
    state: str = Form(...),
    chat_history: str = Form(...)
):
    """Handles voice-based interaction from frontend"""
    # Parse inputs
    state_dict = json.loads(state)
    history_list = json.loads(chat_history)
    
    # STT
    user_text = ""
    with tempfile.NamedTemporaryFile(suffix=".wav", mode="wb", delete=False) as tmp:
        try:
            content = await audio.read()
            tmp.write(content)
            tmp.close()
            user_text = transcribe_audio(tmp.name)
        finally:
            os.unlink(tmp.name)
            
    if not user_text:
        return {
            "agent_text": "I'm sorry, I couldn't understand that. Could you please repeat?",
            "state": state_dict,
            "user_text": "",
            "audio_b64": None
        }
        
    # Standard turn processing
    agent_reply, new_state = process_turn(user_text, state_dict, history_list)
    
    # Try TTS
    audio_b64 = None
    tmp2 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp2_path = tmp2.name
    tmp2.close()
    try:
        success = generate_speech(agent_reply, tmp2_path)
        if success:
            with open(tmp2_path, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"Audio generation error: {e}")
    finally:
        if os.path.exists(tmp2_path):
            os.unlink(tmp2_path)
            
    return {
        "agent_text": agent_reply,
        "state": new_state,
        "user_text": user_text,
        "audio_b64": audio_b64
    }

# Mount static frontend
app.mount("/", StaticFiles(directory="frontend_web", html=True), name="static")

