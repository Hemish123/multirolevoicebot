# # # # conversations/services/core/dialogue_engine.py

# # # from knowledge.services.retriever import retrieve_relevant_chunks
# # # from conversations.services.azure_openai_service import generate_response
# # # from conversations.services.core.memory_manager import (
# # #     load_conversation_history,
# # #     save_conversation
# # # )
# # # from conversations.services.core.intent_classifier import classify_intent
# # # def process_message(agent, message):
# # #     """
# # #     Global conversation processor with intent classification.
# # #     """

# # #     # 1️⃣ Classify intent
# # #     intent_data = classify_intent(message)
# # #     intent = intent_data.get("intent", "unknown")

# # #     # 2️⃣ Load memory
# # #     history = load_conversation_history(agent)

# # #     # 3️⃣ Retrieve knowledge
# # #     context = retrieve_relevant_chunks(agent, message)

# # #     # 4️⃣ Guardrail: no knowledge
# # #     if not context.strip():
# # #         reply = "This information is not mentioned in the uploaded document."
# # #         save_conversation(agent, message, reply)
# # #         return reply

# # #     # 5️⃣ Build system prompt
# # #     system_prompt = f"""
# # # {agent.resolved_prompt}

# # # Detected Intent: {intent}

# # # Conversation History:
# # # {history}

# # # Knowledge Context:
# # # {context}

# # # Rules:
# # # - Answer ONLY using knowledge context
# # # - If information is missing, say:
# # #   "This information is not mentioned in the uploaded document."
# # # - Do NOT hallucinate
# # # """

# # #     reply = generate_response(system_prompt, message)

# # #     # 6️⃣ Save conversation
# # #     save_conversation(agent, message, reply)

# # #     return reply





# # # from knowledge.services.retriever import retrieve_relevant_chunks
# # # from conversations.services.azure_openai_service import generate_response
# # # from conversations.services.core.memory_manager import (
# # #     load_conversation_history,
# # #     save_conversation
# # # )
# # # from conversations.services.core.intent_classifier import classify_intent


# # # def process_message(agent, message):

# # #     # 1️⃣ Detect Intent
# # #     intent_data = classify_intent(message)
# # #     intent = intent_data.get("intent", "unknown")

# # #     # 2️⃣ GLOBAL CONVERSATIONAL ROUTER
# # #     if intent == "greeting":
# # #         reply = f"""
# # # Hello! Welcome to {agent.company_name or agent.name}.How can I assist you today?
# # # """.strip()

# # #         save_conversation(agent, message, reply)
# # #         return reply

# # #     if intent == "complaint":
# # #         reply = "I'm sorry to hear that. Could you please provide more details so I can assist you better?"
# # #         save_conversation(agent, message, reply)
# # #         return reply

# # #     # 3️⃣ Load Memory
# # #     history = load_conversation_history(agent)

# # #     # 4️⃣ Retrieve Knowledge
# # #     context = retrieve_relevant_chunks(agent, message)

# # #     # 5️⃣ Guardrail for Knowledge Questions
# # #     if not context.strip():
# # #         reply = "This information is not mentioned in the uploaded document."
# # #         save_conversation(agent, message, reply)
# # #         return reply

# # #     # 6️⃣ Build System Prompt
# # #     system_prompt = f"""
# # # {agent.resolved_prompt}

# # # Detected Intent: {intent}

# # # Conversation History:
# # # {history}

# # # Knowledge Context:
# # # {context}

# # # Rules:
# # # - Answer ONLY using knowledge context
# # # - If information is missing, say:
# # #   "This information is not mentioned in the uploaded document."
# # # - Do NOT hallucinate
# # # """

# # #     reply = generate_response(system_prompt, message)

# # #     save_conversation(agent, message, reply)

# # #     return reply




# # from knowledge.services.retriever import retrieve_relevant_chunks
# # from conversations.services.azure_openai_service import generate_response
# # from conversations.services.core.intent_classifier import classify_intent
# # from conversations.models import ConversationSession
# # import uuid
# # from conversations.services.core.behavior_router import get_role_strategy
# # from conversations.services.core.strategies import (
# #     information_strategy,
# #     transaction_strategy,
# #     qualification_strategy,
# #     support_strategy,
# # )
 
 
# # def process_message(agent, message, session_id=None):
 
# #     # 1️⃣ Create or Load Session
# #     if not session_id:
# #         session_id = str(uuid.uuid4())
 
# #     session, _ = ConversationSession.objects.get_or_create(
# #         agent=agent,
# #         session_id=session_id
# #     )
 
# #     # 2️⃣ Detect Intent (AI-based)
# #     intent_data = classify_intent(message)
# #     intent = intent_data.get("intent", "unknown")
# #     print("---- DEBUG START ----")
# #     print("MESSAGE:", message)
# #     print("INTENT:", intent)
# #     print("STAGE BEFORE:", session.stage)
# #     print("STATE BEFORE:", session.state)
# #     print("----------------------")
# #     session.current_intent = intent
 
# #     # 3️⃣ GLOBAL ROUTER (Intent-Level)
 
# #     if intent == "greeting" and not session.stage and not session.state:
# #         reply = f"Hello! Welcome to {agent.company_name or agent.name}. How can I assist you today?"
# #         return reply, session_id
 
# #     if intent == "complaint":
# #         reply = "I'm sorry to hear that. Could you please provide more details so I can assist you better?"
# #         session.stage = "handling_complaint"
# #         session.save()
# #         return reply, session_id
 
# #     # if intent == "emergency":
# #     #     reply = "If this is an emergency, please contact local emergency services immediately."
# #     #     session.stage = "emergency"
# #     #     session.save()
# #     #     return reply, session_id
   
 
# #     role_name = agent.role_template.role_name
# #     strategy_type = get_role_strategy(role_name)
 
# #     # 🔥 Only for Appointment Scheduler (transaction type)
# #     if strategy_type == "transaction":
 
# #         # 1️⃣ If booking flow is currently active → continue it
# #         if session.stage in ["collecting_name","collecting_date", "collecting_time", "confirming"]:
# #             reply = transaction_strategy(agent, message, session)
 
# #         # 2️⃣ If user explicitly wants to book → start transaction
# #         elif (
# #             intent == "appointment_request"
# #             or any(word in message.lower() for word in ["book", "appointment", "schedule"])
# #         ):
# #             # Reset previous state
# #             session.stage = None
# #             session.state = {}
# #             session.save()
# #             reply = transaction_strategy(agent, message, session)
 
# #         # 3️⃣ Otherwise → treat as knowledge question
# #         else:
# #             reply = information_strategy(agent, message, session)
 
# #     elif strategy_type == "support":
 
# #         # 🔹 If booking intent → start transaction flow
# #         if (
# #             intent in ["booking_request", "appointment_request"]
# #             or any(word in message.lower() for word in ["book", "appointment", "schedule"])
# #             or session.stage in ["collecting_name", "collecting_date", "collecting_time", "confirming"]
# #         ):
# #             reply = transaction_strategy(agent, message, session)
 
# #         else:
# #             reply = support_strategy(agent, message, session)
 
 
# #     elif strategy_type == "qualification":
# #         reply = qualification_strategy(agent, message, session)
 
# #     elif strategy_type == "smart_real_estate":
 
# #     # If booking intent → transaction
# #         if intent in ["booking_request", "site_visit_request"]:
# #             reply = transaction_strategy(agent, message, session)
 
# #         # If buying / searching intent → qualification
# #         elif any(word in message.lower() for word in [
# #             "2bhk", "3bhk", "villa", "flat", "apartment",
# #             "budget", "lakh", "cr", "property", "looking"
# #         ]):
# #             reply = qualification_strategy(agent, message, session)
 
# #         # Otherwise → general information
# #         else:
# #             reply = information_strategy(agent, message, session)
 
# #     else:
# #         reply = information_strategy(agent, message, session)
 
    
# #     # formatted_reply = ResponseFormatter.format(
# #     #     reply,
# #     #     strategy_type=strategy_type,
# #     #     intent=intent,
# #     #     agent_name=agent.name
# #     #     )

# #     return reply, session_id

# # #     # 4️⃣ Knowledge-Based Flow (RAG)
# # #     context = retrieve_relevant_chunks(agent, message)

# # #     if not context.strip():
# # #         reply = "This information is not mentioned in the uploaded document."
# # #         session.save()
# # #         return reply, session_id

# # #     # 5️⃣ Build Conversational Prompt
# # #     system_prompt = f"""
# # # {agent.resolved_prompt}

# # # Detected Intent: {intent}

# # # Conversation Stage: {session.stage or "new"}

# # # Knowledge Context:
# # # {context}

# # # Rules:
# # # - Respond conversationally like a human professional.
# # # - Use only the knowledge context.
# # # - If information is missing, say:
# # #   "This information is not mentioned in the uploaded document."
# # # - Do NOT hallucinate.
# # # """

# # #     reply = generate_response(system_prompt, message)

# # #     session.stage = "active"
# # #     session.save()

# # #     return reply, session_id















# from knowledge.services.retriever import retrieve_relevant_chunks
# from conversations.services.azure_openai_service import generate_response
# from conversations.services.core.intent_classifier import classify_intent
from conversations.models import ConversationSession
import uuid
from conversations.services.core.behavior_router import get_role_strategy
from conversations.services.core.strategies import (
    education_qualification_strategy,
    hr_helpdesk_strategy,
    identity_guard,
    information_strategy,
    insurance_transaction_strategy,
    investment_advisor_strategy,
    lead_qualification_strategy,
    mutual_fund_advisor_strategy,
    onboarding_support_strategy,
    product_demo_strategy,
    sales_strategy,
    transaction_strategy,
    qualification_strategy,
    support_strategy,
    site_visit_transaction_strategy,
    loan_financial_strategy,
    education_scholarship_strategy,
    education_support_strategy,
    travel_planner_strategy,
    restaurant_booking_strategy,
    hotel_booking_strategy,
    recruitment_advisory_strategy,
    customer_support_strategy,
    complaint_handler_strategy,
    returns_refund_strategy,
    escalation_manager_strategy,
    university_identity_guard,
)
from agents.models import VoiceAgent
 
# def process_message(agent, message, session_id=None):
 
#     # 1️⃣ Create or Load Session
#     if not session_id:
#         session_id = str(uuid.uuid4())
 
#     session, _ = ConversationSession.objects.get_or_create(
#         agent=agent,
#         session_id=session_id
#     )
 
#     # 2️⃣ Detect Intent (AI-based)
#     intent_data = classify_intent(message)
#     intent = intent_data.get("intent", "unknown")
#     print("---- DEBUG START ----")
#     print("MESSAGE:", message)
#     print("INTENT:", intent)
#     print("STAGE BEFORE:", session.stage)
#     print("STATE BEFORE:", session.state)
#     print("----------------------")
#     session.current_intent = intent
 
#     # 3️⃣ GLOBAL ROUTER (Intent-Level)
    
#     identity_reply = identity_guard(agent, message)
#     if identity_reply:
#         return identity_reply, session_id

#     if intent == "greeting" and not session.stage and not session.state:
#         reply = f"Hello! Welcome to {agent.company_name or agent.name}. How can I assist you today?"
#         return reply, session_id
 
#     if intent == "complaint":
#         reply = "I'm sorry to hear that. Could you please provide more details so I can assist you better?"
#         session.stage = "handling_complaint"
#         session.save()
#         return reply, session_id
 
def process_message(agent, message, session_id=None):

    import time
    import re

    start_time = time.time()

    # 1️⃣ Create or Load Session
    if not session_id:
        session_id = str(uuid.uuid4())

    # session, _ = ConversationSession.objects.get_or_create(
    #     agent=agent,
    #     session_id=session_id
    # )

    agent = VoiceAgent.objects.get(id=agent)

    session, _ = ConversationSession.objects.get_or_create(
        agent=agent,
        session_id=session_id
    )

    # 2️⃣ Improved Rule-Based Intent Detection (FAST but smarter)

    msg_lower = message.lower().strip()
    words = re.findall(r"\b\w+\b", msg_lower)

    complaint_keywords = ["complaint", "not happy", "bad service"]
    question_words = ["how", "what", "when", "why", "where", "can", "does", "do"]

    # Greeting detection
    greeting_keywords = [
    "hi",
    "hello",
    "hey",
    "start",
    "start conversation",
    "start chat",
    "begin",
    "good morning",
    "good evening"
    ]
#chnage after chnages========
    service_keywords = [
    "department", "departments",
    "specialty", "specialties",
    "service", "services",
    "clinic", "clinics",
    "treatment", "treatments"

    ]
    booking_phrases = [
    "book appointment",
    "schedule appointment",
    "make appointment",
    "i want appointment",
    "i need appointment",
    "i want to book",
    "schedule a visit"
    ]

    update_phrases = [
    "update appointment",
    "change appointment",
    "modify appointment",
    "reschedule appointment",
    "update the appointment",
    "change the date",
    "update the date",
    "reschedule"
    ]
    #================================ 
    exit_phrases = [
        "bye", "goodbye", "ok bye", "okay bye", "bye bye",
        "thanks", "thank you", "thank you so much",
        "thanks a lot", "thanks for helping",
        "thank you for helping",
        "appreciate it",
        "that is all", "thats all", "that's all",
        "no thanks", "no thank you",
        "done", "im done", "i am done",
        "nothing else", "thats it", "that's it",
        "all set", "perfect thanks",
        "great thanks", "ok thanks", "okay thanks"
    ]

    if any(msg_lower == phrase or msg_lower.startswith(phrase) for phrase in exit_phrases):

        session.stage = None
        session.state = {}
        session.current_intent = "conversation_end"
        session.save()

        reply = (
            f"You're welcome!\n\n"
            f"Thank you to connect with {agent.company_name or agent.name}. "
            f"If you need assistance again, feel free to start a new conversation."
        )

        print("⏱ Total Message Time:", time.time() - start_time)
        return reply, session_id
    
    words = re.findall(r"\b\w+\b", msg_lower)

    
    # 🔹 Bot wellbeing detection (NEW)
    if any(phrase in msg_lower for phrase in [
        "how are you",
        "how are you doing",
        "how are you today",
        "how's it going",
        "how are things"
    ]):
        intent = "bot_wellbeing"
    
    # Greeting detection
    # elif any(word in msg_lower for word in greeting_keywords):
    #     intent = "greeting"

    elif any(word in greeting_keywords for word in words):

        # If message only contains greeting → treat as greeting
        if len(words) <= 2:
            intent = "greeting"

        # If greeting + real sentence → ignore greeting and continue classification
        else:
            msg_lower = re.sub(
                r'^(hi|hello|hey|good morning|good evening)\s+', 
                '', 
                msg_lower
            )
            words = re.findall(r"\b\w+\b", msg_lower)
            intent = "general_query"

    # Complaint detection
    elif any(word in msg_lower for word in complaint_keywords) and not any(q in msg_lower for q in question_words):
        intent = "complaint"

    # Appointment detection
    # elif any(word in msg_lower for word in ["book", "appointment", "schedule"]):
    #     intent = "appointment_request"

    #change after testing=================

    elif any(phrase in msg_lower for phrase in booking_phrases):
        intent = "appointment_request"

    elif any(phrase in msg_lower for phrase in update_phrases):
        intent = "appointment_update"
    #=====================================

    # Scholarship
    elif any(word in msg_lower for word in [
        "scholarship", "percentage", "marks", "financial aid",
        "fee waiver", "eligible", "%"
    ]):
        intent = "scholarship_query"

    # Education
    elif any(word in msg_lower for word in [
        "career",
        "course",
        "management",
        "engineering",
        "study",
        "admission",
        "deadline",
        "last date",
        "apply date",
        "application deadline",
        "closing date",
        "submission date"
    ]):
        intent = "education_query"

    # Information
    # elif any(word in msg_lower for word in [
    #     "what", "which", "tell", "information", "service", "timing"
    # ]):
    #     intent = "information_request"

    #chnage after testing=============
    elif any(word in msg_lower for word in [
        "what", "which", "tell", "information",
        "service", "services",
        "department", "departments",
        "specialty", "specialties",
        "timing"
    ]):
        intent = "information_request"

    else:
        intent = "general_query"

    print("---- DEBUG START ----")
    print("MESSAGE:", message)
    print("INTENT:", intent)
    print("STAGE BEFORE:", session.stage)
    print("STATE BEFORE:", session.state)
    print("----------------------")
    print("⏱ Intent Time: 0 (rule-based)")

    session.current_intent = intent

    # 3️⃣ GLOBAL ROUTER (Intent-Level)

    # identity_reply = identity_guard(agent, message)
    # if identity_reply:
    #     print("⏱ Total Message Time:", time.time() - start_time)
    #     return identity_reply, session_id

    #after testing changes=============
    # Skip identity guard for service/department queries
    is_service_query = any(word in service_keywords for word in words)

    if not is_service_query:
        identity_reply = identity_guard(agent, message)
        if identity_reply:
            print("⏱ Total Message Time:", time.time() - start_time)
            return identity_reply, session_id
        
        # 🔹 NEW: University identity guard (prevents adopting fake universities)
        uni_guard = university_identity_guard(agent, message)
        if uni_guard:
            print("⏱ Total Message Time:", time.time() - start_time)
            return uni_guard, session_id


    print("AGENT SUMMARY FROM DB:", agent.summary)
    if intent == "greeting" and not session.state.get("intro_shown"):

        role_name = agent.role_template.role_name if agent.role_template else "assistant"

        summary = agent.summary or ""

        reply = f"""
    Hello! I'm the {role_name} at {agent.company_name or agent.name}.

    {summary}

    How can I assist you today?
    """

        # mark intro shown so it never repeats
        state = session.state or {}
        state["intro_shown"] = True
        session.state = state
        session.save()

        print("⏱ Total Message Time:", time.time() - start_time)

        return reply.strip(), session_id
    
    if intent == "bot_wellbeing":
        reply = (
            f"I'm doing well, thank you for asking!\n\n"
            f"I'm here to help you with {agent.company_name or agent.name} services. "
            f"How can I assist you today?"
        )
        print("⏱ Total Message Time:", time.time() - start_time)
        return reply, session_id

    # if intent == "complaint":
    #     reply = complaint_handler_strategy(agent, message, session)
    #     print("⏱ Total Message Time:", time.time() - start_time)
    #     return reply, session_id

    role_name = agent.role_template.role_name
    strategy_type = get_role_strategy(role_name)

    # ✅ 1️⃣ Dedicated Site Visit Scheduler (ISOLATED)
    if role_name == "Site Visit Scheduler":

        msg = message.lower()

        # 🔹 If booking flow already active → continue
        if session.stage in [
            "collecting_property",
            "collecting_name",
            "collecting_date",
            "collecting_time",
            "confirming"
        ]:
            reply = site_visit_transaction_strategy(agent, message, session)

        # 🔹 If user explicitly wants to book → start flow
        elif any(phrase in msg for phrase in [
            "schedule site visit",
            "book a visit",
            "arrange visit",
            "schedule a visit",
            "see the property"
        ]):
            session.stage = None
            session.state = {}
            session.save()
            reply = site_visit_transaction_strategy(agent, message, session)

        # 🔹 Otherwise → behave like knowledge bot
        else:
            reply = information_strategy(agent, message, session)

    # 🔥 Only for Appointment Scheduler (transaction type)
    # elif strategy_type == "transaction":
    elif strategy_type == "transaction" and role_name != "Site Visit Scheduler":
        # 1️⃣ If booking flow is currently active → continue it
        if session.stage in ["collecting_name","collecting_date", "collecting_time", "confirming","completed"]:
            reply = transaction_strategy(agent, message, session)
 
        # 2️⃣ If user explicitly wants to book → start transaction
        # elif (
        #     intent == "appointment_request"
        #     or any(word in message.lower() for word in ["book", "appointment", "schedule"])
        # ):
        # 2️⃣ If user explicitly wants to book OR update → start transaction
            # Reset previous state
            # session.stage = None
            # session.state = {}
            # session.save()
            # reply = transaction_strategy(agent, message, session)
            #==change after testing

        elif (
            intent in ["appointment_request", "appointment_update"]
            or any(word in message.lower() for word in ["book", "appointment", "schedule", "update", "change", "reschedule"])
        ):

            if intent == "appointment_update":
                session.stage = "collecting_date"
                state = session.state or {}
                state.pop("date", None)
                state.pop("time", None)
                session.state = state
                session.save()

            session.stage = None if intent == "appointment_request" else session.stage
            session.save()

            reply = transaction_strategy(agent, message, session)
 
        # 3️⃣ Otherwise → treat as knowledge question
        else:
            reply = information_strategy(agent, message, session)

    # 🛡️ Insurance Advisor Dedicated Flow
    elif strategy_type == "insurance_transaction":
        reply = insurance_transaction_strategy(agent, message, session)

    elif strategy_type == "mutual_fund_advisor":
        reply = mutual_fund_advisor_strategy(agent, message, session)

    elif strategy_type == "investment_advisor":
        reply = investment_advisor_strategy(agent, message, session)
 
    elif strategy_type == "support":
 
        # 🔹 If booking intent → start transaction flow
        if (
            intent in ["booking_request", "appointment_request"]
            or any(word in message.lower() for word in ["book", "appointment", "schedule"])
            or session.stage in ["collecting_name", "collecting_date", "collecting_time", "confirming"]
        ):
            reply = transaction_strategy(agent, message, session)
 
        else:
            reply = support_strategy(agent, message, session)
 
 
    elif strategy_type == "qualification":
        reply = qualification_strategy(agent, message, session)

    elif strategy_type == "education_qualification":

    # If already in qualification flow → continue
        if session.state.get("interest") or session.state.get("background"):
            reply = education_qualification_strategy(agent, message, session)

        # If user clearly expressing career intent → start qualification
        elif intent in ["general_query", "information_request"] and any(
            word in message.lower() for word in ["career", "become", "interested", "want to"]
        ):
            reply = education_qualification_strategy(agent, message, session)

        # Otherwise → treat as normal information
        else:
            reply = information_strategy(agent, message, session)


    elif strategy_type == "education_scholarship":
        reply = education_scholarship_strategy(agent, message, session)

    elif strategy_type == "education_support":
        reply = education_support_strategy(agent, message, session)

    elif strategy_type == "recruitment_advisory":
        reply = recruitment_advisory_strategy(agent, message, session)

    elif strategy_type == "hr_helpdesk":
        reply = hr_helpdesk_strategy(agent, message, session)


    elif strategy_type == "onboarding_support":
        reply = onboarding_support_strategy(agent, message, session)

    elif strategy_type == "sales":
        reply = sales_strategy(agent, message, session)

    elif strategy_type == "lead_qualification":
        reply = lead_qualification_strategy(agent, message, session)

    elif strategy_type == "product_demo":
        reply = product_demo_strategy(agent, message, session)

    elif strategy_type == "customer_support":
        reply = customer_support_strategy(agent, message, session)

    elif strategy_type == "complaint_handler":
        reply = complaint_handler_strategy(agent, message, session)

    elif strategy_type == "returns_refund":
        reply = returns_refund_strategy(agent, message, session)

    elif strategy_type == "escalation_manager":
        reply = escalation_manager_strategy(agent, message, session)

    elif strategy_type == "loan_financial":
        reply = loan_financial_strategy(agent, message, session)
 
    elif strategy_type == "smart_real_estate":

        msg = message.lower()

        if any(word in msg for word in [
            "2bhk", "3bhk", "villa", "flat", "apartment",
            "budget", "lakh", "cr", "property", "looking"
        ]):
            reply = qualification_strategy(agent, message, session)

        # 🔹 Everything else → normal info
        else:
            reply = information_strategy(agent, message, session)
 
    elif strategy_type == "hotel_booking":
            reply = hotel_booking_strategy(agent, message, session)

    elif strategy_type == "restaurant_booking":
            reply = restaurant_booking_strategy(agent, message, session)

    elif strategy_type == "travel_planner":
            reply = travel_planner_strategy(agent, message, session)

    # 🔹 Safety fallback
    if 'reply' not in locals():
        reply = information_strategy(agent, message, session)


    return reply, session_id




#*/************///////////////////////////***************************//////////////////////////////////////////
#reduce time backup code



# from knowledge.services.retriever import retrieve_relevant_chunks
# from conversations.models import ConversationSession
# from conversations.services.core.behavior_router import get_role_strategy
# from conversations.services.core.strategies import (
#     identity_guard,
#     information_strategy,
#     hotel_booking_strategy,
#     restaurant_booking_strategy,
#     travel_planner_strategy,
#     recruitment_advisory_strategy,
#     hr_helpdesk_strategy,
#     onboarding_support_strategy,
#     education_qualification_strategy,
#     education_scholarship_strategy,
#     education_support_strategy,
#     qualification_strategy,
#     support_strategy,
#     loan_financial_strategy,
#     site_visit_transaction_strategy,
# )
# import uuid
# import time
# STRATEGY_MAP = {
#     "information": information_strategy,
#     "hotel_booking": hotel_booking_strategy,
#     "restaurant_booking": restaurant_booking_strategy,
#     "travel_planner": travel_planner_strategy,
#     "recruitment_advisory": recruitment_advisory_strategy,
#     "hr_helpdesk": hr_helpdesk_strategy,
#     "onboarding_support": onboarding_support_strategy,
#     "education_qualification": education_qualification_strategy,
#     "education_scholarship": education_scholarship_strategy,
#     "education_support": education_support_strategy,
#     "qualification": qualification_strategy,
#     "support": support_strategy,
#     "loan_financial": loan_financial_strategy,
#     "transaction": site_visit_transaction_strategy,
# }

# def process_message(agent, message, session_id=None):

#     import uuid
#     from conversations.models import ConversationSession
#     from conversations.services.core.behavior_router import get_role_strategy
#     from conversations.services.core.strategies import (
#         identity_guard,
#         information_strategy,
#         education_qualification_strategy,
#         hr_helpdesk_strategy,
#         onboarding_support_strategy,
#         transaction_strategy,
#         qualification_strategy,
#         support_strategy,
#         loan_financial_strategy,
#         education_scholarship_strategy,
#         education_support_strategy,
#         travel_planner_strategy,
#         restaurant_booking_strategy,
#         hotel_booking_strategy,
#         recruitment_advisory_strategy,
#     )

#     # =========================================================
#     # 1️⃣ Create / Load Session
#     # =========================================================

#     if not session_id:
#         session_id = str(uuid.uuid4())

#     session, _ = ConversationSession.objects.get_or_create(
#         agent=agent,
#         session_id=session_id
#     )

#     msg = message.lower().strip()

#     role_name = agent.role_template.role_name
#     strategy_type = get_role_strategy(role_name)

#     STRATEGY_MAP = {
#         "information": information_strategy,
#         "hotel_booking": hotel_booking_strategy,
#         "restaurant_booking": restaurant_booking_strategy,
#         "travel_planner": travel_planner_strategy,
#         "recruitment_advisory": recruitment_advisory_strategy,
#         "hr_helpdesk": hr_helpdesk_strategy,
#         "onboarding_support": onboarding_support_strategy,
#         "education_qualification": education_qualification_strategy,
#         "education_scholarship": education_scholarship_strategy,
#         "education_support": education_support_strategy,
#         "qualification": qualification_strategy,
#         "support": support_strategy,
#         "loan_financial": loan_financial_strategy,
#         "transaction": transaction_strategy,
#     }

#     strategy_function = STRATEGY_MAP.get(strategy_type, information_strategy)

#     # =========================================================
#     # 2️⃣ GREETING FOR NEW SESSION
#     # =========================================================

#     if not session.stage and not session.state:
#         return (
#             f"Hello! Welcome to {agent.company_name}. "
#             "How can I assist you today?",
#             session_id
#         )

#     # =========================================================
#     # 3️⃣ IDENTITY GUARD
#     # =========================================================

#     identity_reply = identity_guard(agent, message)
#     if identity_reply:
#         return identity_reply, session_id

#     # =========================================================
#     # 4️⃣ CONTINUE ACTIVE FLOW
#     # =========================================================

#     if session.stage:
#         reply = strategy_function(agent, message, session)
#         return reply, session_id

#     # =========================================================
#     # 5️⃣ NORMAL STRATEGY ROUTING
#     # =========================================================

#     reply = strategy_function(agent, message, session)

#     return reply, session_id