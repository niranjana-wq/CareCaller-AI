from backend.llm_agent import groq_client

def detect_intent(user_text: str) -> str:
    """
    Detects user intent to handle edge cases.
    Returns one of: 'normal', 'wrong_number', 'opt_out', 'reschedule', 'escalate'
    """
    lower_text = user_text.lower()
    
    # Fast Rule-based Detection
    if any(phrase in lower_text for phrase in ["wrong number", "who is this", "not me", "wrong person"]):
        return "wrong_number"
    
    if any(phrase in lower_text for phrase in ["stop calling", "opt out", "do not call", "remove me", "unsubscribe"]):
        return "opt_out"
        
    if any(phrase in lower_text for phrase in ["call me back", "busy", "reschedule", "later", "not a good time", "have to go", "driving"]):
        return "reschedule"
        
    if any(phrase in lower_text for phrase in ["severe pain", "hospital", "emergency", "can't breathe", "chest pain", "bleeding"]):
        return "escalate"

    # LLM Fallback detection for ambiguity (optional, only if confident)
    if groq_client:
        prompt = f"""
        Classify the intent of the following user utterance into one of these exact words:
        [normal, wrong_number, opt_out, reschedule, escalate]
        
        Utterance: "{user_text}"
        
        CRITICAL RULES:
        1. If the user provides a number (like weight or blood pressure), a date, symptoms, or a short yes/no answer, it is ALWAYS "normal".
        2. Only output "wrong_number" if they explicitly say you have the wrong person or ask who you are trying to reach.
        
        Reply with ONLY the classification word and nothing else.
        """
        try:
            res = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant", # faster model for intent 
                temperature=0.0,
                max_tokens=10
            )
            intent = res.choices[0].message.content.strip().lower()
            if intent in ["normal", "wrong_number", "opt_out", "reschedule", "escalate"]:
                return intent
        except:
            pass
            
    return "normal"
