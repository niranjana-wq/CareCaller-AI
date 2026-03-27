from intent_detector import detect_intent
from llm_agent import generate_agent_response, extract_answer_from_user
from audio_handler import groq_client

QUESTIONS = [
    {"id": "feeling", "question": "How have you been feeling overall?"},
    {"id": "weight", "question": "What's your current weight in pounds?"},
    {"id": "height", "question": "What's your height in feet and inches?"},
    {"id": "weight_lost", "question": "How much weight have you lost this past month in pounds?"},
    {"id": "side_effects", "question": "Any side effects from your medication this month?"},
    {"id": "satisfied", "question": "Satisfied with your rate of weight loss?"},
    {"id": "goal_weight", "question": "What's your goal weight in pounds?"},
    {"id": "dosage_requests", "question": "Any requests about your dosage?"},
    {"id": "new_meds", "question": "Have you started any new medications or supplements since last month?"},
    {"id": "new_conditions", "question": "Do you have any new medical conditions since your last check-in?"},
    {"id": "allergies", "question": "Any new allergies?"},
    {"id": "surgeries", "question": "Any surgeries since your last check-in?"},
    {"id": "doctor_questions", "question": "Any questions for your doctor?"},
    {"id": "shipping_address", "question": "Has your shipping address changed?"}
]

SYSTEM_PROMPT = """You are Jessica, a healthcare call assistant for TrimRX. 
You are speaking with a patient. Your goal is to conduct a medication refill check-in.
- Keep your responses conversational, very brief, and human-like.
- Never provide medical advice. 
- Gently handle interruptions and steer the conversation back to the check-in question.
- CRITICAL: Never break character. Never output thoughts in parentheses. Do not explain your instructions."""

def process_turn(user_text, state, chat_history):
    # Detect intent
    intent = detect_intent(user_text)
    
    if intent == "wrong_number":
        state["call_ended"] = True
        return "I apologize, I must have the wrong number. Have a good day.", state
    elif intent == "opt_out":
        state["call_ended"] = True
        return "I understand. We will remove you from our calling list. Goodbye.", state
    elif intent == "reschedule":
        state["call_ended"] = True
        return "No problem, we will note that and call you back at a better time. Have a good day.", state
    elif intent == "escalate":
        state["escalate"] = True
        state["call_ended"] = True
        return "I'm sorry to hear that. I am connecting you to a healthcare professional right away.", state

    # State Machine Logic
    if state["current_step"] == "greeting":
        state["current_step"] = "questionnaire"
        state["question_index"] = 0
        agent_reply = "Great! Let's start the check-in. " + QUESTIONS[0]["question"]
        return agent_reply, state
        
    elif state["current_step"] == "questionnaire":
        idx = state["question_index"]
        current_q = QUESTIONS[idx]
        
        # Try extracting the answer for the current question
        answer = extract_answer_from_user(user_text, current_q["question"])
        
        if answer: 
            # We got a valid answer! Save it and move to the next question
            state["responses"][current_q["id"]] = answer
            state["question_index"] += 1
            
            if state["question_index"] >= len(QUESTIONS):
                state["current_step"] = "closing"
                state["call_ended"] = True
                return "Thank you for completing the check-in. Your responses have been recorded, and your medication refill will be processed. Have a wonderful day!", state
            else:
                next_q = QUESTIONS[state["question_index"]]
                
                # Context array specifically for LLM to make the transition natural
                # Only use the most recent interactions
                short_history = chat_history[-3:] if len(chat_history) > 3 else chat_history
                
                # Use LLM to generate a natural conversational flow into the next question
                agent_reply = generate_agent_response(short_history, next_q["question"], SYSTEM_PROMPT)
                return agent_reply, state
        else:
            # We didn't get a clear answer, re-ask using LLM keeping conversation natural
            short_history = chat_history[-3:] if len(chat_history) > 3 else chat_history
            agent_reply = generate_agent_response(short_history, current_q["question"], SYSTEM_PROMPT)
            return agent_reply, state

    elif state["current_step"] == "closing":
        state["call_ended"] = True
        return "Thank you, your call is completed. Have a good day.", state

    return "I am not sure what to say.", state
