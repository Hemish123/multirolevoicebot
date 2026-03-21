# from knowledge.services.retriever import retrieve_relevant_chunks
# from conversations.services.azure_openai_service import generate_response
 
 
# def information_strategy(agent, message, session):
#     context = retrieve_relevant_chunks(agent, message)
 
#     if not context:
#         context = ""
 
#     if not context.strip():
#         return "This information is not mentioned in the uploaded document."
 
#     system_prompt = f"""
# {agent.resolved_prompt}
 
# Conversation Stage: {session.stage or "new"}
 
# Knowledge Context:
# {context}
 
# Respond naturally and professionally.
# Use only the knowledge context.
# Do not hallucinate.
# Add helpful follow-up suggestions when appropriate.
# """
 
#     return generate_response(system_prompt, message)
 
 
# def transaction_strategy(agent, message, session):
#     print("TRANSACTION STRATEGY CALLED")
#     print("CURRENT STAGE:", session.stage)
#     print("CURRENT STATE:", session.state)
 
#     state = session.state or {}
#     msg = message.lower()
 
#     # 🔹 Handle polite closing after completion
#     if session.stage == "completed":
#         if any(word in msg for word in ["thank", "thanks", "ok", "okay"]):
#             return "You're most welcome. If you need any further assistance, I'm here to help."
 
#         # Reset if new request
#         session.stage = None
#         session.state = {}
#         session.save()
#         return information_strategy(agent, message, session)
 
#     # 🔹 STEP 1 — Collect Patient Name
#     if not state.get("patient_name"):
#         if session.stage == "collecting_name":
#             state["patient_name"] = message.strip()
#             session.state = state
#             session.stage = "collecting_date"
#             session.save()
#             return f"Thank you, {state['patient_name']}. What date would you prefer for the appointment?"
 
#         session.stage = "collecting_name"
#         session.save()
#         return "Sure, I can help with that. May I have your full name, please?"
 
#     # 🔹 STEP 2 — Collect Preferred Date
#     if not state.get("date"):
#         if session.stage == "collecting_date":
#             state["date"] = message.strip()
#             session.state = state
#             session.stage = "collecting_time"
#             session.save()
#             return "Got it. Do you have a preferred time slot?"
 
#         session.stage = "collecting_date"
#         session.save()
#         return "Please let me know your preferred appointment date."
 
#     # 🔹 STEP 3 — Collect Preferred Time
#     if not state.get("time"):
#         if session.stage == "collecting_time":
#             state["time"] = message.strip()
#             session.state = state
#             session.stage = "confirming"
#             session.save()
 
#             return (
#                 f"Just to confirm, the appointment is for {state['patient_name']} "
#                 f"on {state['date']} at {state['time']}. "
#                 f"Should I proceed with this booking?"
#             )
 
#         session.stage = "collecting_time"
#         session.save()
#         return "Could you please share your preferred time?"
 
#     # 🔹 STEP 4 — Confirmation
#     if session.stage == "confirming":
#         if "yes" in msg:
#             session.stage = "completed"
#             session.state = {}
#             session.save()
#             return (
#                 "Your appointment has been scheduled successfully. "
#                 "We look forward to seeing you. If you need to make any changes, just let me know."
#             )
#         else:
#             session.stage = "collecting_date"
#             session.save()
#             return "No problem. Let's update the details. What new date would you prefer?"
 
#     return "How can I assist you further?"
 
 
# # def qualification_strategy(agent, message, session):
 
# #     state = session.state or {}
# #     msg = message.lower()
 
# #     # STEP 1 — Collect Property Type
# #     if not state.get("property_type"):
# #         if session.stage == "collecting_property_type":
# #             state["property_type"] = message
# #             session.state = state
# #             session.stage = "collecting_location"
# #             session.save()
# #             return "Great. Which location are you interested in?"
 
# #         session.stage = "collecting_property_type"
# #         session.save()
# #         return "What type of property are you looking for? (Apartment, Villa, Commercial, etc.)"
 
# #     # STEP 2 — Collect Location
# #     if not state.get("location"):
# #         if session.stage == "collecting_location":
# #             state["location"] = message
# #             session.state = state
# #             session.stage = "collecting_budget"
# #             session.save()
# #             return "Understood. What is your approximate budget range?"
 
# #         session.stage = "collecting_location"
# #         session.save()
# #         return "Which location do you prefer?"
 
# #     # STEP 3 — Collect Budget
# #     if not state.get("budget"):
# #         if session.stage == "collecting_budget":
# #             state["budget"] = message
# #             session.state = state
# #             session.stage = "suggesting"
# #             session.save()
 
# #             query = f"{state['property_type']} in {state['location']} under {state['budget']}"
# #             context = retrieve_relevant_chunks(agent, query)
 
# #             if not context:
# #                 return "I currently don't see exact matches in that range. Would you like to adjust your budget or location?"
 
# #             system_prompt = f"""
# # {agent.resolved_prompt}
 
# # Buyer Requirements:
# # Property Type: {state['property_type']}
# # Location: {state['location']}
# # Budget: {state['budget']}
 
# # Available Listings:
# # {context}
 
# # Suggest the most relevant properties naturally and offer site visit.
# # """
 
# #             return generate_response(system_prompt, message)
 
# #         session.stage = "collecting_budget"
# #         session.save()
# #         return "What is your budget range?"
 
# #     return "Would you like to schedule a site visit for any of these options?"
 
 
 
 
 
 
 
 
# def qualification_strategy(agent, message, session):
 
#     state = session.state or {}
#     msg = message.lower()
 
#     # 🔹 FIRST: Handle General Information Questions
#     if any(word in msg for word in ["information", "about you", "services", "what do you have", "address", "office"]):
#         return information_strategy(agent, message, session)
 
#     # 🔹 SECOND: If user says no after suggestion → reset flow
#     if msg in ["no", "not interested", "maybe later"]:
#         session.stage = None
#         session.state = {}
#         session.save()
#         return "No problem at all. Let me know if you'd like to explore other options or need any information."
 
#     # 🔹 STEP 1 — Property Type
#     if not state.get("property_type"):
#         if session.stage == "collecting_property_type":
#             state["property_type"] = message
#             session.state = state
#             session.stage = "collecting_location"
#             session.save()
#             return f"Nice choice. Which location are you considering?"
 
#         session.stage = "collecting_property_type"
#         session.save()
#         return "Sure — are you looking for an apartment, villa, or commercial property?"
 
#     # 🔹 STEP 2 — Location
#     if not state.get("location"):
#         if session.stage == "collecting_location":
#             state["location"] = message
#             session.state = state
#             session.stage = "collecting_budget"
#             session.save()
#             return "Got it. What budget range are you comfortable with?"
 
#         session.stage = "collecting_location"
#         session.save()
#         return "Which location do you have in mind?"
 
#     # 🔹 STEP 3 — Budget
#     if not state.get("budget"):
#         if session.stage == "collecting_budget":
#             state["budget"] = message
#             session.state = state
#             session.stage = "suggesting"
#             session.save()
 
#             query = f"{state['property_type']} in {state['location']} under {state['budget']}"
#             context = retrieve_relevant_chunks(agent, query)
 
#             if not context:
#                 return (
#                     f"I’m not seeing an exact match for a {state['property_type']} "
#                     f"in {state['location']} within {state['budget']}. "
#                     "Would you like to adjust location or explore nearby areas?"
#                 )
 
#             system_prompt = f"""
# {agent.resolved_prompt}
 
# Buyer Requirement:
# Property Type: {state['property_type']}
# Location: {state['location']}
# Budget: {state['budget']}
 
# Available Listings:
# {context}
 
# Respond naturally. Suggest best options.
# Do NOT force site visit.
# Offer it softly at the end.
# """
 
#             return generate_response(system_prompt, message)
 
#         session.stage = "collecting_budget"
#         session.save()
#         return "What is your approximate budget?"
 
#     # 🔹 AFTER SUGGESTION — Only offer visit if user shows interest
#     if any(word in msg for word in ["visit", "see property", "schedule", "book"]):
#         session.stage = None
#         session.save()
#         return transaction_strategy(agent, message, session)
 
#     return information_strategy(agent, message, session)
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
# def classify_medical_case(agent, message):
 
#     system_prompt = f"""
# You are a medical triage classifier.
 
# Hospital Specialty: {agent.company_name}
 
# Return JSON only in this format:
 
# {{
#   "severity": "emergency | urgent | mild | informational",
#   "domain_relevance": "in_scope | out_of_scope"
# }}
 
# Rules:
# - emergency = life-threatening symptoms (chest pain, breathing difficulty, unconsciousness, heavy bleeding)
# - urgent = needs doctor soon
# - mild = minor symptom
# - informational = service question
# """
 
#     response = generate_response(system_prompt, message)
 
#     import json
#     try:
#         return json.loads(response)
#     except:
#         return {
#             "severity": "informational",
#             "domain_relevance": "in_scope"
#         }
 
 
# def support_strategy(agent, message, session):
 
#     case = classify_medical_case(agent, message)
 
#     severity = case.get("severity")
#     domain = case.get("domain_relevance")
 
#     # Emergency
#     if severity == "emergency":
#         return (
#             "⚠️ This may require urgent medical attention. "
#             "Please visit the emergency department or contact emergency services immediately."
#         )
 
#     # Out of scope
#     if domain == "out_of_scope":
#         return (
#             f"This concern appears outside the specialty of {agent.company_name}. "
#             "It would be best to consult the appropriate specialist or a general hospital."
#         )
 
#     # Urgent
#     if severity == "urgent":
#         return (
#             "This seems important and should be evaluated by a doctor soon. "
#             "Would you like me to help you book an appointment?"
#         )
 
#     # Mild
#     if severity == "mild":
#         return (
#             "This doesn’t sound urgent, but it’s still a good idea to consult a doctor if it continues. "
#             "Would you like assistance scheduling a visit?"
#         )
 
#     # Default → informational
#     return information_strategy(agent, message, session)





from knowledge.services.retriever import retrieve_relevant_chunks
from conversations.services.azure_openai_service import generate_response
import dateparser
import re
from dateparser.search import search_dates
from datetime import datetime, timedelta
import json
 
#==changes after testing=========================
# 🔹 ADD THESE FUNCTIONS HERE

from datetime import datetime, timedelta
import re

def normalize_datetime(message):

    msg = message.lower().strip()

    # remove punctuation
    msg = re.sub(r"[^\w\s]", "", msg)

    # ---- ordinal word conversion ----

    ordinal_map = {
        "first": "1",
        "second": "2",
        "third": "3",
        "fourth": "4",
        "fifth": "5",
        "sixth": "6",
        "seventh": "7",
        "eighth": "8",
        "ninth": "9",
        "tenth": "10"
    }

    for word, num in ordinal_map.items():
        if word in msg:
            msg = msg.replace(word, num)
    
    # remove st/nd/rd/th
    msg = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", msg)

    today = datetime.now()

    # 🔹 Time detection FIRST
    time_map = {
        "morning": "09:00",
        "afternoon": "14:00",
        "evening": "18:00",
        "night": "20:00"
    }

    for word, value in time_map.items():
        if word in msg:
            return {"date": None, "time": value}

    # ---- relative day handling ----

    if "day after tomorrow" in msg:
        return {"date": (today + timedelta(days=2)).strftime("%Y-%m-%d"), "time": None}

    if "tomorrow" in msg:
        return {"date": (today + timedelta(days=1)).strftime("%Y-%m-%d"), "time": None}

    if "today" in msg:
        return {"date": today.strftime("%Y-%m-%d"), "time": None}
    

    # ---- after X days handling ----

    # numeric days like "after 3 days", "in 5 days"
    match = re.search(r"(after|in)\s+(\d+)\s+day", msg)
    if match:
        days = int(match.group(2))
        date = today + timedelta(days=days)
        return {"date": date.strftime("%Y-%m-%d"), "time": None}

    match = re.search(r"(after|in)\s+(\d+)\s+days", msg)
    if match:
        days = int(match.group(2))
        date = today + timedelta(days=days)
        return {"date": date.strftime("%Y-%m-%d"), "time": None}


    # word numbers like "after two days"
    word_numbers = {
        "one":1, "two":2, "three":3, "four":4, "five":5,
        "six":6, "seven":7, "eight":8, "nine":9, "ten":10
    }

    for word, num in word_numbers.items():
        if f"after {word} day" in msg or f"after {word} days" in msg:
            date = today + timedelta(days=num)
            return {"date": date.strftime("%Y-%m-%d"), "time": None}

    # ---- weekday handling ----

    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }

    for day, idx in weekdays.items():

        if f"next {day}" in msg:
            days_ahead = (idx - today.weekday()) + 7
            date = today + timedelta(days=days_ahead)
            return {"date": date.strftime("%Y-%m-%d"), "time": None}

        elif day in msg:
            days_ahead = idx - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            date = today + timedelta(days=days_ahead)
            return {"date": date.strftime("%Y-%m-%d"), "time": None}

    # ---- month date parsing ----

    try:
        parsed = datetime.strptime(msg, "%d %B")
        parsed = parsed.replace(year=today.year)
        return {"date": parsed.strftime("%Y-%m-%d"), "time": None}
    except:
        pass

    try:
        parsed = datetime.strptime(msg, "%d %b")
        parsed = parsed.replace(year=today.year)
        return {"date": parsed.strftime("%Y-%m-%d"), "time": None}
    except:
        pass

    return {"date": None, "time": None}
#======================================================

def rewrite_user_query(message):

    msg = message.lower()

    # 🔹 Course name normalization for better retrieval
    course_map = {
        "bcom": "B.Com",
        "bba": "BBA",
        "mba": "MBA",
        "bsc": "B.Sc",
        "ba": "B.A"
    }

    for k, v in course_map.items():
        if k in msg:
            return v + " course eligibility fee admission"

    if "cheapest" in msg or "lowest fee" in msg:
        return "course with lowest fee tuition"

    if "most expensive" in msg:
        return "course with highest fee"

    prompt = f"""
Rewrite the user question so it is clearer for knowledge retrieval.

Rules:
- Keep meaning same
- Make it concise
- Do not add new information

User message:
{message}
"""

    try:
        rewritten = generate_response(prompt, message)
        return rewritten.strip()
    except:
        return message



def llm_intent_clarifier(message):

    prompt = f"""
Classify the user's message intent.

Return ONLY one of these words:

information
demo
sales
qualification
general

Message:
{message}
"""

    try:
        intent = generate_response(prompt, message)
        return intent.strip().lower()
    except:
        return "general"



def normalize_course_names(text):

    # Replace dot pronunciation
    text = re.sub(r"\bB\.?\s*dot\s*com\b", "B Com", text, flags=re.IGNORECASE)

    # Replace B.Com variations
    text = re.sub(r"\bB\.?\s*Com\b", "B Com", text, flags=re.IGNORECASE)

    # Other course formats
    text = re.sub(r"\bB\.?\s*A\b", "B A", text, flags=re.IGNORECASE)
    text = re.sub(r"\bB\.?\s*Sc\b", "B Sc", text, flags=re.IGNORECASE)

    return text




#==========================================================

def validate_appointment_slot(date_str, time_str):
    try:
        dt = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M")
    except:
        return False, "invalid"

    if dt < datetime.now():
        return False, "past"

    if dt.hour < 9 or dt.hour > 18:
        return False, "closed"

    if dt.weekday() == 6:
        return False, "closed"

    return True, "valid"


# def identity_guard(agent, message):
#     """
#     Intercepts identity-related questions BEFORE any strategy logic.
#     Returns a response string if handled, otherwise None.
#     """

#     msg = message.lower().strip()

#     identity_phrases = [
#         "who are you",
#         "what is your name",
#         "introduce yourself",
#         "tell me about you",
#         "what do you do"
#     ]

#     if any(p in msg for p in identity_phrases):
#         system_prompt = f"""
# {agent.resolved_prompt}

# User is asking about your identity.

# Instructions:
# - Introduce yourself clearly.
# - Mention your role and company.
# - Do NOT start any sales, qualification, or booking flow.
# - Keep response to 2–3 sentences.
# - Sound human and professional.
# """
#         return generate_response(system_prompt, message)

#     return None



#after testing changes===========
def identity_guard(agent, message):
    """
    Intercepts identity-related questions BEFORE any strategy logic.
    Returns a response string if handled, otherwise None.
    """

    msg = message.lower().strip()

    # 🔹 NEW: service/domain keywords to bypass identity guard
    service_keywords = [
        "department", "departments",
        "service", "services",
        "specialty", "specialties",
        "clinic", "clinics",
        "treatment", "treatments",
        "doctor", "doctors",
        "hospital", "facility"
    ]

    # If user is asking about hospital services → skip identity guard
    if any(word in msg for word in service_keywords):
        return None

    identity_phrases = [
        "who are you",
        "what is your name",
        "introduce yourself",
        "tell me about you",
        "what do you do"
    ]

    if any(p in msg for p in identity_phrases):
        system_prompt = f"""
{agent.resolved_prompt}

User is asking about your identity.

Instructions:
- Introduce yourself clearly.
- Mention your role and company.
- Do NOT start any sales, qualification, or booking flow.
- Keep response to 2–3 sentences.
- Sound human and professional.
"""
        return generate_response(system_prompt, message)

    return None


def university_identity_guard(agent, message):

    import re

    msg = message.lower()

    # Detect university mentions
    university_pattern = r"(?:university|college|institute)\s+[a-zA-Z]+|[a-zA-Z]+\s+(?:university|college|institute)"

    matches = re.findall(university_pattern, msg)

    if not matches:
        return None

    agent_uni = (agent.company_name or "").lower()

    for uni in matches:
        if agent_uni not in uni.lower():
            return (
                f"I can only provide scholarship information for {agent.company_name}. "
                "For other universities, please contact their admissions office."
            )

    return None


#/////////////////////////////////////////////////////////////////////////

def information_strategy(agent, message, session):

    rewritten_query = rewrite_user_query(message)
    context = retrieve_relevant_chunks(agent, rewritten_query)

    # fallback retrieval
    if not context.strip():
        context = retrieve_relevant_chunks(agent, message)

    msg = message.lower()

    is_cheapest_query = any(word in msg for word in [
        "cheapest",
        "lowest fee",
        "least fee",
        "minimum fee"
    ])
    # 🟢 If general capability question → allow natural response
    general_questions = [
        "who are you",
        "what is your company",
        "what information",
        "what services",
        "summarize",
        "about you"
    ]


    service_keywords = [
    "department", "departments",
    "service", "services",
    "specialty", "specialties",
    "doctor", "doctors",
    "clinic", "clinics"
    ]

    if any(q in msg for q in general_questions) and not any(k in msg for k in service_keywords):
        system_prompt = f"""
{agent.resolved_prompt}

User is asking about general information.

Respond naturally and confidently about:
- Your role
- The type of information you provide
- Your company name if available

Do NOT mention document limitation.
Keep it conversational.
"""
        reply = generate_response(system_prompt, message)
        return normalize_course_names(reply)

    # 🔴 If no relevant context found for property-specific question
    if not context.strip():
        return (
            "At the moment, I don’t have matching details for that request. "
            "If you need any other information tell me."
        )
    
    # cheapest course logic
    if is_cheapest_query:

        system_prompt = f"""
{agent.resolved_prompt}

Knowledge Context:
{context}

User Question:
{message}

Instructions:
- Identify courses and their fees.
- Compare the fees.
- Tell which course has the lowest fee.
- Keep response under 2 sentences.

Formatting Rules:
- Write course names exactly as: BCA, BBA, B.Com, MBA, MCA
- Never write "B dot com"
"""

        reply = generate_response(system_prompt, message)
        return normalize_course_names(reply)

    # 🟢 Normal knowledge response
    system_prompt = f"""
{agent.resolved_prompt}

Knowledge Context:
{context}


Formatting Rules:
- Write course names exactly as: BCA, BBA, B.Com, MBA, MCA
- Never write "B dot com"


Respond in a short, natural tone.
Maximum 2–3 sentences.
Under 70 words.
No repetition.
Be direct and helpful.
Do not hallucinate.
"""

    reply = generate_response(system_prompt, message)
    reply = normalize_course_names(reply)
    return reply
 
 




def transaction_strategy(agent, message, session):
    print("TRANSACTION STRATEGY CALLED")
    print("CURRENT STAGE:", session.stage)
    print("CURRENT STATE:", session.state)
 
    state = session.state or {}
    msg = message.lower()

    #change after testing====================
    # 🔄 Update request after booking
    if session.stage == "completed" and any(word in msg for word in ["update","change","modify","reschedule"]):

        state = session.state or {}

        # Keep patient name, only reset date/time
        if "date" in state:
            del state["date"]

        if "time" in state:
            del state["time"]

        session.state = state
        session.stage = "collecting_date"
        session.save()

        return "Sure, I can help update your appointment. What new date would you prefer?"
    #==========================================
    
    #changes after testing=================================================

    # 🔴 Cancel / Stop booking flow
    if any(word in msg for word in ["cancel", "stop", "exit", "quit"]):
        session.stage = None
        session.state = {}
        session.save()
        return "Okay, I've cancelled the appointment booking process. Let me know if you need anything else."

    # 🔄 Reschedule request
    if "reschedule" in msg:
        session.stage = "collecting_date"
        session.save()
        return "Sure, let's reschedule your appointment. What new date would you prefer?"
    #======================================================================
    # 🔹 Handle polite closing after completion
    if session.stage == "completed":
        if any(word in msg for word in ["thank", "thanks", "ok", "okay"]):
            return "You're most welcome. If you need any further assistance, I'm here to help."
 
        # Reset if new request
        session.stage = None
        session.state = {}
        session.save()
        return information_strategy(agent, message, session)
 
    # 🔹 STEP 1 — Collect Patient Name
    # if not state.get("patient_name"):
    if not state.get("patient_name") and session.stage != "collecting_date":
        if session.stage == "collecting_name":
            name = re.sub(r"(my name is|i am|myself|this is|my name|i|my self is)", "", message.lower()).strip()
            state["patient_name"] = name.title()
            session.state = state
            session.stage = "collecting_date"
            session.save()
            return f"Thank you, {state['patient_name']}. What date would you prefer for the appointment?"
 
        session.stage = "collecting_name"
        session.save()
        return "Sure, I can help with that. May I have your full name, please?"
 
    # 🔹 STEP 2 — Collect Preferred Date
    if not state.get("date"):
        if session.stage == "collecting_date":
            # state["date"] = message.strip()
            #change after testing=======================================
            # slot = normalize_datetime(message)

            # if not slot["date"] or not slot["time"]:
            slot = normalize_datetime(message) or {"date": None, "time": None}

             # ❌ If date not detected
            if not slot.get("date"):
                return "I couldn't understand the appointment date. Could you please tell me the date?"

            # ✔ Date detected but time missing
            if slot.get("date") and not slot.get("time"):
                state["date"] = slot["date"]
                session.state = state
                session.stage = "collecting_time"
                session.save()
                return "Got it. What time would you prefer for the appointment?"

            # ✔ Date + Time detected together
            is_valid, reason = validate_appointment_slot(slot["date"], slot["time"])

            if not is_valid:

                if reason == "past":
                    return "That date has already passed. Please choose a future appointment date."

                if reason == "closed":
                    return "Our clinic operates between 9 AM and 6 PM. Please choose a valid appointment time."

                if reason == "invalid":
                    return "That doesn't look like a valid appointment slot."

            state["date"] = slot["date"]
            state["time"] = slot["time"]

            session.state = state
            session.stage = "confirming"
            session.save()

            return (
                f"Just to confirm, the appointment is for {state['patient_name']} "
                f"on {state['date']} at {state['time']}. Should I proceed?"
            )

        session.stage = "collecting_date"
        session.save()
        return "Please let me know your preferred appointment date."
    
    # 🔹 STEP 3 — Collect Preferred Time
    if not state.get("time"):
        if session.stage == "collecting_time":
            state["time"] = message.strip()
            session.state = state
            session.stage = "confirming"
            session.save()
 
            return (
                f"Just to confirm, the appointment is for {state['patient_name']} "
                f"on {state['date']} at {state['time']}. "
                f"Should I proceed with this booking?"
            )
 
        session.stage = "collecting_time"
        session.save()
        return "Could you please share your preferred time?"
 
    # 🔹 STEP 4 — Confirmation
    if session.stage == "confirming":

        confirm_words = [
            "yes", "yeah", "yup", "ok", "okay",
            "sure", "correct", "proceed",
            "confirm", "go ahead"
        ]

        cancel_words = [
            "no", "cancel", "change",
            "reschedule", "modify"
        ]

        msg_clean = msg.strip().lower()

        # confirmation
        if any(word in msg_clean for word in confirm_words):

            session.stage = "completed"
            session.state = {}
            session.save()

            return (
                "Your appointment has been scheduled successfully. "
                "We look forward to seeing you."
            )

        # cancellation / modification
        if any(word in msg_clean for word in cancel_words):

            session.stage = "collecting_date"
            session.save()

            return "No problem. Let's update the details. What new date would you prefer?"

        # unclear answer
        return "Please confirm by saying yes or no."
 
 
 
def qualification_strategy(agent, message, session):
 
    state = session.state or {}
    msg = message.lower()
 
    # 🔹 FIRST: Handle General Information Questions
    if any(word in msg for word in ["information", "about you", "services", "what do you have", "address", "office"]):
        return information_strategy(agent, message, session)
 
    # 🔹 SECOND: If user says no after suggestion → reset flow
    if msg in ["no", "not interested", "maybe later"]:
        session.stage = None
        session.state = {}
        session.save()
        return "No problem at all. Let me know if you'd like to explore other options or need any information."
 
    # 🔹 STEP 1 — Property Type
    if not state.get("property_type"):
        if session.stage == "collecting_property_type":
            state["property_type"] = message
            session.state = state
            session.stage = "collecting_location"
            session.save()
            return f"Nice choice. Which location are you considering?"
 
        session.stage = "collecting_property_type"
        session.save()
        return "Sure — are you looking for an apartment, villa, or commercial property?"
 
    # 🔹 STEP 2 — Location
    if not state.get("location"):
        if session.stage == "collecting_location":
            state["location"] = message
            session.state = state
            session.stage = "collecting_budget"
            session.save()
            return "Got it. What budget range are you comfortable with?"
 
        session.stage = "collecting_location"
        session.save()
        return "Which location do you have in mind?"
 
    # 🔹 STEP 3 — Budget
    if not state.get("budget"):
        if session.stage == "collecting_budget":
            state["budget"] = message
            session.state = state
            session.stage = "suggesting"
            session.save()
 
            query = f"{state['property_type']} in {state['location']} under {state['budget']}"
            context = retrieve_relevant_chunks(agent, query)
 
            if not context:
                return (
                    f"I’m not seeing an exact match for a {state['property_type']} "
                    f"in {state['location']} within {state['budget']}. "
                    "Would you like to adjust location or explore nearby areas?"
                )
 
            system_prompt = f"""
{agent.resolved_prompt}
 
Buyer Requirement:
Property Type: {state['property_type']}
Location: {state['location']}
Budget: {state['budget']}
 
Available Listings:
{context}
 
Respond naturally. Suggest best options.
Do NOT force site visit.
Offer it softly at the end.
"""
 
            return generate_response(system_prompt, message)
 
        session.stage = "collecting_budget"
        session.save()
        return "What is your approximate budget?"
 
    # 🔹 AFTER SUGGESTION — Only offer visit if user shows interest
    if any(word in msg for word in ["visit", "see property", "schedule", "book"]):
        session.stage = None
        session.save()
        return transaction_strategy(agent, message, session)
 
    return information_strategy(agent, message, session)
 

 
 
# def classify_medical_case(agent, message):
 
#     system_prompt = f"""
# You are a medical triage classifier.
 
# Hospital Specialty: {agent.company_name}
 
# Return JSON only in this format:
 
# {{
#   "severity": "emergency | urgent | mild | informational",
#   "domain_relevance": "in_scope | out_of_scope"
# }}
 
# Rules:
# - emergency = life-threatening symptoms (chest pain, breathing difficulty, unconsciousness, heavy bleeding)
# - urgent = needs doctor soon
# - mild = minor symptom
# - informational = service question
# """
 
#     response = generate_response(system_prompt, message)
 
#     import json
#     try:
#         return json.loads(response)
#     except:
#         return {
#             "severity": "informational",
#             "domain_relevance": "in_scope"
#         }
 
def classify_medical_case(agent, message):

    import json
    import re

    # 🔹 Prompt-injection guard (non-breaking)
    injection_patterns = [
        "ignore previous",
        "ignore instruction",
        "disregard previous",
        "override system",
        "forget instructions",
        "act as"
    ]

    msg_lower = message.lower()

    if any(p in msg_lower for p in injection_patterns):
        return {
            "severity": "informational",
            "domain_relevance": "in_scope"
        }

    system_prompt = f"""
You are a medical triage classifier.

Hospital Specialty: {agent.company_name}

Return JSON only in this format:

{{
  "severity": "emergency | urgent | mild | informational",
  "domain_relevance": "in_scope | out_of_scope"
}}

Rules:
- emergency = life-threatening symptoms (chest pain, breathing difficulty, unconsciousness, heavy bleeding)
- urgent = needs doctor soon
- mild = minor symptom
- informational = service question
"""

    # 🔹 Protect LLM call
    try:
        response = generate_response(system_prompt, message)
    except Exception:
        return {
            "severity": "informational",
            "domain_relevance": "in_scope"
        }

    # 🔹 Extract JSON safely (LLMs sometimes add text)
    try:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            raise ValueError("No JSON found")

    except Exception:
        return {
            "severity": "informational",
            "domain_relevance": "in_scope"
        }
 
# def support_strategy(agent, message, session):
 
#     case = classify_medical_case(agent, message)
 
#     severity = case.get("severity")
#     domain = case.get("domain_relevance")
 
#     # Emergency
#     if severity == "emergency":
#         return (
#             "⚠️ This may require urgent medical attention. "
#             "Please visit the emergency department or contact emergency services immediately."
#         )
 
#     # Out of scope
#     if domain == "out_of_scope":
#         return (
#             f"This concern appears outside the specialty of {agent.company_name}. "
#             "It would be best to consult the appropriate specialist or a general hospital."
#         )
 
#     # Urgent
#     if severity == "urgent":
#         return (
#             "This seems important and should be evaluated by a doctor soon. "
#             "Would you like me to help you book an appointment?"
#         )
 
#     # Mild
#     if severity == "mild":
#         return (
#             "This doesn’t sound urgent, but it’s still a good idea to consult a doctor if it continues. "
#             "Would you like assistance scheduling a visit?"
#         )
 
#     # Default → informational
#     return information_strategy(agent, message, session)


def support_strategy(agent, message, session):

    state = session.state or {}

    # -------------------------------
    # 1️⃣ Knowledge Base Check (NEW)
    # -------------------------------

    context = retrieve_relevant_chunks(agent, message)

    if context and context.strip():

        system_prompt = f"""
{agent.resolved_prompt}

You are a healthcare assistant for {agent.company_name}.

Knowledge Context:
{context}

User Question:
{message}

Instructions:
- Answer using the knowledge context.
- Respond naturally and professionally.
- Maximum 2–3 sentences.
- Do not mention "knowledge base".
"""

        return generate_response(system_prompt, message)

    system_prompt = f"""
You are a compassionate healthcare support assistant for {agent.company_name}.

Your role:
- Understand patient symptoms
- Provide helpful health guidance
- Suggest doctor consultation when needed

Safety rules:
- Never diagnose diseases
- Never prescribe medicines
- Only give general advice

Conversation memory:
{state}

User message:
{message}

Return JSON:

{{
 "symptoms": [],
 "response": ""
}}

Rules:
- Extract symptoms mentioned
- Use previous conversation context
- Respond naturally like a human healthcare assistant
- Keep response under 3 sentences
"""

    raw = generate_response(system_prompt, message)

    import json, re

    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(match.group())
    except:
        data = {"symptoms": [], "response": "Could you tell me more about your symptoms?"}

    # store symptoms in memory
    if data.get("symptoms"):
        previous = state.get("symptoms", [])
        state["symptoms"] = list(set(previous + data["symptoms"]))
        session.state = state
        session.save()

    return data.get("response")





def site_visit_transaction_strategy(agent, message, session):

    state = session.state or {}
    msg = message.lower()

    # Reset after completion
    if session.stage == "completed":
        if any(word in msg for word in ["thank", "thanks", "ok", "okay"]):
            return "You're most welcome. We look forward to seeing you at the property."
        session.stage = None
        session.state = {}
        session.save()
        return information_strategy(agent, message, session)

    # STEP 1 — Property Name (if not already known)
    if not state.get("property_name"):
        if session.stage == "collecting_property":
            state["property_name"] = message.strip()
            session.state = state
            session.stage = "collecting_name"
            session.save()
            return "Great. May I have your name for the visit booking?"

        session.stage = "collecting_property"
        session.save()
        return "Sure, which property would you like to schedule a site visit for?"

    # STEP 2 — Visitor Name
    if not state.get("visitor_name"):
        if session.stage == "collecting_name":
            state["visitor_name"] = message.strip()
            session.state = state
            session.stage = "collecting_date"
            session.save()
            return f"Thank you, {state['visitor_name']}. What date would be convenient for you?"

        session.stage = "collecting_name"
        session.save()
        return "May I have your name for the visit?"

    # STEP 3 — Visit Date
    if not state.get("visit_date"):
        if session.stage == "collecting_date":
            state["visit_date"] = message.strip()
            session.state = state
            session.stage = "collecting_time"
            session.save()
            return "And what time of the day works best for you?"

        session.stage = "collecting_date"
        session.save()
        return "Please share your preferred date for the visit."

    # STEP 4 — Visit Time
    if not state.get("visit_time"):
        if session.stage == "collecting_time":
            state["visit_time"] = message.strip()
            session.state = state
            session.stage = "confirming"
            session.save()

            return (
                f"Just to confirm — the site visit for {state['property_name']} "
                f"is scheduled on {state['visit_date']} at {state['visit_time']} "
                f"under the name {state['visitor_name']}. "
                "Shall I finalize this?"
            )

        session.stage = "collecting_time"
        session.save()
        return "What time would you prefer?"

    # STEP 5 — Confirmation
    if session.stage == "confirming":

        # if "yes" in msg:
        confirm_words = ["yes", "yeah", "yup", "ok", "okay", "sure", "correct", "proceed"]

        if any(word in msg for word in confirm_words):
            session.stage = "completed"
            session.state = {}
            session.save()
            return (
                "Perfect. Your site visit has been scheduled successfully. "
                "Our representative will meet you at the property entrance. "
                "If you need directions, feel free to let me know."
            )
        else:
            session.stage = "collecting_date"
            session.save()
            return "No problem. Let’s update it. Which new date works for you?"

    return information_strategy(agent, message, session)


def loan_financial_strategy(agent, message, session):

    msg = message.lower()

    # 🔹 Step 1 — Extract structured data safely
    extraction_prompt = f"""
Extract financial details from this message.

Return JSON only:
{{
  "monthly_income": number or null,
  "existing_emi": number or null,
  "loan_amount_requested": number or null,
  "tenure_years": number or null,
  "interest_rate": number or null
}}

Message: "{message}"
"""

    raw = generate_response(extraction_prompt, message)

    import json
    try:
        data = json.loads(raw)
    except:
        data = {}

    if not isinstance(data, dict):
        data = {}

    # 🔹 Safe numeric initialization
    income = float(data.get("monthly_income") or 0)
    existing_emi = float(data.get("existing_emi") or 0)
    loan_amount = float(data.get("loan_amount_requested") or 0)
    tenure_years = float(data.get("tenure_years") or 20)
    interest_rate = float(data.get("interest_rate") or 8.5)

    # 🔹 2️⃣ Eligibility Estimation Mode
    if income > 0:

        eligible_emi = (income * 0.5) - existing_emi

        monthly_rate = (interest_rate / 100) / 12
        tenure_months = tenure_years * 12

        if monthly_rate > 0:
            estimated_loan = (
                eligible_emi *
                ((1 + monthly_rate) ** tenure_months - 1) /
                (monthly_rate * (1 + monthly_rate) ** tenure_months)
            )
        else:
            estimated_loan = eligible_emi * tenure_months

        estimated_loan_lakh = round(estimated_loan / 100000, 1)

        explanation_prompt = f"""
You are a professional home loan advisor.

Monthly Income: ₹{income}
Existing EMI: ₹{existing_emi}
Estimated Loan Eligibility: ₹{estimated_loan_lakh} lakh

Rules:
- Keep answer under 4 sentences.
- No bullet points.
- Professional and human tone.
- Mention final approval depends on bank evaluation.
"""

        return generate_response(explanation_prompt, message)

    # 🔹 3️⃣ EMI Calculation Mode
    if loan_amount > 0:

        monthly_rate = (interest_rate / 100) / 12
        tenure_months = tenure_years * 12

        emi = (
            loan_amount *
            monthly_rate *
            (1 + monthly_rate) ** tenure_months
        ) / ((1 + monthly_rate) ** tenure_months - 1)

        emi_value = round(emi)

        explanation_prompt = f"""
You are a professional home loan advisor.

Loan Amount: ₹{loan_amount}
Interest Rate: {interest_rate}%
Tenure: {tenure_years} years
Calculated EMI: ₹{emi_value}

Rules:
- Keep response short (max 4 sentences).
- Explain clearly and professionally.
"""

        return generate_response(explanation_prompt, message)

    # 🔹 4️⃣ Otherwise → Knowledge Mode
    return information_strategy(agent, message, session)





def education_qualification_strategy(agent, message, session):

    state = session.state or {}
    msg = message.lower()

    # 🔹 Fallback for direct info queries
    if any(word in msg for word in ["fee", "eligibility", "deadline", "document"]):
        return information_strategy(agent, message, session)

    # 🔹 STEP 1 — Extract structured profile via AI (Fully dynamic)

    extraction_prompt = f"""
You are an academic advisor assistant.

Extract the student's career interest and education background.

Return JSON only:

{{
  "career_interest": "",
  "education_level": ""
}}

Rules:
- career_interest should reflect the field or domain (example: marketing, business, engineering, medicine, computer science)
- education_level must be one of: 12th, graduation, unknown
- If student mentions a degree (BBA, BCA etc), infer education_level = graduation
- If unclear, leave fields empty
"""

    profile_response = generate_response(extraction_prompt, message)

    import json, re

    try:
        match = re.search(r"\{.*\}", profile_response, re.DOTALL)
        profile = json.loads(match.group())
    except:
        profile = {
            "career_interest": "",
            "education_level": ""
        }

    # 🔹 Store extracted values
    if profile.get("career_interest"):
        state["interest"] = profile["career_interest"].lower().strip()

    if profile.get("education_level"):
        state["background"] = profile["education_level"]

    session.state = state
    session.save()

    # 🔹 If no interest yet → ask
    if not state.get("interest"):
        return "Which career field are you interested in?"

    # 🔹 STEP 2 — CHECK PROGRAM EXISTENCE (Scope Awareness)

    scope_prompt = f"""
Generate search keywords for university programs related to this field.

Field:
{state['interest']}

Return a short search query.
"""

    # scope_query = generate_response(scope_prompt, message)
    scope_query = generate_response(scope_prompt, message).strip().replace('"', '')

    scope_context = retrieve_relevant_chunks(agent, scope_query)

    if not scope_context or len(scope_context) < 30:
        return (
            "At the moment, we do not offer programs in that field. "
            "Would you like to explore the courses currently available at our university?"
        )

    # 🔹 Ask background if missing
    if not state.get("background"):
        return "May I know your highest qualification — 12th or graduation?"

    # 🔹 STEP 3 — Retrieve best matching course dynamically

    query_prompt = f"""
Generate a semantic search query to retrieve university programs.

Student Interest: {state['interest']}
Education Level: {state['background']}

Include:
- related courses
- specializations
- higher studies progression

Return a short search query.
"""

    # semantic_query = generate_response(query_prompt, message)
    semantic_query = generate_response(query_prompt, message).strip().replace('"', '')


    context = retrieve_relevant_chunks(agent, semantic_query)

    relevance_prompt = f"""
    Check whether the available programs match the student's interest.

    Student Interest:
    {state['interest']}

    Programs:
    {context}

    Return JSON:
    {{
    "relevant": true or false
    }}
    """

    # check = generate_response(relevance_prompt, message)
    relevant = True

    if context:
        check = generate_response(relevance_prompt, message)

        try:
            match = re.search(r"\{.*\}", check, re.DOTALL)
            data = json.loads(match.group())
            relevant = data.get("relevant", True)
        except:
            relevant = True


    try:
        match = re.search(r"\{.*\}", check, re.DOTALL)
        data = json.loads(match.group())
        relevant = data.get("relevant", True)
    except:
        relevant = True

    if not relevant:
        return (
            "At the moment, we do not offer programs directly related to that field. "
            "Would you like to explore the courses currently available at our university?"
        )

    if not context:
        return (
            "We offer programs in this area, but I’d like to guide you better. "
            "Would you prefer undergraduate or postgraduate options?"
        )

    # 🔹 STEP 4 — Controlled AI Suggestion

    system_prompt = f"""
{agent.resolved_prompt}

Student Career Interest: {state['interest']}
Student Education Level: {state['background']}

Available Programs:
{context}

Instructions:
- Identify programs most aligned with the student's interest.
- If a specialization exists (example: Marketing under MBA), mention it.
- Suggest maximum 2 programs.
- Only suggest programs explicitly mentioned in the Available Programs section.
- If no relevant program exists, say the university does not offer one.
- Keep the response under 3 sentences.
- Sound like a professional academic counselor.
"""

    return generate_response(system_prompt, message)



def education_scholarship_strategy(agent, message, session):

    if agent.company_name and agent.company_name.lower() not in message.lower():

        if any(word in message.lower() for word in ["university","college","institute"]):
            return (
                f"I provide scholarship guidance only for {agent.company_name}. "
                "If you have questions about its scholarship programs, I'd be happy to help."
            )

    # 🔹 STEP 1 — AI Scope Classification

    scope_prompt = """
You are a role boundary classifier.

Role: Scholarship Advisor.

Determine whether the user's message is related to ANY of the following:

- scholarship schemes
- fee waiver
- financial aid
- eligibility criteria
- percentage-based benefits
- income-based assistance
- sports scholarship
- scholarship application
- scholarship deadline
- scholarship verification process
- approval timeline
- result announcement

If the message is about scholarship-related policy, process, deadline, approval, or eligibility → return "in_scope".

If it is about courses, admissions, identity, hostel, placements, or general university information → return "out_of_scope".

Return JSON only:
{
  "scope": "in_scope" or "out_of_scope"
}
"""

    scope_response = generate_response(scope_prompt, message)

    import json, re

    try:
        match = re.search(r"\{.*\}", scope_response, re.DOTALL)
        scope_data = json.loads(match.group())
        scope = scope_data.get("scope", "out_of_scope")
    except:
        scope = "out_of_scope"

    # 🔹 STEP 2 — If Out of Scope → Respond Naturally via Role Prompt
    if scope == "out_of_scope":

        redirect_prompt = f"""
{agent.resolved_prompt}

The user question is outside scholarship scope.

Respond professionally:
- Clarify that you specialize in scholarships and financial aid.
- Suggest contacting relevant advisor for other queries.
- Maximum 2 sentences.
"""

        return generate_response(redirect_prompt, message)

    # 🔹 STEP 3 — Extract Percentage (Fully AI)

    extraction_prompt = """
Extract percentage marks if mentioned.

Return JSON:
{
  "percentage": ""
}
If not mentioned, return empty string.
"""

    profile_response = generate_response(extraction_prompt, message)

    try:
        match = re.search(r"\{.*\}", profile_response, re.DOTALL)
        profile = json.loads(match.group())
        percentage = profile.get("percentage", "")
    except:
        percentage = ""

    # 🔹 STEP 4 — RAG Retrieval

    if percentage:
        query = f"Scholarship eligibility for {percentage}%"
    else:
        query = "Scholarship policy and eligibility details"

    context = retrieve_relevant_chunks(agent, query)

    if not context:
        return "I currently do not have scholarship details available."

    # 🔹 STEP 5 — Controlled Response Generation

    system_prompt = f"""
{agent.resolved_prompt}

IMPORTANT RULE:
- The university name is {agent.company_name}.
- Never assume or adopt any other university name mentioned by the user.
- If the user mentions another institution, politely clarify you only provide information for {agent.company_name}.

User Message:
{message}

Relevant Scholarship Policy:
{context}

Instructions:
- Keep response under 3 sentences.
- If percentage provided, evaluate eligibility clearly.
- Do not guarantee approval.
- Sound supportive and professional.
"""

    return generate_response(system_prompt, message)




def education_support_strategy(agent, message, session):

    # 🔹 STEP 1 — AI Scope Classification

    scope_prompt = """
You are a role boundary classifier.

Role: Student Help Desk.

Determine if the message relates to:
- admission process
- application steps
- document submission
- login or portal issues
- payment issues
- application status
- technical support

If yes → "in_scope"
If about career advice, scholarships, or course selection → "out_of_scope"

Return JSON:
{
  "scope": "in_scope" or "out_of_scope"
}
"""

    scope_response = generate_response(scope_prompt, message)

    import json, re
    try:
        match = re.search(r"\{.*\}", scope_response, re.DOTALL)
        scope_data = json.loads(match.group())
        scope = scope_data.get("scope", "out_of_scope")
    except:
        scope = "out_of_scope"

    # 🔹 STEP 2 — Redirect if out of scope
    if scope == "out_of_scope":

        redirect_prompt = f"""
{agent.resolved_prompt}

The user message is outside your support role.

Respond politely:
- Clarify your role.
- Suggest connecting with appropriate advisor.
- Maximum 2 sentences.
"""

        return generate_response(redirect_prompt, message)

    # 🔹 STEP 3 — Retrieve support information

    context = retrieve_relevant_chunks(agent, message)

    if not context:
        return "I currently do not see specific details about that. Please contact the admissions office for further assistance."

    system_prompt = f"""
{agent.resolved_prompt}

User Query:
{message}

Relevant Information:
{context}

Instructions:
- Give a short and clear answer.
- Maximum 2–3 sentences.
- Keep response under 80 words.
- Summarize steps instead of listing all in detail.
- Sound natural and helpful.
- Avoid numbered lists unless absolutely necessary.
"""

    return generate_response(system_prompt, message)


###############################################################################33

def hotel_booking_strategy(agent, message, session):

    import re
    from dateparser.search import search_dates

    msg = message.lower().strip()
    state = session.state or {}

    # ===============================
    # 1️⃣ Start Booking
    # ===============================
    if any(word in msg for word in ["book", "reservation", "reserve"]):
        session.stage = "ask_checkin"
        session.state = {}
        session.save()
        return "Sure. What is your check-in date?"

    # ===============================
    # 2️⃣ Ask Check-in
    # ===============================
    if session.stage == "ask_checkin":

        parsed = search_dates(message)
        if parsed:
            state["check_in"] = parsed[0][1].strftime("%d %B")
            session.stage = "ask_checkout"
            session.state = state
            session.save()
            return "And your check-out date?"

        return "Please tell me your check-in date."

    # ===============================
    # 3️⃣ Ask Check-out
    # ===============================
    if session.stage == "ask_checkout":

        parsed = search_dates(message)
        if parsed:
            state["check_out"] = parsed[0][1].strftime("%d %B")
            session.stage = "ask_guests"
            session.state = state
            session.save()
            return "How many guests will be staying?"

        return "Please tell me your check-out date."

    # ===============================
    # 4️⃣ Ask Guests
    # ===============================
    if session.stage == "ask_guests":

        match = re.search(r"\d+", msg)
        if match:
            state["guests"] = match.group()
            session.stage = "ask_room"
            session.state = state
            session.save()
            return "Do you have a preferred room type?"

        return "How many guests will be staying?"

    # ===============================
    # 5️⃣ Ask Room Type
    # ===============================
    if session.stage == "ask_room":

        state["room_type"] = message.strip()
        session.stage = "ask_name"
        session.state = state
        session.save()
        return "May I have your name for the booking?"

    # ===============================
    # 6️⃣ Ask Name
    # ===============================
    if session.stage == "ask_name":

        state["name"] = message.strip()
        session.stage = "confirming"
        session.state = state
        session.save()

        return (
            f"Just to confirm — {state['room_type']} from "
            f"{state['check_in']} to {state['check_out']} "
            f"for {state['guests']} guest(s) under {state['name']}. "
            f"Should I confirm it?"
        )

    # ===============================
    # 7️⃣ Confirmation
    # ===============================
    if session.stage == "confirming":

        if any(word in msg for word in [
            "yes", "confirm", "sure", "okay", "ok", "go ahead"
        ]):
            session.stage = "completed"
            session.state = {}
            session.save()
            return "Perfect. Your booking is confirmed."

        session.stage = None
        session.state = {}
        session.save()
        return "No problem. Let's start again whenever you're ready."

    # ===============================
    # 8️⃣ Fallback → Information
    # ===============================
    return information_strategy(agent, message, session)


def restaurant_booking_strategy(agent, message, session):

    import re
    import json
    from dateparser.search import search_dates
    from knowledge.services.retriever import retrieve_relevant_chunks
    from conversations.services.azure_openai_service import generate_response

    msg = message.lower().strip()
    state = session.state or {}

    # =========================================================
    # 1️⃣ COMPLETED STATE
    # =========================================================
    if session.stage == "completed":
        if any(word in msg for word in ["thank", "thanks"]):
            return "You're most welcome. We look forward to serving you."
        session.stage = None
        session.state = {}
        session.save()
        return information_strategy(agent, message, session)

    # =========================================================
    # 2️⃣ CONFIRMATION STAGE
    # =========================================================
    if session.stage == "confirming":

        if any(word in msg for word in [
            "yes", "confirm", "sure", "okay", "ok", "go ahead"
        ]):
            session.stage = "completed"
            session.state = {}
            session.save()

            confirm_prompt = """
You are a warm and professional restaurant assistant.

Confirm the reservation in a friendly, welcoming tone.
Keep it under 2 sentences.
"""
            return generate_response(confirm_prompt, message)

        session.stage = None
        session.state = {}
        session.save()
        return "No worries at all. Let me know whenever you'd like to reserve a table."

    # =========================================================
    # 3️⃣ KNOWLEDGE / INFORMATION HANDLING (RAG)
    # =========================================================
    knowledge_context = retrieve_relevant_chunks(agent, message)

    info_keywords = [
        "menu", "timing", "hours", "open", "close",
        "parking", "address", "policy", "cuisine"
    ]

    if knowledge_context and any(word in msg for word in info_keywords):

        info_prompt = f"""
You are a helpful and friendly restaurant assistant.

Knowledge:
{knowledge_context}

Respond naturally in 2-3 sentences.
Do not sound robotic.
"""

        info_reply = generate_response(info_prompt, message)

        # Resume booking if in progress
        if session.stage:
            next_question = get_next_restaurant_question(session.stage)
            if next_question:
                return f"{info_reply}\n\nBy the way, {next_question}"

        return info_reply

    # =========================================================
    # 4️⃣ START BOOKING INTENT
    # =========================================================
    if any(word in msg for word in ["book", "reserve", "reservation", "table"]):
        session.stage = "ask_date"
        session.state = {}
        session.save()

        start_prompt = """
You are a friendly restaurant reservation assistant.

Ask the guest for their preferred reservation date.
Keep it short and welcoming.
"""
        return generate_response(start_prompt, message)

    # =========================================================
    # 5️⃣ STAGE-BASED FLOW
    # =========================================================

    # ---- ASK DATE
    if session.stage == "ask_date":

        parsed = search_dates(message)
        if parsed:
            state["date"] = parsed[0][1].strftime("%d %B")
            session.stage = "ask_time"
            session.state = state
            session.save()

            time_prompt = """
Politely ask for the preferred reservation time.
Sound natural.
"""
            return generate_response(time_prompt, message)

        return "Could you please share the reservation date?"

    # ---- ASK TIME
    if session.stage == "ask_time":

        time_match = re.search(r"\b(\d{1,2}(:\d{2})?\s?(am|pm)?)\b", msg)
        if time_match:
            state["time"] = time_match.group(1)
            session.stage = "ask_guests"
            session.state = state
            session.save()

            guest_prompt = """
Ask how many guests will be dining.
Be friendly and concise.
"""
            return generate_response(guest_prompt, message)

        return "What time should I reserve the table for?"

    # ---- ASK GUESTS
    if session.stage == "ask_guests":

        guest_match = re.search(r"\d+", msg)
        if guest_match:
            state["guests"] = guest_match.group()
            session.stage = "ask_name"
            session.state = state
            session.save()

            name_prompt = """
Politely ask for the guest's name for the reservation.
Keep it short.
"""
            return generate_response(name_prompt, message)

        return "How many guests will be joining?"

    # ---- ASK NAME
    if session.stage == "ask_name":

        state["name"] = message.strip()
        session.stage = "confirming"
        session.state = state
        session.save()

        confirm_prompt = f"""
You are a professional restaurant assistant.

Summarize the reservation naturally:

Date: {state['date']}
Time: {state['time']}
Guests: {state['guests']}
Name: {state['name']}

Ask politely if you should confirm it.
Keep it warm and under 2 sentences.
"""
        return generate_response(confirm_prompt, message)

    # =========================================================
    # 6️⃣ DEFAULT FALLBACK
    # =========================================================
    if knowledge_context:
        fallback_prompt = f"""
You are a helpful restaurant assistant.

Knowledge:
{knowledge_context}

Respond naturally and briefly.
"""
        return generate_response(fallback_prompt, message)

    return "How may I assist you today?"


def get_next_restaurant_question(stage):

    mapping = {
        "ask_date": "what date would you like to reserve?",
        "ask_time": "what time works best for you?",
        "ask_guests": "how many guests will be joining?",
        "ask_name": "may I have your name for the reservation?",
        "confirming": "shall I confirm the reservation?"
    }

    return mapping.get(stage, "")

def travel_planner_strategy(agent, message, session):

    import json, re
    from knowledge.services.retriever import retrieve_relevant_chunks
    from conversations.services.azure_openai_service import generate_response

    msg = message.lower().strip()
    state = session.state or {}

    # =========================================================
    # 1️⃣ ALWAYS CHECK KNOWLEDGE FIRST (RAG PRIORITY)
    # =========================================================

    context = retrieve_relevant_chunks(agent, message)

    if context.strip():
        system_prompt = f"""
{agent.resolved_prompt}

Relevant Information:
{context}

Instructions:
- Answer directly from the knowledge context.
- Keep response under 3 sentences.
- Be natural and conversational.
- Do NOT invent information.
"""
        return generate_response(system_prompt, message)

    # =========================================================
    # 2️⃣ IDENTITY / META QUESTIONS
    # =========================================================

    meta_keywords = [
        "who are you",
        "about you",
        "what services",
        "how can you help",
        "contact",
        "address",
        "phone",
        "email"
    ]

    if any(word in msg for word in meta_keywords):
        return information_strategy(agent, message, session)

    # =========================================================
    # 3️⃣ ADVISORY EXTRACTION (ONLY IF NOT KNOWLEDGE)
    # =========================================================

    extraction_prompt = f"""
Extract travel planning details.

Return JSON:
{{
  "destination": "",
  "travel_dates": "",
  "budget": "",
  "travel_type": "",
  "duration": ""
}}

Message: "{message}"
"""

    raw = generate_response(extraction_prompt, message)

    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        extracted = json.loads(match.group())
    except:
        extracted = {}

    for key, value in extracted.items():
        if value:
            state[key] = value

    session.state = state
    session.save()

    # =========================================================
    # 4️⃣ CLARIFICATION
    # =========================================================

    if not state.get("destination"):
        return "Sure. Which destination are you planning to visit?"

    if not state.get("travel_dates"):
        return "When are you planning to travel?"

    # =========================================================
    # 5️⃣ SUGGEST PACKAGE
    # =========================================================

    query = f"""
Travel package for {state.get('destination')}
Duration: {state.get('duration','')}
Budget: {state.get('budget','')}
Travel type: {state.get('travel_type','')}
"""

    package_context = retrieve_relevant_chunks(agent, query)

    if not package_context.strip():
        return (
            "I don’t see an exact match for that combination. "
            "Would you like to explore available options for that destination?"
        )

    system_prompt = f"""
You are a professional travel consultant at {agent.company_name}.

Traveler Preferences:
{state}

Available Package:
{package_context}

Instructions:
- Recommend the most relevant package.
- Keep response under 3 sentences.
- Be natural and helpful.
- End with one short follow-up question.
"""

    return generate_response(system_prompt, message)






def recruitment_advisory_strategy(agent, message, session):

    import json, re
    from knowledge.services.retriever import retrieve_relevant_chunks
    from conversations.services.azure_openai_service import generate_response

    msg = message.lower().strip()
    state = session.state or {}


    if "screening_stage" not in state:
        state["screening_stage"] = "intro"

    if "screening_turns" not in state:
        state["screening_turns"] = 0

    state["screening_turns"] += 1
    session.state = state
    session.save()
    # =========================================================
    # 0️⃣ IDENTITY QUESTIONS
    # =========================================================

    if any(q in msg for q in ["company name", "who are you", "about company"]):
        return information_strategy(agent, message, session)

    # =========================================================
    # 1️⃣ STRICT ROLE LOCK (TOP PRIORITY)
    # =========================================================

    if state.get("active_role"):


        # If already closed → stop responding further
        if state.get("screening_stage") == "closed":
            return "Thank you for your time. Our team will connect if shortlisted."

        # 🔴 TERMINATION CHECK FIRST (before incrementing)
        if state.get("screening_turns", 0) >= 4:

            state["screening_stage"] = "closed"
            session.state = state
            session.save()

            closing_prompt = f"""
    You are an HR Recruiter at {agent.company_name}.

    Politely conclude the screening conversation.

    Instructions:
    - Thank the candidate for sharing details.
    - Mention that the profile will be reviewed internally.
    - Do NOT guarantee selection.
    - Do NOT sound robotic.
    - Keep under 3 sentences.
    - End conversation professionally.
    """

            return generate_response(closing_prompt, message)

    # 🔹 If not terminating → continue screening

        continuity_prompt = f"""
You are an HR Recruiter at {agent.company_name}.

Active Role: {state['active_role']}
Previous Context: Candidate is being evaluated for this role.

Candidate Message: "{message}"

Instructions:
- Assume this is a continuation of the same role discussion.
- Stay strictly focused on the Active Role.
- If candidate mentions projects, relate them to required skills.
- If unclear, ask clarification question.
- Do NOT mention other job roles.
- Do NOT retrieve new roles.
- Do NOT suggest resume submission yet.
- Keep response under 3 sentences.
- Maintain natural recruiter tone.
"""

        return generate_response(continuity_prompt, message)

    # =========================================================
    # 2️⃣ INITIAL DISCOVERY
    # =========================================================

    job_context = retrieve_relevant_chunks(agent, message)

    if not job_context or not job_context.strip():
        return "Could you share which role or technology you're interested in?"

    # Extract detected role
    role_extract_prompt = f"""
From the job description below, extract the exact job title.

Return JSON:
{{ "role": "" }}

Job Description:
{job_context}
"""

    raw_role = generate_response(role_extract_prompt, job_context)

    detected_role = None

    try:
        match = re.search(r"\{.*\}", raw_role, re.DOTALL)
        role_data = json.loads(match.group())
        detected_role = role_data.get("role")
    except:
        pass

    if detected_role:
        state["active_role"] = detected_role
        state["screening_turns"] = 0
        state["screening_stage"] = "screening"
        session.state = state
        session.save()

    # Initial human response
    system_prompt = f"""
You are an HR Recruiter at {agent.company_name}.

Job Information:
{job_context}

Instructions:
- Introduce the relevant role naturally.
- Do NOT list unrelated roles.
- Do NOT push resume submission.
- Keep response under 3 sentences.
- Sound professional and conversational.
"""

    return generate_response(system_prompt, message)



def hr_helpdesk_strategy(agent, message, session):

    from knowledge.services.retriever import retrieve_relevant_chunks
    from conversations.services.azure_openai_service import generate_response
    import json, re

    state = session.state or {}
    msg = message.lower().strip()

    # =========================================================
    # 1️⃣ AI-Based Identity Detection
    # =========================================================

    classification_prompt = f"""
Classify the message.

Return JSON:
{{
  "type": "identity" OR "policy_query"
}}

Message: "{message}"
"""

    raw = generate_response(classification_prompt, message)

    msg_type = "policy_query"

    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(match.group())
        msg_type = data.get("type", "policy_query")
    except:
        pass

    if msg_type == "identity":
        return information_strategy(agent, message, session)

    # =========================================================
    # 2️⃣ Retrieve HR Policy Context
    # =========================================================

    context = retrieve_relevant_chunks(agent, message)

    if not context or not context.strip():
        return (
            "This information is not mentioned in the official HR policy documents. "
            "Please contact the HR department for further clarification."
        )

    # =========================================================
    # 3️⃣ Generate Professional Response
    # =========================================================

    final_prompt = f"""
You are an HR Helpdesk Assistant at {agent.company_name}.

Relevant HR Policy Information:
{context}

Employee Question:
"{message}"

Instructions:
- Answer clearly and professionally.
- Use only the provided HR policy information.
- Do not interpret beyond policy.
- Do not guarantee approvals.
- Keep response between 2–4 sentences.
- End with a natural professional closing offering assistance.
- Do not repeat the question.
- Do not use markdown or bullet formatting.
- Maintain supportive and neutral tone.
"""

    return generate_response(final_prompt, message)




def onboarding_support_strategy(agent, message, session):

    from knowledge.services.retriever import retrieve_relevant_chunks
    from conversations.services.azure_openai_service import generate_response
    import json, re

    state = session.state or {}
    msg = message.lower().strip()

    # =========================================================
    # 1️⃣ Identity Handling (AI-based)
    # =========================================================

    classification_prompt = f"""
Classify the message.

Return JSON:
{{
  "type": "identity" OR "onboarding_query"
}}

Message: "{message}"
"""

    raw = generate_response(classification_prompt, message)

    msg_type = "onboarding_query"

    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(match.group())
        msg_type = data.get("type", "onboarding_query")
    except:
        pass

    if msg_type == "identity":
        return information_strategy(agent, message, session)

    # =========================================================
    # 2️⃣ Retrieve Onboarding Context
    # =========================================================

    context = retrieve_relevant_chunks(agent, message)

    if not context or not context.strip():
        return (
            "I currently do not see specific onboarding details related to that. "
            "Please contact the HR team for further clarification."
        )

    # =========================================================
    # 3️⃣ Generate Professional Humanized Response
    # =========================================================

    system_prompt = f"""
You are an Onboarding Assistant at {agent.company_name}.

Relevant Onboarding Information:
{context}

Candidate Question:
"{message}"

Instructions:
- Answer clearly and professionally.
- Use only the provided onboarding information.
- Do not interpret beyond policy.
- Do not guarantee joining confirmation or approvals.
- Keep response between 2–4 sentences.
- Maintain welcoming and supportive tone.
- End with a natural offer of assistance.
- Do not use bullet points or markdown formatting.
"""

    return generate_response(system_prompt, message)




def customer_support_strategy(agent, message, session):

    context = retrieve_relevant_chunks(agent, message) or ""
    state = session.state or {}

    system_prompt = f"""
{agent.resolved_prompt}

Conversation memory:
{state}

Customer message:
{message}

Customer Support Knowledge Context:
{context}

Instructions:
- Your role is to provide guidance and suggestions.
- Do NOT request personal information such as email, phone number, account ID, or order number.
- Explain processes clearly so the customer can complete them themselves.
- If the customer says "yes", "ok", or similar confirmations, continue explaining the process.
- Prefer information from the knowledge base.
- If the knowledge base does not contain the exact answer, give general customer support guidance.
- Keep responses concise (2–3 sentences).
"""

    reply = generate_response(system_prompt, message)

    # store conversation topic
    session.state = {
        "topic": state.get("topic", message)
    }
    session.save()

    return reply



def complaint_handler_strategy(agent, message, session):

    import json
    import re

    state = session.state or {}

    # -----------------------------
    # 1️⃣ Knowledge-first routing
    # -----------------------------

    context = retrieve_relevant_chunks(agent, message)

    if context:
        system_prompt = f"""
    {agent.resolved_prompt}

    User question:
    {message}

    Knowledge context:
    {context}

    Instructions:
    - Answer the user question using the knowledge context.
    - Keep response clear and professional.
    - Maximum 2–3 sentences.
    """

        return generate_response(system_prompt, message)

    # -----------------------------
    # 🔹 AI Classification (Process vs Complaint)
    # -----------------------------

    classification_prompt = f"""
Classify the user's message.

Return JSON only:

{{
"type": "process_question" OR "information_question" OR "actual_complaint"
}}

Definitions:
process_question → asking how to start or file a complaint
information_question → asking about complaint policies, timelines, escalation, or procedures
actual_complaint → reporting a problem with a product or service

Examples:
"How do I file a complaint?" → process_question
"What is the complaint process?" → process_question
"How do you handle complaints?" → information_question
"How long does complaint investigation take?" → information_question
"My order arrived damaged" → actual_complaint
"I received a broken item" → actual_complaint

Message: "{message}"
"""

    raw_classification = generate_response(classification_prompt, message)

    try:
        match = re.search(r"\{.*\}", raw_classification, re.DOTALL)
        data = json.loads(match.group())
        msg_type = data.get("type")
    except:
        msg_type = "actual_complaint"





    # -----------------------------
    # 🔹 Process question handling
    # -----------------------------

    if msg_type == "process_question":

        context = retrieve_relevant_chunks(agent, message) or ""

        system_prompt = f"""
{agent.resolved_prompt}

User Question:
{message}

Knowledge Context:
{context}

Instructions:
- Explain how a customer can file a complaint.
- Use knowledge context if available.
- If knowledge does not contain the process, explain generally.
- Keep response short and helpful.
- Maximum 2–3 sentences.
"""

        return generate_response(system_prompt, message)


    # -----------------------------
    # 3️⃣ INFORMATION QUESTION  ← ADD YOUR CODE HERE
    # -----------------------------

    if msg_type == "information_question":

        context = retrieve_relevant_chunks(agent, message) or ""

        system_prompt = f"""
{agent.resolved_prompt}

User Question:
{message}

Knowledge Context:
{context}

Instructions:
- Answer using the knowledge context if relevant.
- If knowledge is incomplete, answer generally using customer support best practices.
- Keep response clear and professional.
- Maximum 2–3 sentences.
"""

        return generate_response(system_prompt, message)


    # -----------------------------
    # 1️⃣ Extract structured info
    # -----------------------------

    extraction_prompt = f"""
Extract complaint details from the message.

Return JSON only:

{{
"order_number": "",
"product_name": "",
"issue_description": ""
}}

Message: "{message}"

Rules:
- Extract only if explicitly mentioned.
- Do not guess or infer.
- If not present return empty string.
"""

    raw = generate_response(extraction_prompt, message)

    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        extracted = json.loads(match.group())
    except:
        extracted = {}

    for k, v in extracted.items():
        if v:
            state[k] = v

    session.state = state
    session.save()


    # -----------------------------
    # 2️⃣ Determine missing info
    # -----------------------------

    missing_fields = []

    if not state.get("order_number"):
        missing_fields.append("order_number")

    if not state.get("product_name"):
        missing_fields.append("product_name")

    if not state.get("issue_description"):
        missing_fields.append("issue_description")


    # -----------------------------
    # 3️⃣ Ask next question
    # -----------------------------

    if missing_fields:

        next_prompt = f"""
You are a professional complaint handler.

Conversation memory:
{state}

Customer message:
{message}

Missing information:
{missing_fields}

Instructions:
- Ask ONLY for the most important missing detail.
- Do not repeat previously collected information.
- If the user message does not answer the previous question, politely ask again.
- Keep response under 25 words.
- Be empathetic and professional.
"""

        return generate_response(next_prompt, message)


    # -----------------------------
    # 4️⃣ Investigation response
    # -----------------------------

    context = retrieve_relevant_chunks(agent, message) or ""

    final_prompt = f"""
{agent.resolved_prompt}

Complaint details:
{state}

Knowledge context:
{context}

Instructions:
- Acknowledge the complaint professionally.
- Explain that the issue will be investigated.
- Mention typical resolution timeline if available.
- Keep response under 40 words.
"""

    return generate_response(final_prompt, message)










def returns_refund_strategy(agent, message, session):

    import json
    import re

    state = session.state or {}

    # 1️⃣ Retrieve knowledge from uploaded files
    context = retrieve_relevant_chunks(agent, message) or ""

    # 2️⃣ Extract structured information from message
    extraction_prompt = f"""
Extract return/refund related information from the message.

Return JSON only:

{{
"order_number": "",
"product_name": "",
"reason": ""
}}

Message: "{message}"

Rules:
- Extract only if clearly mentioned
- Do not guess
- If not present return empty string
"""

    raw = generate_response(extraction_prompt, message)

    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        extracted = json.loads(match.group())
    except:
        extracted = {}

    # Save extracted fields into session memory
    for k, v in extracted.items():
        if v:
            state[k] = v

    session.state = state
    session.save()

    # 3️⃣ Determine missing information dynamically
    missing_fields = []

    if not state.get("order_number"):
        missing_fields.append("order_number")

    if not state.get("product_name"):
        missing_fields.append("product_name")

    if not state.get("reason"):
        missing_fields.append("reason")

    # 4️⃣ If information missing → ask next question
    if missing_fields:

        ask_prompt = f"""
You are a professional returns and refund support agent.

Conversation memory:
{state}

Customer message:
{message}

Return policy context:
{context}

Missing information:
{missing_fields}

Instructions:
- Ask ONLY for the most important missing detail.
- Do not repeat previously collected information.
- Be polite and helpful.
- Maximum 20 words.
"""

        return generate_response(ask_prompt, message)

    # 5️⃣ When enough info collected → provide resolution
    final_prompt = f"""
{agent.resolved_prompt}

Customer return request details:
{state}

Return / Refund Policy Context:
{context}

Instructions:
- Confirm the return/refund request.
- Explain next steps according to company policy.
- Mention refund processing timeline if available.
- Do not invent policies.
- Maximum 40 words.
"""

    return generate_response(final_prompt, message)



def escalation_manager_strategy(agent, message, session):

    import re

    # -----------------------------------------
    # Initialize session memory
    # -----------------------------------------

    if session.state is None:
        session.state = {}

    state = session.state

    # Conversation memory
    history = state.get("conversation_history", [])

    history.append({"role": "user", "content": message})

    # keep last 6 messages
    history = history[-6:]

    state["conversation_history"] = history

    conversation_context = "\n".join(
        [f"{h['role']}: {h['content']}" for h in history]
    )

    session.state = state
    session.save()

    # -----------------------------------------
    # Retrieve knowledge context
    # -----------------------------------------

    context = retrieve_relevant_chunks(agent, message)

    # -----------------------------------------
    # If KB contains answer → respond with AI
    # -----------------------------------------

    if context:

        prompt = f"""
You are {agent.name}, the Escalation Manager at {agent.company_name}.

Knowledge Base:
{context}

Conversation History:
{conversation_context}

User Message:
{message}

Instructions:
- Answer using the knowledge base.
- Do not repeat questions already answered.
- Ask only one question at a time if additional details are required.
- Be professional and concise.
"""

        reply = generate_response(agent.resolved_prompt, prompt)

        history.append({"role": "assistant", "content": reply})
        state["conversation_history"] = history
        session.state = state
        session.save()

        return reply

    # -----------------------------------------
    # Escalation Information Collection Flow
    # -----------------------------------------

    msg = message.strip()

    state.setdefault("issue_description", None)
    state.setdefault("customer_name", None)
    state.setdefault("contact_number", None)
    state.setdefault("order_number", None)
    state.setdefault("asked_fields", [])

    # Store answers based on previous question

    if state["asked_fields"]:

        last_question = state["asked_fields"][-1]

        if last_question == "issue_description" and not state["issue_description"]:
            state["issue_description"] = msg

        elif last_question == "customer_name" and not state["customer_name"]:
            state["customer_name"] = msg

        elif last_question == "contact_number" and not state["contact_number"]:
            if re.search(r"\d{8,15}", msg):
                state["contact_number"] = msg

        elif last_question == "order_number" and not state["order_number"]:
            state["order_number"] = msg

    session.state = state
    session.save()

    # -----------------------------------------
    # Ask next missing detail
    # -----------------------------------------

    if not state["issue_description"]:

        state["asked_fields"].append("issue_description")
        session.save()

        reply = "I'm sorry you're experiencing an issue. Could you briefly describe the problem?"

    elif not state["customer_name"]:

        state["asked_fields"].append("customer_name")
        session.save()

        reply = "Thank you for explaining the issue. May I have your name?"

    elif not state["contact_number"]:

        state["asked_fields"].append("contact_number")
        session.save()

        reply = "Could you please provide a contact number so our escalation manager can reach you?"

    elif not state["order_number"]:

        state["asked_fields"].append("order_number")
        session.save()

        reply = "If this issue relates to an order, please provide the order number or type 'none'."

    else:

        reply = (
            "Thank you for providing the details. "
            "Your issue has been escalated to our escalation team. "
            "A support manager will review the case and contact you shortly."
        )

    # -----------------------------------------
    # Save assistant response in memory
    # -----------------------------------------

    history.append({"role": "assistant", "content": reply})

    state["conversation_history"] = history

    session.state = state
    session.save()

    return reply


def insurance_transaction_strategy(agent, message, session):

    def clean_for_voice(text):
        text = re.sub(r"\b\d+\.\s*", "", text)  # remove 1. 2. 3.

        # Convert "3-5 L" → "3 to 5 lakh"
        text = re.sub(r"(\d+)\s*-\s*(\d+)\s*L\b", r"\1 to \2 lakh", text)

        # Convert "5 L" → "5 lakh"
        text = re.sub(r"(\d+)\s*L\b", r"\1 lakh", text)
        # Convert "2-3 Cr" → "2 to 3 crore"
        text = re.sub(r"(\d+)\s*-\s*(\d+)\s*Cr\b", r"\1 to \2 crore", text)

        # Convert "5 Cr" → "5 crore"
        text = re.sub(r"(\d+)\s*Cr\b", r"\1 crore", text)

        text = text.replace("\n", ". ")         # better voice pause
        return text.strip()

    from conversations.services.core.strategies import information_strategy

    state = session.state or {}
    msg = message.lower().strip()

    def humanize(agent, user_message, instruction, stage=None):

        from conversations.services.azure_openai_service import generate_response

        context = ""

        system_prompt = f"""
    {agent.resolved_prompt}

    You are an Insurance Advisor at {agent.company_name}.

    Current Conversation Stage: {stage}

    Knowledge Context:
    {context}

    Instruction:
    {instruction}

    STRICT RULES:
    - ONLY respond to the CURRENT STAGE
    - DO NOT restart conversation
    - DO NOT suggest other insurance types
    - DO NOT ask unrelated questions
    - DO NOT go back to menu
    - DO NOT assume new intent
    - Stay within the current step
    - DO NOT use numbered lists (1, 2, 3)
    - Use simple sentences or comma-separated options
    - Keep it natural for voice conversation
    

    DO NOT:
    - change flow
    - ask new questions
    - suggest other insurance
    - interpret user intent

    Response Style:
    - Short and natural
    - Show options clearly if needed
    """

        return generate_response(system_prompt, user_message)

    

    # =====================================================
    # 🔹 INSURANCE INFORMATION REQUEST DETECTION (NEW)
    # =====================================================

    info_request_words = [
        "know", "information", "info", "details",
        "explain", "tell me about", "about",
        "what is", "how does", "guide"
    ]

    flow_request_words = [
        "want", "need", "buy", "get", "apply",
        "purchase", "take", "start"
    ]

    insurance_keywords = [
        "health insurance",
        "car insurance",
        "vehicle insurance",
        "term insurance",
        "life insurance"
    ]

    # If user asking for insurance knowledge (not buying)
    if any(word in msg for word in info_request_words) and any(ins in msg for ins in insurance_keywords):

        return information_strategy(agent, message, session)


    # =====================================================
    # 🔹 DOCUMENT KNOWLEDGE MODE (NEW ADDITION)
    # =====================================================

    document_intent_keywords = [
        "what information",
        "which information",
        "kind of information",
        "what kind of information",
        "which information do you have",
        "which kind of information",
        "what do you know",
        "what do you have",
        "what services",
        "what policies",
        "summarize",
        "summarize the document",
        "give me summary",
        "summary",
        "explain",
        "details",
        "tell me about",
        "about the policy",
        "policy information"
    ]

    if any(keyword in msg for keyword in document_intent_keywords):

        # If user asked while inside flow
        if session.stage and session.stage != "insurance_menu":
            answer = information_strategy(agent, message, session)
            return f"{answer}\n\nWould you like to continue where we left off?"
        
        return information_strategy(agent, message, session)

    # =====================================================
    # 🔹 FLOW INTERRUPTION HANDLER (NEW ADDITION)
    # =====================================================

    insurance_knowledge_keywords = [
        "coverage", "premium", "waiting", "claim",
        "benefit", "exclusion", "hospital",
        "cashless", "document", "renewal",
        "maternity", "network", "process"
    ]

    # If inside any active flow stage and user asks knowledge question
    active_flow_stages = [
        "health_member_type", "health_age", "health_cover",
        "term_cover_for", "term_age",
        "car_requirement",
        "insurance_lead_capture"
    ]

    if session.stage in active_flow_stages and len(msg.split()) > 2:
        if any(word in msg for word in insurance_knowledge_keywords):

            answer = information_strategy(agent, message, session)

            return (
                f"{answer}\n\n"
                "Shall we continue where we left off?"
            )

    # =====================================================
    # HANDLE CONFIRM SWITCH FIRST
    # =====================================================

    if session.stage == "confirm_switch":

        switch_to = state.get("switch_to")
        previous_stage = state.get("previous_stage")

        if "yes" in msg or msg == "y":
            session.state = {"product": switch_to}
            session.stage = None
            session.save()
            return insurance_transaction_strategy(agent, switch_to, session)

        elif "no" in msg or msg == "n":
            session.stage = previous_stage
            session.save()
            response = humanize(agent, message, "Tell user we will continue with current insurance selection.")
            return clean_for_voice(response)

        else:
            response = humanize(agent, message, "Ask user to reply with Yes or No.")
            return clean_for_voice(response)

    # =====================================================
    # DETECT PRODUCT FROM MESSAGE
    # =====================================================

    detected_product = None

    if any(word in msg for word in ["car", "vehicle", "renew", "new car"]):
        detected_product = "car"

    elif any(word in msg for word in ["health", "medical", "hospital"]):
        detected_product = "health"

    elif any(word in msg for word in ["term", "life insurance", "life cover"]):
        detected_product = "term"

    current_product = state.get("product")

    # 🚨 HARD FLOW LOCK (PREVENT RESET)
    if current_product and session.stage:
        detected_product = current_product

    # Mid-flow switch detection
    if detected_product and current_product and detected_product != current_product:
        state["switch_to"] = detected_product
        state["previous_stage"] = session.stage
        session.state = state
        session.stage = "confirm_switch"
        session.save()

        return (
            f"You're currently in {current_product.capitalize()} Insurance flow.\n\n"
            f"Would you like to switch to {detected_product.capitalize()} Insurance? (Yes/No)"
        )
    
    # HARD LOCK (ONLY WHEN FLOW STARTED)
    if current_product and session.stage:
        detected_product = current_product

    # =====================================================
    # HANDLE GREETING → DIRECT PRODUCT (FIX LOOP)
    # =====================================================

    if not state.get("product") and detected_product:
        session.stage = None  # reset cleanly before starting flow

    # =====================================================
    # SMART INITIAL ENTRY
    # =====================================================

    if not state.get("product") :

        # 🚨 HARD FLOW LOCK (PREVENT RESET)
        if current_product and session.stage:
            detected_product = current_product

        if detected_product == "car":
            session.stage = "car_requirement"
            session.state = {"product": "car"}
            session.save()

            response = humanize(agent, message,
                "Ask what user needs: New Car Insurance, Renewal, or Claim Assistance."
            )
            return clean_for_voice(response)
        
        elif detected_product == "health":

            # Smart member detection from first message
            member_type = None

            if "family" in msg:
                member_type = "Family"
            elif "parents" in msg:
                member_type = "Parents"
            elif "spouse" in msg:
                member_type = "Self + Spouse"
            elif "self" in msg:
                member_type = "Self"

            session.state = {"product": "health"}

            # If member type already mentioned → skip asking again
            if member_type:
                session.state["member_type"] = member_type
                session.stage = "health_age"
                session.save()

                response = humanize(agent, message,
                    "Ask age group of eldest member: 18-25, 26-35, 36-45, 46-55, 56-65, 65+."
                )
                return clean_for_voice(response)

            # Otherwise ask normally
            session.stage = "health_member_type"
            session.save()

            response = humanize(agent, message,
                "Ask which type of insurance you need: Self, Spouse, Family, Parents, Complete Family."
            )
            return clean_for_voice(response)

        elif detected_product == "term":
            session.stage = "term_cover_for"
            session.state = {"product": "term"}
            session.save()

            response = humanize(agent, message,
                "Ask who the policy is for: Self or Spouse."
            )
            return clean_for_voice(response)

        # If nothing detected → show menu
        if not state.get("product"):
            session.stage = "insurance_menu"
            session.save()

            response = humanize(agent, message,
                "Welcome user and show options: Health Insurance, Car Insurance, Term Life Insurance."
            )
            return clean_for_voice(response)

    # =====================================================
    # MASTER MENU
    # =====================================================

    if session.stage == "insurance_menu" and not state.get("product"):

        if msg in ["1", "health", "health insurance"]:
            session.stage = "health_member_type"
            session.state = {"product": "health"}
            session.save()

            response = humanize(agent, message,
                "Ask  which type of insurance you need: Self, Self + Spouse, Family, Parents, Complete Family."
            )
            return clean_for_voice(response)

        elif msg in ["2", "car", "car insurance"]:
            session.stage = "car_requirement"
            session.state = {"product": "car"}
            session.save()

            response = humanize(agent, message,
                "Ask what the user needs: New Car Insurance, Renew Existing Policy, or Claim Assistance."
            )
            return clean_for_voice(response)

        elif msg in ["3", "term", "life", "term life insurance"]:
            session.stage = "term_cover_for"
            session.state = {"product": "term"}
            session.save()

            response = humanize(agent, message,
                "Ask who the policy is for: Self or Spouse."
            )
            return clean_for_voice(response)

        elif msg in ["4", "advisor", "talk"]:
            session.stage = "insurance_lead_capture"
            session.state = {"product": "advisor"}
            session.save()

            response = humanize(agent, message,
                "Ask the user to share their name to connect with an advisor."
            )
            return clean_for_voice(response)

        else:
            response = humanize(agent, message,
                "Ask the user to select a valid option from the menu."
            )
            return clean_for_voice(response)

    # =====================================================
    # HEALTH FLOW
    # =====================================================

    if session.stage == "health_member_type":
        state["member_type"] = message
        session.stage = "health_age"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask age group of eldest member. 18-25, 26-35, 36-45, 46-55, 56-65, Above 65 ",
        )
        return clean_for_voice(response)

    if session.stage == "health_age":
        state["age_band"] = message
        session.stage = "health_cover"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask preferred sum insured: 3-5L, 5-10L, 10-25L, 25L+.",
            session.stage
        )
        return clean_for_voice(response)

    if session.stage == "health_cover":
        state["coverage"] = message
        session.stage = "insurance_lead_capture"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask user to share their name."
        )
        return clean_for_voice(response)
    
    # =====================================================
    # 🚗 CAR FLOW (NEW LOGIC ADDED)
    # =====================================================

    if session.stage == "car_requirement":

        state["requirement"] = message.strip()
        session.stage = "car_vehicle_details"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask for car registration number OR brand, year."
        )
        return clean_for_voice(response)

    if session.stage == "car_vehicle_details":

        state["vehicle_details"] = message.strip()
        session.stage = "car_policy_status"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask current policy status."
        )
        return clean_for_voice(response)

    if session.stage == "car_policy_status":

        state["policy_status"] = message.strip()
        session.stage = "car_plan_type"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask insurance type: Third Party or Comprehensive."
        )
        return clean_for_voice(response)

    if session.stage == "car_plan_type":

        state["plan_type"] = message.strip()
        session.stage = "car_addons"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask which add-ons user wants."
            " Zero Depreciation,\n"
            " Engine Protection."
        )
        return clean_for_voice(response)

    if session.stage == "car_addons":

        state["addons"] = message.strip()
        session.stage = "car_previous_claim"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask if user made any claims last year."
        )

    if session.stage == "car_previous_claim":

        state["previous_claim"] = message.strip()
        session.stage = "insurance_lead_capture"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask user to share their name."
        )
        return clean_for_voice(response)

    # =====================================================
    # TERM LIFE INSURANCE FLOW
    # =====================================================

    if session.stage == "term_cover_for":

        state["cover_for"] = message.strip()
        session.stage = "term_age"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask age group options. 18-25, 26-35, 36-45, 46-55, 56-65, Above 65 "
        )
        return clean_for_voice(response)


    if session.stage == "term_age":

        state["age"] = message.strip()
        session.stage = "term_income"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask preferred sum insured: 3-5L, 5-10L, 10-25L, 25L+."
        )
        return clean_for_voice(response)


    if session.stage == "term_income":

        state["income"] = message.strip()
        session.stage = "term_coverage"
        session.state = state
        session.save()
        

        response = humanize(agent, message,
            "Ask life cover amount options. 50L, 1 Crore, 2 Crore, Above 2 Crore"
        )
        return clean_for_voice(response)


    if session.stage == "term_coverage":

        state["coverage"] = message.strip()
        session.stage = "term_duration"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask policy duration options."
            "Till age 60,\n"
            "Till age 65,\n"
            "Till age 70,\n"
            "Whole life coverage"
        )
        return clean_for_voice(response)


    if session.stage == "term_duration":

        state["duration"] = message.strip()
        session.stage = "term_smoker"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask if the user is a smoker (Yes/No)."
        )
        return clean_for_voice(response)


    if session.stage == "term_smoker":

        state["smoker"] = message.strip()
        session.stage = "term_riders"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask which riders user wants."
            "Critical illness rider,\n"
            "Accidental death benefit,\n"
            "Waiver of premium,\n"
            "Income payout option\n"
            "You can choose one or multiple riders."
        )
        return clean_for_voice(response)


    if session.stage == "term_riders":

        state["riders"] = message.strip()
        session.stage = "insurance_lead_capture"
        session.state = state
        session.save()

        response = humanize(agent, message,
            "Ask user to share their name."
        )
        return clean_for_voice(response)


    # if session.stage == "insurance_lead_phone":

    #     state["phone"] = message.strip()
    #     session.stage = "insurance_lead_email"
    #     session.state = state
    #     session.save()

    #     response = humanize(agent, message, "Ask for phone number and email address.")


    # if session.stage == "insurance_lead_email":

    #     state["email"] = message.strip()
    #     session.stage = "completed"
    #     session.state = state
    #     session.save()

    #     response = humanize(agent, message,
    #         "Thank user and tell advisor will contact soon."
    #     )

    # =====================================================
    # LEAD CAPTURE
    # =====================================================

    # =====================================================
    # LEAD CAPTURE (UPDATED)
    # =====================================================

    if session.stage == "insurance_lead_capture":

        # ✅ STEP 1 — NAME
        if not state.get("name"):
            state["name"] = message.strip()
            session.state = state
            session.save()

            return(
                "Can you please provide your email address?"
            )

            # response = humanize(agent, message, "Ask for email address.")
            # return clean_for_voice(response)

        # ✅ STEP 2 — EMAIL (NO PHONE)
        elif not state.get("email"):
            state["email"] = message.strip()
            session.stage = "completed"
            session.state = state
            session.save()

            return (
                "Thank you for sharing your details Our advisor will connect with you shortly."
            )

     # =====================================================
    # 🔒 HARD STOP AFTER COMPLETION
    # =====================================================

    if session.stage == "completed":
        return "thank you Our advisor will contact you shortly."




# def insurance_transaction_strategy(agent, message, session):

#     from knowledge.services.retriever import retrieve_relevant_chunks
#     from conversations.services.azure_openai_service import generate_response

#     state = session.state or {}

#     context = retrieve_relevant_chunks(agent, message)

#     if not context:
#         context = ""

#     system_prompt = f"""
# You are {agent.name}, an Insurance Advisor at {agent.company_name}.

# Use the knowledge below to answer user questions and guide insurance conversations.

# CRITICAL CONVERSATION RULES:

# 1. Ask ONLY ONE question at a time.
# 2. Wait for the user's answer before asking the next question.
# 3. Never ask multiple questions in a single response.
# 4. Never list all required information at once.
# 5. Follow a step-by-step conversational flow.
# 6. Use short and clear questions.
# 7. Maintain a natural advisor tone.

# Additional Rules:

# • If the user asks for information → answer from the document.
# • If the user says they want insurance → start the flow.
# • Ask questions sequentially.
# • Never ask more than one question at once.


# Knowledge:
# {context}

# Conversation State:
# {state}
# """

#     response = generate_response(system_prompt, message)

#     # Safety fix for tuple/list responses
#     if isinstance(response, (list, tuple)):
#         response = response[0]

#     return response










def mutual_fund_advisor_strategy(agent, message, session):

    from knowledge.services.retriever import retrieve_relevant_chunks
    from conversations.services.azure_openai_service import generate_response
    import re

    msg = message.lower()
    state = session.state or {}

    # =====================================================
    #  DOCUMENT KNOWLEDGE CHECK (RAG FIRST)
    # =====================================================

    context = retrieve_relevant_chunks(agent, message)

    if context and context.strip():

        system_prompt = f"""
{agent.resolved_prompt}

Knowledge Context:
{context}

Instructions:
- Answer ONLY using the provided document context.
- If the answer exists in the document, explain it clearly.
- Keep the response under 3 sentences.
- Do not invent information outside the document.
"""

        return generate_response(system_prompt, message)

    # =====================================================
    #  BEGINNER EXPLANATION FLOW
    # =====================================================

    beginner_keywords = [
        "don't know", "dont know", "new to mutual fund",
        "what is mutual fund", "mutual funds explain",
        "i am beginner"
    ]

    if any(k in msg for k in beginner_keywords):

        return (
            "Mutual funds are investment funds where money from many investors "
            "is pooled together and invested in assets like stocks or bonds. "
            "They are managed by professional fund managers and allow investors "
            "to start with small amounts through SIP or lump sum investments."
        )


    # =====================================================
    #  RETIREMENT GOAL DETECTION
    # =====================================================

    if "retirement" in msg or "retire" in msg:

        return (
            "For retirement goals, investors often consider long-term investment approaches such as equity mutual funds and SIP investing. "
            "Long-term investing allows compounding to grow wealth gradually over many years."
        )


    # =====================================================
    #  DETECT INVESTMENT AMOUNT
    # =====================================================

    numbers = re.findall(r"\d+\.?\d*", msg)

    if numbers and not state.get("amount"):

        state["amount"] = numbers[0]
        session.state = state
        session.stage = "ask_investment_horizon"
        session.save()

        return (
            f"Got it. You want to invest around ₹{state['amount']}.\n"
            "Are you planning to invest for:\n"
            "Short term (less than 1 year),\n"
            "Mid term (1–3 years),\n"
            "Long term (3+ years)?"
        )

    # =====================================================
    #  INVESTMENT HORIZON FLOW
    # =====================================================

    if session.stage == "ask_investment_horizon":

        if "short" in msg:

            session.stage = None
            session.state = {}
            session.save()

            return (
                "For short-term goals, some investors explore trading approaches like:\n"
                " Intraday trading,\n"
                " Swing trading,\n"
                " Options trading\n"
                "These approaches generally involve higher risk and require market knowledge."
            )

        elif "mid" in msg:

            session.stage = "ask_risk"
            session.save()

            return (
                "For medium-term investing (1–3 years), investors often consider:\n"
                " Hybrid mutual funds,\n"
                " Balanced advantage funds,\n"
                " Conservative equity funds\n"
                "These aim to balance growth and stability."
            )

        elif "long" in msg:

            session.stage = "ask_risk"
            session.save()

            return (
                "For long-term investing (3+ years), investors often consider:\n"
                " Equity mutual funds,\n"
                " Index funds,\n"
                " SIP investing\n"
                "Long-term investing allows compounding to work over time."
            )

        else:
            return "Would you prefer short-term, mid-term, or long-term investing?"
        
    
    # =====================================================
    #  RISK PROFILING
    # =====================================================

    if session.stage == "ask_risk":

        if "low" in msg:

            suggestion = (
                "Investors with lower risk tolerance often consider debt funds or conservative hybrid funds."
            )

        elif "moderate" in msg:

            suggestion = (
                "Moderate risk investors often explore balanced advantage funds or hybrid mutual funds."
            )

        elif "high" in msg:

            suggestion = (
                "Higher risk investors sometimes consider equity mutual funds such as large-cap or index funds."
            )

        else:
            return "Would you say your risk tolerance is low, moderate, or high?"

        session.stage = "sip_suggestion"
        session.save()

        return (
            f"{suggestion}\n\n"
            "Would you like to invest through a monthly SIP or a lump-sum investment?"
        )

    # =====================================================
    #  SIP SUGGESTION
    # =====================================================

    if session.stage == "sip_suggestion":

        if "sip" in msg:

            session.stage = None
            session.state = {}
            session.save()

            return (
                "SIP (Systematic Investment Plan) allows investors to invest a fixed amount regularly, "
                "such as monthly. This approach helps build investment discipline and reduces timing risk."
            )

        if "lump" in msg:

            session.stage = None
            session.state = {}
            session.save()

            return (
                "Lump-sum investing means investing the full amount at once. "
                "Some investors use this approach when they have a larger amount ready for long-term investment."
            )

        return "Would you prefer SIP investing or lump-sum investing?"


    # =====================================================
    #  DEFAULT RESPONSE
    # =====================================================

    return (
        "I can help you understand mutual funds and general investment approaches. "
        "You can ask about mutual funds or tell me your investment amount."
    )










def investment_advisor_strategy(agent, message, session):

    from knowledge.services.retriever import retrieve_relevant_chunks
    from conversations.services.azure_openai_service import generate_response
    import re

    msg = message.lower().strip()
    state = session.state or {}

    # =====================================================
    # 1️⃣ DOCUMENT KNOWLEDGE (RAG FIRST)
    # Only trigger if NO active flow
    # =====================================================

    if not session.stage:

        context = retrieve_relevant_chunks(agent, message)

        if context and context.strip():

            system_prompt = f"""
{agent.resolved_prompt}

Knowledge Context:
{context}

Instructions:
- Answer strictly using the document context.
- Keep response within 2–3 sentences.
- Do not generate financial advice outside the document.
"""

            return generate_response(system_prompt, message)

    # =====================================================
    # 2️⃣ BEGINNER INVESTMENT EXPLANATION
    # =====================================================

    beginner_keywords = [
        "what is investment",
        "i want to start investing",
        "how to start investing",
        "new to investing",
        "beginner"
    ]

    if any(k in msg for k in beginner_keywords):

        return (
            "Investing means allocating money into financial assets such as stocks, "
            "mutual funds, bonds, or other instruments with the goal of growing wealth "
            "over time."
        )


    # =====================================================
    # 2.5️⃣ DEMO INTEREST RATE / RETURN QUESTIONS
    # =====================================================

    interest_keywords = [
        "interest", "rate", "return", "returns", "roi", "profit"
    ]

    if any(word in msg for word in interest_keywords):

        if "short" in msg:
            rate = "6.5%"

        elif "mid" in msg:
            rate = "7.5%"

        elif "long" in msg:
            rate = "9%"

        else:
            return (
                "Investment returns depend on market conditions and investment duration. "
                "For demonstration purposes, investors sometimes consider approximate ranges such as:\n"
                "Short-term investments: around 6.5%,\n"
                "Mid-term investments: around 7.5%,\n"
                "Long-term investments: around 9%,\n"
                "This information is provided for educational purposes only."
            )

    # =====================================================
    # 3️⃣ DETECT INVESTMENT AMOUNT
    # =====================================================

    numbers = re.findall(r"\d+\.?\d*", msg)

    if numbers and not state.get("amount"):

        state["amount"] = numbers[0]
        session.stage = "investment_horizon"
        session.state = state
        session.save()

        return (
            f"Got it. You are planning to invest around ₹{state['amount']}.\n\n"
            "Is your investment horizon:,\n"
            "Short term (less than 1 year),\n"
            "Mid term (1–5 years),\n"
            "Long term (5+ years)?"
        )

    # =====================================================
    # 4️⃣ INVESTMENT HORIZON
    # =====================================================

    if session.stage == "investment_horizon":

        if "short" in msg:

            session.stage = None
            session.state = {}
            session.save()

            return (
                "For short-term investing, some investors explore trading approaches "
                "such as intraday trading or swing trading. These approaches involve "
                "higher risk and require market knowledge."
            )

        if "mid" in msg:

            session.stage = "risk_profile"
            session.save()

            return (
                "For medium-term investing, investors often look at diversified options "
                "such as balanced portfolios or hybrid investment strategies.\n"
                "What level of risk are you comfortable with?,\n"
                "Low risk,\n"
                "Moderate risk,\n"
                "High risk"
            )

        if "long" in msg:

            session.stage = "risk_profile"
            session.save()

            return (
                "Long-term investing focuses on wealth creation and compounding.\n"
                "What level of investment risk are you comfortable with?,\n"
                "Low risk,\n"
                "Moderate risk,\n"
                "High risk"
            )

        return "Would you prefer short-term, mid-term, or long-term investing?"

    # =====================================================
    # 5️⃣ RISK PROFILING
    # =====================================================

    if session.stage == "risk_profile":

        if "low" in msg:

            suggestion = (
                "Investors with lower risk tolerance often consider instruments "
                "such as bonds, fixed income investments, or conservative portfolios."
            )

        elif "moderate" in msg:

            suggestion = (
                "Moderate risk investors often consider diversified portfolios "
                "including mutual funds, hybrid funds, or balanced investments."
            )

        elif "high" in msg:

            suggestion = (
                "Higher risk investors sometimes explore equity-focused investments "
                "or growth-oriented portfolios."
            )

        else:
            return "Would you say your risk tolerance is low, moderate, or high?"

        session.stage = "investment_goal"
        session.save()

        return (
            f"{suggestion}\n\n"
            "What is your main investment goal?\n"
            "Retirement planning\n"
            "Wealth creation\n"
            "Short-term financial goal"
        )

    # =====================================================
    # 6️⃣ GOAL DETECTION
    # =====================================================

    if session.stage == "investment_goal":

        if "retirement" in msg:

            goal_response = (
                "For retirement planning, investors usually focus on long-term "
                "investment strategies that allow compounding over many years."
            )

        elif "wealth" in msg:

            goal_response = (
                "For wealth creation, investors often focus on diversified portfolios "
                "with growth-oriented assets."
            )

        elif "short" in msg:

            goal_response = (
                "Short-term goals often require more stable investments to reduce "
                "exposure to market fluctuations."
            )

        else:
            return (
                "Could you tell me your goal? For example: retirement planning, "
                "wealth creation, or a short-term goal."
            )

        session.stage = "investment_method"
        session.save()

        return (
            f"{goal_response}\n"
            "Would you prefer investing through:,\n"
            "Monthly SIP,\n"
            "Lump sum investment?"
        )

    # =====================================================
    # 7️⃣ INVESTMENT METHOD
    # =====================================================

    if session.stage == "investment_method":

        if "sip" in msg:

            session.stage = None
            session.state = {}
            session.save()

            return (
                "SIP (Systematic Investment Plan) allows investors to invest "
                "a fixed amount regularly, typically monthly. This helps build "
                "investment discipline and reduces timing risk."
            )

        if "lump" in msg:

            session.stage = None
            session.state = {}
            session.save()

            return (
                "A lump sum investment means investing the full amount at once. "
                "Some investors use this approach when they have a large amount "
                "available for long-term investment."
            )

        return "Would you prefer SIP investing or lump-sum investing?"

    # =====================================================
    # DEFAULT RESPONSE
    # =====================================================

    return (
        "I can help explain investment concepts such as asset allocation, "
        "risk levels, and investment strategies. You can also tell me how "
        "much you plan to invest."
    )





def sales_strategy(agent, message, session):

    context = retrieve_relevant_chunks(agent, message)

    if not context:
        context = ""

    system_prompt = f"""
{agent.resolved_prompt}

Product Information:
{context}

Goal:
Explain product value clearly and guide the user toward the next step.

Rules:
- 2–3 sentences
- Simple language
- Focus on benefits
- End with a soft next step
"""

    return generate_response(system_prompt, message)

def lead_qualification_strategy(agent, message, session):

    state = session.state or {}
    msg = message.lower()
    stage = session.stage

    affirm_words = [
    "yes",
    "yeah",
    "yup",
    "ok",
    "okay",
    "sure",
    "sounds good",
    "that works",
    "lets do it",
    "please do"
]

    connect_words = [
    "connect",
    "talk",
    "meet",
    "book",
    "schedule",
    "appointment",
    "speak with",
    "sales expert"
    ]

    # -------------------------------
    # User agrees to meet specialist
    # -------------------------------

    if stage not in ["collect_name", "collect_phone"] and (
        any(w in msg for w in affirm_words) or
        any(w in msg for w in connect_words)
    ):

        session.stage = "collect_name"
        session.save()

        return "Great. May I have your name so I can arrange the meeting?"
    

    # -------------------------------
    # Collect user name
    # -------------------------------

    if stage == "collect_name":

        state["user_name"] = message.strip()
        session.state = state

        session.stage = "collect_phone"
        session.save()

        return f"Thanks {state['user_name']}. Could you also share your phone number?"


    # -------------------------------
    # Collect phone number
    # -------------------------------

    if stage == "collect_phone":

        phone_match = re.search(r"\d{8,15}", message)

        if phone_match:

            state["phone"] = phone_match.group()
            session.state = state

            session.stage = "meeting_confirmed"
            session.save()

            return f"""
    Perfect, {state['user_name']}.

    Our specialist from {agent.company_name} will contact you shortly to schedule the meeting and discuss the best strategy for your business.
    """

        return "Could you please share a valid phone number?"

    info_keywords = [
        "information",
        "what do you do",
        "what services",
        "services",
        "solutions",
        "about your company",
        "tell me about",
        "what can you help with"
    ]

    if any(k in msg for k in info_keywords):
        return information_strategy(agent, message, session)

    

    # ------------------------------------------------
    # STEP 1: Retrieve knowledge context dynamically
    # ------------------------------------------------

    context = retrieve_relevant_chunks(agent, message) or ""


    # ------------------------------------------------
    # STEP 2: Extract structured lead information
    # ------------------------------------------------

    extraction_prompt = f"""
You are extracting lead qualification information.

Return JSON only:

{{
"goal": "",
"business_type": "",
"industry": "",
"budget": "",
"timeline": ""
}}

User message:
"{message}"

Rules:
- Extract information only if clearly mentioned.
- Do not guess missing details.
- Leave fields empty if not present.
"""

    raw = generate_response(extraction_prompt, message)

    try:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        extracted = json.loads(match.group())
    except:
        extracted = {}

    for k,v in extracted.items():
        if v:
            state[k] = v

    session.state = state
    session.save()


    # ------------------------------------------------
    # STEP 3: Determine missing lead information
    # ------------------------------------------------

    missing = []

    if not state.get("goal"):
        missing.append("goal")

    if not state.get("business_type"):
        missing.append("business_type")

    if not state.get("budget"):
        missing.append("budget")


    # ------------------------------------------------
    # STEP 4: Ask intelligent follow-up question
    # ------------------------------------------------

    if missing:

        question_prompt = f"""
You are {agent.name}, a Lead Qualifier at {agent.company_name}.

Company knowledge context:
{context}

Known lead information:
{state}

User message:
{message}

Missing information:
{missing}

Instructions:
- Ask ONE intelligent follow-up question.
- Use the available information to make the question relevant.
- Do NOT ask about information already implied by the user.
- Do NOT repeat questions already answered.
- Keep response under 20 words.
- Sound conversational and professional.
"""

        return generate_response(question_prompt, message)


    # ------------------------------------------------
    # STEP 5: Provide advisory insight + sales handoff
    # ------------------------------------------------

    advisory_prompt = f"""
You are a business advisor at {agent.company_name}.

Lead information:
{state}

Company knowledge:
{context}

Instructions:
1. Provide a short advisory insight based on the user's business goal.
2. Mention one realistic strategy the business could use.
3. Ask if the user would like to speak with a company specialist.

Rules:
- Maximum 2 sentences
- Sound like a real business advisor
- No filler phrases like "it sounds like"
"""

    return generate_response(advisory_prompt, message)


def product_demo_strategy(agent, message, session):


    state = session.state or {}
    msg = message.lower()
    context = retrieve_relevant_chunks(agent, message) or ""
    stage = session.stage



    overview_keywords = [
    "what information",
    "what does this product do",
    "what is the product",
    "product name",
    "tell me about the product",
    "what platform is this"
    ]

    if any(k in msg for k in overview_keywords):

        context = retrieve_relevant_chunks(agent, message) or ""

        system_prompt = f"""
    You are a Product Demo Specialist at {agent.company_name}.

    Knowledge Context:
    {context}

    User Question:
    {message}

    Instructions:
    - Identify the product or platform described in the context.
    - Explain what the product does.
    - Mention key capabilities or features.

    Rules:
    - Only use information from the context.
    - Do NOT guess product names.
    - If the name is unclear, say "the platform described".
    - Maximum 3 sentences.
    """

        return generate_response(system_prompt, message)


    general_questions = [
    "what information",
    "what do you do",
    "what is this product",
    "what features",
    "what services"
    ]

    if any(q in msg for q in general_questions):

        system_prompt = f"""
    You are a Product Demo Specialist at {agent.company_name}.

    Explain the product overview.

    Knowledge:
    {context}

    Rules:
    - Summarize the platform capabilities
    - Mention key features
    - Maximum 3 sentences
    """

        return generate_response(system_prompt, message)

    # -------------------------------------
    # 1️⃣ Demo booking confirmation
    # -------------------------------------

    affirm_words = [
        "yes","yeah","yup","ok","okay",
        "sure","sounds good","lets do it"
    ]

    demo_words = [
        "demo","show me","walkthrough",
        "see how","product demo"
    ]


    if stage not in ["collect_name","collect_phone"] and (
        any(w in msg for w in affirm_words) or
        any(w in msg for w in demo_words)
    ):

        session.stage = "collect_name"
        session.save()

        return "Great. May I have your name to arrange the product demo?"


    # -------------------------------------
    # 2️⃣ Collect name
    # -------------------------------------

    if stage == "collect_name":

        state["name"] = message.strip()
        session.state = state

        session.stage = "collect_phone"
        session.save()

        return f"Thanks {state['name']}. Could you share your phone number so we can schedule the demo?"


    # -------------------------------------
    # 3️⃣ Collect phone
    # -------------------------------------

    if stage == "collect_phone":

        phone = re.search(r"\d{8,15}", message)

        if phone:

            state["phone"] = phone.group()
            session.state = state

            session.stage = "demo_booked"
            session.save()

            return f"""
Perfect {state['name']}.

Our product specialist from {agent.company_name} will contact you shortly to schedule the demo.
"""

        return "Could you please provide a valid phone number?"


    # -------------------------------------
    # 4️⃣ Retrieve product knowledge
    # -------------------------------------

    


    # -------------------------------------
    # 5️⃣ Explain product feature
    # -------------------------------------

    system_prompt = f"""
You are a Product Demo Specialist at {agent.company_name}.

Knowledge Context:
{context}

User Question:
{message}

Goal:
Explain the product feature or capability clearly and relate it to real business usage.

Rules:
- Use only the provided knowledge context
- Do NOT invent product names or features
- If information is missing, say you do not have that detail
- Keep answers clear and conversational
- Maximum 2–3 sentences
"""

    return generate_response(system_prompt, message)