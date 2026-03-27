import streamlit as st
import requests
import json
import base64
from audio_recorder_streamlit import audio_recorder

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Healthcare Voice Agent", layout="wide")
st.title("Healthcare Voice Agent - Call Simulation")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "call_state" not in st.session_state:
    st.session_state.call_state = {
        "responses": {},
        "current_step": "greeting",
        "question_index": 0,
        "escalate": False,
        "call_ended": False
    }
if "last_audio" not in st.session_state:
    st.session_state.last_audio = b""

def process_text_input(text):
    st.session_state.chat_history.append({"role": "user", "message": text})
    payload = {
        "user_text": text,
        "state": st.session_state.call_state,
        "chat_history": st.session_state.chat_history
    }
    try:
        res = requests.post(f"{API_URL}/chat_text", json=payload)
        if res.status_code == 200:
            data = res.json()
            st.session_state.call_state = data["state"]
            agent_text = data["agent_text"]
            st.session_state.chat_history.append({"role": "agent", "message": agent_text})
            # Play audio logic
            if data.get("audio_b64"):
                b64 = data["audio_b64"]
                md = f"""<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>"""
                st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Backend Error: {e}")

def process_audio_input(audio_bytes):
    # Dummy text to show user speaking
    st.session_state.chat_history.append({"role": "user", "message": "🎤 (Voice Input)"})
    
    files = {"audio": ("user_audio.wav", audio_bytes, "audio/wav")}
    data = {
        "state": json.dumps(st.session_state.call_state),
        "chat_history": json.dumps(st.session_state.chat_history[:-1]) # exclude the dummy wait
    }
    
    try:
        with st.spinner("🎙️ Transcribing and thinking..."):
            res = requests.post(f"{API_URL}/chat_audio", files=files, data=data)
            
        if res.status_code == 200:
            resp_data = res.json()
            st.session_state.call_state = resp_data["state"]
            user_transcribed = resp_data["user_text"]
            agent_text = resp_data["agent_text"]
            
            # Update the dummy message with real transcription
            if not user_transcribed.strip():
                user_transcribed = "(Audio was unclear or silent)"
            st.session_state.chat_history[-1]["message"] = user_transcribed
            
            st.session_state.chat_history.append({"role": "agent", "message": agent_text})
            
            if resp_data.get("audio_b64"):
                b64 = resp_data["audio_b64"]
                md = f"""
                <audio controls autoplay="true" style="width: 100%;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
                st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Backend Error: {e}")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Conversation")
    
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Start / Reset Call"):
            st.session_state.chat_history = []
            st.session_state.call_state = {
                "responses": {},
                "current_step": "greeting",
                "question_index": 0,
                "escalate": False,
                "call_ended": False
            }
            # Start call
            process_text_input("hello")
            st.rerun()

    with b2:
        if st.button("End Call", type="primary"):
            st.session_state.call_state["call_ended"] = True
            st.warning("Call ended.")

    # Display as a Phone Call instead of Chat App
    st.markdown("### 📞 Live Call with Jessica (AI)")
    
    # Show only the latest interaction
    if st.session_state.chat_history:
        # Show what the user just said
        last_user = [m for m in st.session_state.chat_history if m["role"] == "user"]
        if last_user and last_user[-1]['message'] != "hello":
            st.success(f"**You said:** {last_user[-1]['message']}", icon="🗣️")
            
        last_agent = [m for m in st.session_state.chat_history if m["role"] == "agent"]
        if last_agent:
            st.info(f"**Jessica says:** {last_agent[-1]['message']}", icon="🤖")

    if not st.session_state.call_state["call_ended"]:
        st.write("---")
        st.subheader("Turn on your Microphone to Speak:")
        
        # FIX: The key ensures the React component remounts correctly after every turn!
        audio_bytes = audio_recorder("Record Response", icon_size="3x", key=f"audio_{len(st.session_state.chat_history)}")
        
        if audio_bytes and audio_bytes != st.session_state.last_audio:
            st.session_state.last_audio = audio_bytes
            process_audio_input(audio_bytes)
            st.rerun()
            
        st.write("*(Or fallback to typing:)*")
        user_input = st.chat_input("Type here if mic is unavailable...")
        if user_input:
            process_text_input(user_input)
            st.rerun()

with col2:
    st.subheader("Live State Data")
    
    st.write("**Escalation Status:**", 
             "🔴 ESCALATED" if st.session_state.call_state.get("escalate", False) else "🟢 Normal")
    st.write("**Call Status:**", "Ended" if st.session_state.call_state.get("call_ended") else "Active")
    st.write("**Current Step:**", st.session_state.call_state.get("current_step", "Unknown").upper())
    
    st.markdown("---")
    st.write("**Extracted Responses:**")
    st.json(st.session_state.call_state.get("responses", {}))
