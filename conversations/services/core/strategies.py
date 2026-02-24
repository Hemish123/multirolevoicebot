from knowledge.services.retriever import retrieve_relevant_chunks
from conversations.services.azure_openai_service import generate_response
 
 
def information_strategy(agent, message, session):
    context = retrieve_relevant_chunks(agent, message)
 
    if not context:
        context = ""
 
    if not context.strip():
        return "This information is not mentioned in the uploaded document."
 
    system_prompt = f"""
{agent.resolved_prompt}
 
Conversation Stage: {session.stage or "new"}
 
Knowledge Context:
{context}
 
Respond naturally and professionally.
Use only the knowledge context.
Do not hallucinate.
Add helpful follow-up suggestions when appropriate.
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
 
 
# def qualification_strategy(agent, message, session):
 
#     state = session.state or {}
#     msg = message.lower()
 
#     # STEP 1 — Collect Property Type
#     if not state.get("property_type"):
#         if session.stage == "collecting_property_type":
#             state["property_type"] = message
#             session.state = state
#             session.stage = "collecting_location"
#             session.save()
#             return "Great. Which location are you interested in?"
 
#         session.stage = "collecting_property_type"
#         session.save()
#         return "What type of property are you looking for? (Apartment, Villa, Commercial, etc.)"
 
#     # STEP 2 — Collect Location
#     if not state.get("location"):
#         if session.stage == "collecting_location":
#             state["location"] = message
#             session.state = state
#             session.stage = "collecting_budget"
#             session.save()
#             return "Understood. What is your approximate budget range?"
 
#         session.stage = "collecting_location"
#         session.save()
#         return "Which location do you prefer?"
 
#     # STEP 3 — Collect Budget
#     if not state.get("budget"):
#         if session.stage == "collecting_budget":
#             state["budget"] = message
#             session.state = state
#             session.stage = "suggesting"
#             session.save()
 
#             query = f"{state['property_type']} in {state['location']} under {state['budget']}"
#             context = retrieve_relevant_chunks(agent, query)
 
#             if not context:
#                 return "I currently don't see exact matches in that range. Would you like to adjust your budget or location?"
 
#             system_prompt = f"""
# {agent.resolved_prompt}
 
# Buyer Requirements:
# Property Type: {state['property_type']}
# Location: {state['location']}
# Budget: {state['budget']}
 
# Available Listings:
# {context}
 
# Suggest the most relevant properties naturally and offer site visit.
# """
 
#             return generate_response(system_prompt, message)
 
#         session.stage = "collecting_budget"
#         session.save()
#         return "What is your budget range?"
 
#     return "Would you like to schedule a site visit for any of these options?"
 
 
 
 
 
 
 
 
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