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
Do not use brochure formatting.
Keep response 3–5 sentences.
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