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
        return f"I am {agent.name}, your {agent.role_template.role_name} at {agent.company_name}."

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

Respond conversationally.
Keep response strictly 2–3 sentences.
Use simple, clear language.
Do not use brochure formatting.
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

    import re

    msg = message.lower()

    # 🔹 Lightweight numeric extraction (NO LLM)
    numbers = re.findall(r"\d+\.?\d*", msg)
    numbers = [float(n) for n in numbers]

    income = numbers[0] if len(numbers) > 0 else 0
    loan_amount = numbers[1] if len(numbers) > 1 else 0

    tenure_years = 20
    interest_rate = 8.5

    # 🔹 Eligibility Mode
    if income > 0 and "income" in msg:

        eligible_emi = income * 0.5
        monthly_rate = (interest_rate / 100) / 12
        tenure_months = tenure_years * 12

        estimated_loan = (
            eligible_emi *
            ((1 + monthly_rate) ** tenure_months - 1) /
            (monthly_rate * (1 + monthly_rate) ** tenure_months)
        )

        estimated_loan_lakh = round(estimated_loan / 100000, 1)

        system_prompt = f"""
You are a professional home loan advisor.

Estimated Loan Eligibility: {estimated_loan_lakh} lakh

Keep answer under 4 sentences.
Professional tone.
Mention final approval depends on bank evaluation.
"""

        return generate_response(system_prompt, message)

    # 🔹 EMI Mode
    if loan_amount > 0:

        monthly_rate = (interest_rate / 100) / 12
        tenure_months = tenure_years * 12

        emi = (
            loan_amount *
            monthly_rate *
            (1 + monthly_rate) ** tenure_months
        ) / ((1 + monthly_rate) ** tenure_months - 1)

        emi_value = round(emi)

        system_prompt = f"""
You are a professional home loan advisor.

Calculated EMI: {emi_value}

Keep response short and professional.
"""

        return generate_response(system_prompt, message)

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






def insurance_transaction_strategy(agent, message, session):

    from conversations.services.core.strategies import information_strategy

    state = session.state or {}
    msg = message.lower().strip()

    def humanize(agent, user_message, instruction, stage=None):

        from knowledge.services.retriever import retrieve_relevant_chunks
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
            return humanize(agent, message, "Tell user we will continue with current insurance selection.")

        else:
            return humanize(agent, message, "Ask user to reply with Yes or No.")

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
    
    # HARD LOCK
    detected_product = current_product if current_product else detected_product

    # =====================================================
    # SMART INITIAL ENTRY
    # =====================================================

    if not state.get("product") and session.stage is None:

        if detected_product == "car":
            session.stage = "car_requirement"
            session.state = {"product": "car"}
            session.save()

            return humanize(agent, message,
                "Ask what user needs: New Car Insurance, Renewal, or Claim Assistance."
            )
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

                return humanize(agent, message,
                    "Ask age group of eldest member: 18-25, 26-35, 36-45, 46-55, 56-65, 65+."
                )

            # Otherwise ask normally
            session.stage = "health_member_type"
            session.save()

            return humanize(agent, message,
                "Ask which type of insurance you need: Self, Spouse, Family, Parents, Complete Family."
            )

        elif detected_product == "term":
            session.stage = "term_cover_for"
            session.state = {"product": "term"}
            session.save()

            return humanize(agent, message,
                "Ask who the policy is for: Self or Spouse."
            )

        # If nothing detected → show menu
        if not state.get("product"):
            session.stage = "insurance_menu"
            session.save()

            return humanize(agent, message,
                "Welcome user and show options: Health Insurance, Car Insurance, Term Life Insurance."
            )

    # =====================================================
    # MASTER MENU
    # =====================================================

    if session.stage == "insurance_menu":

        if msg in ["1", "health", "health insurance"]:
            session.stage = "health_member_type"
            session.state = {"product": "health"}
            session.save()

            return humanize(agent, message,
                "Ask  which type of insurance you need: Self, Self + Spouse, Family, Parents, Complete Family."
            )

        elif msg in ["2", "car", "car insurance"]:
            session.stage = "car_requirement"
            session.state = {"product": "car"}
            session.save()

            return humanize(agent, message,
                "Ask what the user needs: New Car Insurance, Renew Existing Policy, or Claim Assistance."
            )

        elif msg in ["3", "term", "life", "term life insurance"]:
            session.stage = "term_cover_for"
            session.state = {"product": "term"}
            session.save()

            return humanize(agent, message,
                "Ask who the policy is for: Self or Spouse."
            )

        elif msg in ["4", "advisor", "talk"]:
            session.stage = "insurance_lead_capture"
            session.state = {"product": "advisor"}
            session.save()

            return humanize(agent, message,
                "Ask the user to share their name to connect with an advisor."
            )

        else:
            return humanize(agent, message,
                "Ask the user to select a valid option from the menu."
            )

    # =====================================================
    # HEALTH FLOW
    # =====================================================

    if session.stage == "health_member_type":
        state["member_type"] = message
        session.stage = "health_age"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask age group of eldest member. 18-25, 26-35, 36-45, 46-55, 56-65, Above 65 ",
        )

    if session.stage == "health_age":
        state["age_band"] = message
        session.stage = "health_cover"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask preferred sum insured: 3-5L, 5-10L, 10-25L, 25L+.",
            session.stage
        )

    if session.stage == "health_cover":
        state["coverage"] = message
        session.stage = "insurance_lead_capture"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask user to share their name."
        )
    
    # =====================================================
    # 🚗 CAR FLOW (NEW LOGIC ADDED)
    # =====================================================

    if session.stage == "car_requirement":

        state["requirement"] = message.strip()
        session.stage = "car_vehicle_details"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask for car registration number OR brand, model, fuel, year."
        )

    if session.stage == "car_vehicle_details":

        state["vehicle_details"] = message.strip()
        session.stage = "car_policy_status"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask current policy status."
        )

    if session.stage == "car_policy_status":

        state["policy_status"] = message.strip()
        session.stage = "car_plan_type"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask insurance type: Third Party or Comprehensive."
        )

    if session.stage == "car_plan_type":

        state["plan_type"] = message.strip()
        session.stage = "car_addons"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask which add-ons user wants."
            " Zero Depreciation,\n"
            " Engine Protection,\n"
            " Roadside Assistance,\n"
            " Return to Invoice,\n"
            " NCB Protection"
        )

    if session.stage == "car_addons":

        state["addons"] = message.strip()
        session.stage = "car_previous_claim"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask if user made any claims last year."
        )

    if session.stage == "car_previous_claim":

        state["previous_claim"] = message.strip()
        session.stage = "insurance_lead_capture"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask user to share their name."
        )

    # =====================================================
    # TERM LIFE INSURANCE FLOW
    # =====================================================

    if session.stage == "term_cover_for":

        state["cover_for"] = message.strip()
        session.stage = "term_age"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask age group options. 18-25, 26-35, 36-45, 46-55, 56-65, Above 65 "
        )


    if session.stage == "term_age":

        state["age"] = message.strip()
        session.stage = "term_income"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask preferred sum insured: 3-5L, 5-10L, 10-25L, 25L+."
        )


    if session.stage == "term_income":

        state["income"] = message.strip()
        session.stage = "term_coverage"
        session.state = state
        session.save()
        

        return humanize(agent, message,
            "Ask life cover amount options. 50L, 1 Crore, 2 Crore, Above 2 Crore"
        )


    if session.stage == "term_coverage":

        state["coverage"] = message.strip()
        session.stage = "term_duration"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask policy duration options."
            "Till age 60,\n"
            "Till age 65,\n"
            "Till age 70,\n"
            "Whole life coverage"
        )


    if session.stage == "term_duration":

        state["duration"] = message.strip()
        session.stage = "term_smoker"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask if the user is a smoker (Yes/No)."
        )


    if session.stage == "term_smoker":

        state["smoker"] = message.strip()
        session.stage = "term_riders"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask which riders user wants."
            "Critical illness rider,\n"
            "Accidental death benefit,\n"
            "Waiver of premium,\n"
            "Income payout option\n"
            "You can choose one or multiple riders."
        )


    if session.stage == "term_riders":

        state["riders"] = message.strip()
        session.stage = "insurance_lead_capture"
        session.state = state
        session.save()

        return humanize(agent, message,
            "Ask user to share their name."
        )


    # if session.stage == "insurance_lead_phone":

    #     state["phone"] = message.strip()
    #     session.stage = "insurance_lead_email"
    #     session.state = state
    #     session.save()

    #     return humanize(agent, message, "Ask for phone number and email address.")


    # if session.stage == "insurance_lead_email":

    #     state["email"] = message.strip()
    #     session.stage = "completed"
    #     session.state = state
    #     session.save()

    #     return humanize(agent, message,
    #         "Thank user and tell advisor will contact soon."
    #     )

    # =====================================================
    # LEAD CAPTURE
    # =====================================================

    if session.stage == "insurance_lead_capture":

        if not state.get("name"):
            state["name"] = message.strip()
            session.state = state
            session.save()
            return humanize(agent, message, "Ask for phone number.")

        elif not state.get("phone"):
            state["phone"] = message.strip()
            session.state = state
            session.save()
            return humanize(agent, message, "Ask for email address.")

        elif not state.get("email"):
            state["email"] = message.strip()
            session.stage = "completed"
            session.state = state
            session.save()

            return (
                " Thank you for choosing us!\n\n"
                "We’re preparing the best insurance plan for you.\n"
                "Our expert will connect with you shortly."
            )

     # =====================================================
    # 🔒 HARD STOP AFTER COMPLETION
    # =====================================================

    if session.stage == "completed":
        return "thank you. Our advisor will contact you shortly."








# def insurance_transaction_strategy(agent, message, session):

#     from knowledge.services.retriever import retrieve_relevant_chunks
#     from conversations.services.azure_openai_service import generate_response

#     msg = message.lower()

#     # =====================================================
#     # STEP 1 — RETRIEVE KNOWLEDGE FROM DOCUMENT
#     # =====================================================

#     context = retrieve_relevant_chunks(agent, message)

#     # =====================================================
#     # STEP 2 — BUILD SYSTEM PROMPT
#     # =====================================================

#     system_prompt = f"""
# {agent.resolved_prompt}

# You are an Insurance Advisor for {agent.company_name}.

# Use ONLY the knowledge document provided below to guide the user.

# Knowledge Context:
# {context}

# Instructions:
# - Follow the conversation flows defined in the document.
# - Ask the next step based on the flow.
# - Provide clear options when available.
# - If the user asks about claims, benefits, or policy terms, answer from the document.
# - Do NOT invent information outside the document.
# - Do NOT guarantee claims or returns.
# - Encourage consultation with a licensed advisor when necessary.

# Conversation Rules:
# - Keep answers short (2–3 sentences).
# - When multiple options exist, present them clearly.
# """

#     # =====================================================
#     # STEP 3 — GENERATE RESPONSE
#     # =====================================================

#     return generate_response(system_prompt, message)











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