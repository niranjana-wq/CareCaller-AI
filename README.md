**CareCaller AI**
Real-Time AI Voice Agent for Automated Healthcare Screening

**Live Demo:** https://care-caller-ai.vercel.app/

**Overview**

CareCaller AI is a real-time, voice-based AI healthcare assistant designed to automate initial patient screening.

The system enables users to interact using voice or text. It listens to patient input, processes it using AI, and responds with structured, context-aware medical questions and guidance.

This reduces manual workload, improves consistency, and enables scalable healthcare interaction.

**Problem Statement**

Initial patient screening is manual, repetitive, and time-consuming
Healthcare staff spend significant time on basic questioning
Call-based systems are slow and not scalable
Lack of real-time automated solutions for patient interaction

**Solution**

CareCaller AI introduces an AI-powered voice agent that:

Conducts structured conversations with patients
Understands user input using speech and language models
Follows a controlled questioning flow
Generates real-time responses
Operates continuously without human intervention

**How It Works**

User provides input (voice or text)
→ Audio is captured and transcribed (Speech-to-Text)
→ AI model processes context and intent
→ State machine determines next question
→ Response is generated
→ Converted to speech (Text-to-Speech)
→ Played back to the user

**Core Innovation**

**Controlled AI System**

The system uses a state machine combined with prompt engineering to ensure structured and relevant medical questioning instead of open-ended responses.

**Real-Time Processing**

End-to-end pipeline processes input and generates output within seconds.

**Multi-Modal Interaction**

Supports both voice and text input, with audio and text output.

**Tech Stack**

Frontend
HTML
CSS
JavaScript
Web Audio API
Backend
Python
FastAPI
Uvicorn
AI and Processing
Groq API (LLaMA 3.1)
Whisper (Speech-to-Text)
Prompt Engineering
State Machine Logic
Audio Processing
ElevenLabs (Text-to-Speech)
gTTS (Fallback)
Deployment
Frontend: Vercel
Backend: Render

**Key Benefits**

Feature	Existing Method	AI-Based System
Interaction	Manual calls or forms	Real-time voice interaction
Speed	Slow	Instant response
Accuracy	Prone to human error	Consistent AI-driven responses
Screening	Unstructured	Structured automated flow
Effort	High manual effort	Minimal human involvement
Scalability	Limited	Highly scalable
Availability	Limited hours	24/7 operation
Cost	High	Reduced operational cost

**API Endpoints**

**POST /chat_text**

Handles text-based interaction

Request:

{
  "user_text": "I have a headache"
}

**POST /chat_audio**

**Handles audio input**

Input: audio file (multipart/form-data)
Output: processed response and generated speech

**Installation and Setup**

**Clone the repository**
git clone https://github.com/<your-username>/CareCaller-AI.git
cd CareCaller-AI

**Backend Setup**
cd backend
pip install -r requirements.txt

**Environment Variables**

Create a .env file:

GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key

**Run Backend**
uvicorn main:app --reload

**Run Frontend**
Open:
frontend_web/index.html
Or use a local server (e.g., Live Server).

**Challenges Faced**

Handling browser audio formats (webm vs wav)
Managing real-time communication between frontend and backend
Maintaining conversation state across requests
Dealing with deployment cold starts on free-tier services
Future Improvements
Database integration for patient records
Multi-language support
Emotion detection from voice
Integration with hospital systems
Mobile application

**Contributor**
Niranjana J

**Final Note**
CareCaller AI demonstrates how AI can automate a critical part of healthcare workflows by handling initial patient interaction efficiently, consistently, and at scale.
It is a strong foundation for building real-world, production-ready AI healthcare systems.
