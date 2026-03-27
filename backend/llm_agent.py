import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"Failed to initialize Groq client: {e}")
    groq_client = None

def generate_agent_response(transcript_history, current_question, system_prompt):
    """
    Uses LLM to generate the next conversational response.
    Context is constrained strictly by the system prompt.
    """
    if not groq_client:
        return "System error: Groq API client not initialized."

    messages = [{"role": "system", "content": system_prompt}]
    for msg in transcript_history:
        role = msg["role"]
        if role == "agent":
            role = "assistant"
        messages.append({"role": role, "content": msg["message"]})
        
    # Append a prompt directing the agent to ask the current question
    messages.append({
        "role": "system", 
        "content": f"The patient is currently on this step. You must gently steer the conversation to ask or ask directly: '{current_question}'. Reply directly as the agent without any meta-commentary or explanations."
    })
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=150
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Generation Error: {e}")
        return "I'm having trouble connecting right now. Can you repeat that?"

def extract_answer_from_user(user_text: str, question: str) -> str:
    """
    Given the user's text and the question asked, uses LLM to extract the concise answer.
    """
    if not groq_client: return user_text
    
    prompt = f"""
    The patient was asked: "{question}"
    The patient answered: "{user_text}"
    
    Extract the concise, factual answer to the question from the patient's response.
    CRITICAL INSTRUCTION: You MUST return ONLY the raw factual value (e.g., '148', '5'6', 'No', 'Nausea'). Do NOT include any introductory text, quotes, or complete sentences like "The answer is...".
    If the patient didn't answer or it's unclear, return 'UNKNOWN'.
    """
    try:
        res = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.0,
            max_tokens=50
        )
        ans = res.choices[0].message.content.strip()
        if ans.upper() == "UNKNOWN":
            return ""
        return ans
    except:
        return ""
