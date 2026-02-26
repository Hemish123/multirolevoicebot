# # # conversations/services/core/dialogue_engine.py

# # from knowledge.services.retriever import retrieve_relevant_chunks
# # from conversations.services.azure_openai_service import generate_response
# # from conversations.services.core.memory_manager import (
# #     load_conversation_history,
# #     save_conversation
# # )
# # from conversations.services.core.intent_classifier import classify_intent
# # def process_message(agent, message):
# #     """
# #     Global conversation processor with intent classification.
# #     """

# #     # 1️⃣ Classify intent
# #     intent_data = classify_intent(message)
# #     intent = intent_data.get("intent", "unknown")

# #     # 2️⃣ Load memory
# #     history = load_conversation_history(agent)

# #     # 3️⃣ Retrieve knowledge
# #     context = retrieve_relevant_chunks(agent, message)

# #     # 4️⃣ Guardrail: no knowledge
# #     if not context.strip():
# #         reply = "This information is not mentioned in the uploaded document."
# #         save_conversation(agent, message, reply)
# #         return reply

# #     # 5️⃣ Build system prompt
# #     system_prompt = f"""
# # {agent.resolved_prompt}

# # Detected Intent: {intent}

# # Conversation History:
# # {history}

# # Knowledge Context:
# # {context}

# # Rules:
# # - Answer ONLY using knowledge context
# # - If information is missing, say:
# #   "This information is not mentioned in the uploaded document."
# # - Do NOT hallucinate
# # """

# #     reply = generate_response(system_prompt, message)

# #     # 6️⃣ Save conversation
# #     save_conversation(agent, message, reply)

# #     return reply





# # from knowledge.services.retriever import retrieve_relevant_chunks
# # from conversations.services.azure_openai_service import generate_response
# # from conversations.services.core.memory_manager import (
# #     load_conversation_history,
# #     save_conversation
# # )
# # from conversations.services.core.intent_classifier import classify_intent


# # def process_message(agent, message):

# #     # 1️⃣ Detect Intent
# #     intent_data = classify_intent(message)
# #     intent = intent_data.get("intent", "unknown")

# #     # 2️⃣ GLOBAL CONVERSATIONAL ROUTER
# #     if intent == "greeting":
# #         reply = f"""
# # Hello! Welcome to {agent.company_name or agent.name}.How can I assist you today?
# # """.strip()

# #         save_conversation(agent, message, reply)
# #         return reply

# #     if intent == "complaint":
# #         reply = "I'm sorry to hear that. Could you please provide more details so I can assist you better?"
# #         save_conversation(agent, message, reply)
# #         return reply

# #     # 3️⃣ Load Memory
# #     history = load_conversation_history(agent)

# #     # 4️⃣ Retrieve Knowledge
# #     context = retrieve_relevant_chunks(agent, message)

# #     # 5️⃣ Guardrail for Knowledge Questions
# #     if not context.strip():
# #         reply = "This information is not mentioned in the uploaded document."
# #         save_conversation(agent, message, reply)
# #         return reply

# #     # 6️⃣ Build System Prompt
# #     system_prompt = f"""
# # {agent.resolved_prompt}

# # Detected Intent: {intent}

# # Conversation History:
# # {history}

# # Knowledge Context:
# # {context}

# # Rules:
# # - Answer ONLY using knowledge context
# # - If information is missing, say:
# #   "This information is not mentioned in the uploaded document."
# # - Do NOT hallucinate
# # """

# #     reply = generate_response(system_prompt, message)

# #     save_conversation(agent, message, reply)

# #     return reply




# from knowledge.services.retriever import retrieve_relevant_chunks
# from conversations.services.azure_openai_service import generate_response
# from conversations.services.core.intent_classifier import classify_intent
# from conversations.models import ConversationSession
# import uuid
# from conversations.services.core.behavior_router import get_role_strategy
# from conversations.services.core.strategies import (
#     information_strategy,
#     transaction_strategy,
#     qualification_strategy,
#     support_strategy,
# )
 
 
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
 
#     if intent == "greeting" and not session.stage and not session.state:
#         reply = f"Hello! Welcome to {agent.company_name or agent.name}. How can I assist you today?"
#         return reply, session_id
 
#     if intent == "complaint":
#         reply = "I'm sorry to hear that. Could you please provide more details so I can assist you better?"
#         session.stage = "handling_complaint"
#         session.save()
#         return reply, session_id
 
#     # if intent == "emergency":
#     #     reply = "If this is an emergency, please contact local emergency services immediately."
#     #     session.stage = "emergency"
#     #     session.save()
#     #     return reply, session_id
   
 
#     role_name = agent.role_template.role_name
#     strategy_type = get_role_strategy(role_name)
 
#     # 🔥 Only for Appointment Scheduler (transaction type)
#     if strategy_type == "transaction":
 
#         # 1️⃣ If booking flow is currently active → continue it
#         if session.stage in ["collecting_name","collecting_date", "collecting_time", "confirming"]:
#             reply = transaction_strategy(agent, message, session)
 
#         # 2️⃣ If user explicitly wants to book → start transaction
#         elif (
#             intent == "appointment_request"
#             or any(word in message.lower() for word in ["book", "appointment", "schedule"])
#         ):
#             # Reset previous state
#             session.stage = None
#             session.state = {}
#             session.save()
#             reply = transaction_strategy(agent, message, session)
 
#         # 3️⃣ Otherwise → treat as knowledge question
#         else:
#             reply = information_strategy(agent, message, session)
 
#     elif strategy_type == "support":
 
#         # 🔹 If booking intent → start transaction flow
#         if (
#             intent in ["booking_request", "appointment_request"]
#             or any(word in message.lower() for word in ["book", "appointment", "schedule"])
#             or session.stage in ["collecting_name", "collecting_date", "collecting_time", "confirming"]
#         ):
#             reply = transaction_strategy(agent, message, session)
 
#         else:
#             reply = support_strategy(agent, message, session)
 
 
#     elif strategy_type == "qualification":
#         reply = qualification_strategy(agent, message, session)
 
#     elif strategy_type == "smart_real_estate":
 
#     # If booking intent → transaction
#         if intent in ["booking_request", "site_visit_request"]:
#             reply = transaction_strategy(agent, message, session)
 
#         # If buying / searching intent → qualification
#         elif any(word in message.lower() for word in [
#             "2bhk", "3bhk", "villa", "flat", "apartment",
#             "budget", "lakh", "cr", "property", "looking"
#         ]):
#             reply = qualification_strategy(agent, message, session)
 
#         # Otherwise → general information
#         else:
#             reply = information_strategy(agent, message, session)
 
#     else:
#         reply = information_strategy(agent, message, session)
 
    
#     # formatted_reply = ResponseFormatter.format(
#     #     reply,
#     #     strategy_type=strategy_type,
#     #     intent=intent,
#     #     agent_name=agent.name
#     #     )

#     return reply, session_id

# #     # 4️⃣ Knowledge-Based Flow (RAG)
# #     context = retrieve_relevant_chunks(agent, message)

# #     if not context.strip():
# #         reply = "This information is not mentioned in the uploaded document."
# #         session.save()
# #         return reply, session_id

# #     # 5️⃣ Build Conversational Prompt
# #     system_prompt = f"""
# # {agent.resolved_prompt}

# # Detected Intent: {intent}

# # Conversation Stage: {session.stage or "new"}

# # Knowledge Context:
# # {context}

# # Rules:
# # - Respond conversationally like a human professional.
# # - Use only the knowledge context.
# # - If information is missing, say:
# #   "This information is not mentioned in the uploaded document."
# # - Do NOT hallucinate.
# # """

# #     reply = generate_response(system_prompt, message)

# #     session.stage = "active"
# #     session.save()

# #     return reply, session_id















from knowledge.services.retriever import retrieve_relevant_chunks
from conversations.services.azure_openai_service import generate_response
from conversations.services.core.intent_classifier import classify_intent
from conversations.models import ConversationSession
import uuid
from conversations.services.core.behavior_router import get_role_strategy
from conversations.services.core.strategies import (
    education_qualification_strategy,
    information_strategy,
    transaction_strategy,
    qualification_strategy,
    support_strategy,
    site_visit_transaction_strategy,
    loan_financial_strategy,
    education_scholarship_strategy,
    education_support_strategy,
)
 
 
def process_message(agent, message, session_id=None):
 
    # 1️⃣ Create or Load Session
    if not session_id:
        session_id = str(uuid.uuid4())
 
    session, _ = ConversationSession.objects.get_or_create(
        agent=agent,
        session_id=session_id
    )
 
    # 2️⃣ Detect Intent (AI-based)
    intent_data = classify_intent(message)
    intent = intent_data.get("intent", "unknown")
    print("---- DEBUG START ----")
    print("MESSAGE:", message)
    print("INTENT:", intent)
    print("STAGE BEFORE:", session.stage)
    print("STATE BEFORE:", session.state)
    print("----------------------")
    session.current_intent = intent
 
    # 3️⃣ GLOBAL ROUTER (Intent-Level)
 
    if intent == "greeting" and not session.stage and not session.state:
        reply = f"Hello! Welcome to {agent.company_name or agent.name}. How can I assist you today?"
        return reply, session_id
 
    if intent == "complaint":
        reply = "I'm sorry to hear that. Could you please provide more details so I can assist you better?"
        session.stage = "handling_complaint"
        session.save()
        return reply, session_id
 


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
        if session.stage in ["collecting_name","collecting_date", "collecting_time", "confirming"]:
            reply = transaction_strategy(agent, message, session)
 
        # 2️⃣ If user explicitly wants to book → start transaction
        elif (
            intent == "appointment_request"
            or any(word in message.lower() for word in ["book", "appointment", "schedule"])
        ):
            # Reset previous state
            session.stage = None
            session.state = {}
            session.save()
            reply = transaction_strategy(agent, message, session)
 
        # 3️⃣ Otherwise → treat as knowledge question
        else:
            reply = information_strategy(agent, message, session)
 
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

    elif strategy_type == "information":
        reply = information_strategy(agent, message, session)



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
 
    

    return reply, session_id