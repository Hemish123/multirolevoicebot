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
 


def identity_guard(agent, message):
    """
    Intercepts identity-related questions BEFORE any strategy logic.
    Returns a response string if handled, otherwise None.
    """

    msg = message.lower().strip()

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
 
def information_strategy(agent, message, session):
    context = retrieve_relevant_chunks(agent, message)

    if not context:
        context = ""

    # 🟢 If general capability question → allow natural response
    general_questions = [
        "who are you",
        "what is your company",
        "what information",
        "what services",
        "summarize",
        "about you"
    ]

    if any(q in message.lower() for q in general_questions):
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
        return generate_response(system_prompt, message)

    # 🔴 If no relevant context found for property-specific question
    if not context.strip():
        return (
            "At the moment, I don’t have matching details for that request. "
            "If you need any other infromation tell me."
        )

    # 🟢 Normal knowledge response
    system_prompt = f"""
{agent.resolved_prompt}

Knowledge Context:
{context}

Respond in a short, natural tone.
Maximum 2–3 sentences.
Under 70 words.
No repetition.
Be direct and helpful.
Do not hallucinate.
"""

    return generate_response(system_prompt, message)
 
 




def transaction_strategy(agent, message, session):
    print("TRANSACTION STRATEGY CALLED")
    print("CURRENT STAGE:", session.stage)
    print("CURRENT STATE:", session.state)
 
    state = session.state or {}
    msg = message.lower()
 
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
    if not state.get("patient_name"):
        if session.stage == "collecting_name":
            state["patient_name"] = message.strip()
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
            state["date"] = message.strip()
            session.state = state
            session.stage = "collecting_time"
            session.save()
            return "Got it. Do you have a preferred time slot?"
 
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
        if "yes" in msg:
            session.stage = "completed"
            session.state = {}
            session.save()
            return (
                "Your appointment has been scheduled successfully. "
                "We look forward to seeing you. If you need to make any changes, just let me know."
            )
        else:
            session.stage = "collecting_date"
            session.save()
            return "No problem. Let's update the details. What new date would you prefer?"
 
    return "How can I assist you further?"
 
 
 
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
 

 
 
def classify_medical_case(agent, message):
 
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
 
    response = generate_response(system_prompt, message)
 
    import json
    try:
        return json.loads(response)
    except:
        return {
            "severity": "informational",
            "domain_relevance": "in_scope"
        }
 
 
def support_strategy(agent, message, session):
 
    case = classify_medical_case(agent, message)
 
    severity = case.get("severity")
    domain = case.get("domain_relevance")
 
    # Emergency
    if severity == "emergency":
        return (
            "⚠️ This may require urgent medical attention. "
            "Please visit the emergency department or contact emergency services immediately."
        )
 
    # Out of scope
    if domain == "out_of_scope":
        return (
            f"This concern appears outside the specialty of {agent.company_name}. "
            "It would be best to consult the appropriate specialist or a general hospital."
        )
 
    # Urgent
    if severity == "urgent":
        return (
            "This seems important and should be evaluated by a doctor soon. "
            "Would you like me to help you book an appointment?"
        )
 
    # Mild
    if severity == "mild":
        return (
            "This doesn’t sound urgent, but it’s still a good idea to consult a doctor if it continues. "
            "Would you like assistance scheduling a visit?"
        )
 
    # Default → informational
    return information_strategy(agent, message, session)





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
        if "yes" in msg:
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

Extract structured student information from the message.

Return JSON only:

{{
  "career_interest": "",
  "education_level": ""
}}

Rules:
- career_interest = desired career field
- education_level = 12th | graduation | unknown
- Do not explain.
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
        state["interest"] = profile["career_interest"]

    if profile.get("education_level"):
        state["background"] = profile["education_level"]

    session.state = state
    session.save()

    # 🔹 If no interest yet → ask
    if not state.get("interest"):
        return "Which career field are you interested in?"

    # 🔹 STEP 2 — CHECK PROGRAM EXISTENCE (Scope Awareness)

    scope_query = f"Programs related to {state['interest']}"
    scope_context = retrieve_relevant_chunks(agent, scope_query)

    if not scope_context:
        return (
            "At the moment, we do not offer programs in that field. "
            "Would you like to explore the courses currently available at our university?"
        )

    # 🔹 Ask background if missing
    if not state.get("background"):
        return "May I know your highest qualification — 12th or graduation?"

    # 🔹 STEP 3 — Retrieve best matching course dynamically

    query = f"Best course for {state['interest']} after {state['background']}"
    context = retrieve_relevant_chunks(agent, query)

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
- Suggest ONLY the most relevant program.
- Maximum 3 sentences.
- No marketing language.
- No long explanation.
- Sound like a professional academic counselor.
- Do not invent programs outside context.
"""

    return generate_response(system_prompt, message)



def education_scholarship_strategy(agent, message, session):

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

User Message: {message}

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

    context = retrieve_relevant_chunks(agent, message)

    system_prompt = f"""
{agent.resolved_prompt}

User Message:
{message}

Knowledge Base Context:
{context}

Instructions:
- Answer the customer’s question clearly.
- Use only the knowledge base if relevant information exists.
- If the knowledge base does not contain the answer, politely say the information is unavailable.
- Maintain a friendly and professional tone.
- Keep the response under 3 sentences.
"""

    return generate_response(system_prompt, message)




def complaint_handler_strategy(agent, message, session):

    context = retrieve_relevant_chunks(agent, message)

    system_prompt = f"""
{agent.resolved_prompt}

Customer Complaint:
{message}

Relevant Knowledge:
{context}

Instructions:
- First acknowledge the customer's concern empathetically.
- If knowledge context contains a solution, explain the next steps.
- If resolution is unclear, guide the customer toward the proper support channel.
- Do not invent company policies.
- Keep response supportive and professional.
- Maximum 3 sentences.
"""

    return generate_response(system_prompt, message)



def returns_refund_strategy(agent, message, session):

    context = retrieve_relevant_chunks(agent, message)

    system_prompt = f"""
{agent.resolved_prompt}

Customer Query:
{message}

Return / Refund Policy Context:
{context}

Instructions:
- Explain return or refund procedures clearly.
- Use only the policy information provided.
- If the policy does not contain the answer, state that the information is not available.
- Do not invent refund conditions or timelines.
- Keep the response concise and professional.
"""

    return generate_response(system_prompt, message)



def escalation_manager_strategy(agent, message, session):

    context = retrieve_relevant_chunks(agent, message)

    system_prompt = f"""
{agent.resolved_prompt}

Customer Issue:
{message}

Relevant Context:
{context}

Instructions:
- Review the issue and provide a professional response.
- If the issue requires escalation, explain the escalation process clearly.
- If resolution steps exist in the knowledge base, provide them.
- Do not promise outcomes beyond your authority.
- Maintain a calm and authoritative tone.
- Keep response within 3 sentences.
"""

    return generate_response(system_prompt, message)