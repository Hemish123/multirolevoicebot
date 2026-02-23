# # conversations/services/core/dialogue_engine.py

# from knowledge.services.retriever import retrieve_relevant_chunks
# from conversations.services.azure_openai_service import generate_response
# from conversations.services.core.memory_manager import (
#     load_conversation_history,
#     save_conversation
# )
# from conversations.services.core.intent_classifier import classify_intent
# def process_message(agent, message):
#     """
#     Global conversation processor with intent classification.
#     """

#     # 1️⃣ Classify intent
#     intent_data = classify_intent(message)
#     intent = intent_data.get("intent", "unknown")

#     # 2️⃣ Load memory
#     history = load_conversation_history(agent)

#     # 3️⃣ Retrieve knowledge
#     context = retrieve_relevant_chunks(agent, message)

#     # 4️⃣ Guardrail: no knowledge
#     if not context.strip():
#         reply = "This information is not mentioned in the uploaded document."
#         save_conversation(agent, message, reply)
#         return reply

#     # 5️⃣ Build system prompt
#     system_prompt = f"""
# {agent.resolved_prompt}

# Detected Intent: {intent}

# Conversation History:
# {history}

# Knowledge Context:
# {context}

# Rules:
# - Answer ONLY using knowledge context
# - If information is missing, say:
#   "This information is not mentioned in the uploaded document."
# - Do NOT hallucinate
# """

#     reply = generate_response(system_prompt, message)

#     # 6️⃣ Save conversation
#     save_conversation(agent, message, reply)

#     return reply





# from knowledge.services.retriever import retrieve_relevant_chunks
# from conversations.services.azure_openai_service import generate_response
# from conversations.services.core.memory_manager import (
#     load_conversation_history,
#     save_conversation
# )
# from conversations.services.core.intent_classifier import classify_intent


# def process_message(agent, message):

#     # 1️⃣ Detect Intent
#     intent_data = classify_intent(message)
#     intent = intent_data.get("intent", "unknown")

#     # 2️⃣ GLOBAL CONVERSATIONAL ROUTER
#     if intent == "greeting":
#         reply = f"""
# Hello! Welcome to {agent.company_name or agent.name}.How can I assist you today?
# """.strip()

#         save_conversation(agent, message, reply)
#         return reply

#     if intent == "complaint":
#         reply = "I'm sorry to hear that. Could you please provide more details so I can assist you better?"
#         save_conversation(agent, message, reply)
#         return reply

#     # 3️⃣ Load Memory
#     history = load_conversation_history(agent)

#     # 4️⃣ Retrieve Knowledge
#     context = retrieve_relevant_chunks(agent, message)

#     # 5️⃣ Guardrail for Knowledge Questions
#     if not context.strip():
#         reply = "This information is not mentioned in the uploaded document."
#         save_conversation(agent, message, reply)
#         return reply

#     # 6️⃣ Build System Prompt
#     system_prompt = f"""
# {agent.resolved_prompt}

# Detected Intent: {intent}

# Conversation History:
# {history}

# Knowledge Context:
# {context}

# Rules:
# - Answer ONLY using knowledge context
# - If information is missing, say:
#   "This information is not mentioned in the uploaded document."
# - Do NOT hallucinate
# """

#     reply = generate_response(system_prompt, message)

#     save_conversation(agent, message, reply)

#     return reply




from knowledge.services.retriever import retrieve_relevant_chunks
from conversations.services.azure_openai_service import generate_response
from conversations.services.core.intent_classifier import classify_intent
from conversations.models import ConversationSession
import uuid


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
    session.current_intent = intent

    # 3️⃣ GLOBAL ROUTER (Intent-Level)

    if intent == "greeting":
        reply = f"Hello! Welcome to {agent.company_name or agent.name}. How can I assist you today?"
        session.stage = "active"
        session.save()
        return reply, session_id

    if intent == "complaint":
        reply = "I'm sorry to hear that. Could you please provide more details so I can assist you better?"
        session.stage = "handling_complaint"
        session.save()
        return reply, session_id

    if intent == "emergency":
        reply = "If this is an emergency, please contact local emergency services immediately."
        session.stage = "emergency"
        session.save()
        return reply, session_id

    # 4️⃣ Knowledge-Based Flow (RAG)
    context = retrieve_relevant_chunks(agent, message)

    if not context.strip():
        reply = "This information is not mentioned in the uploaded document."
        session.save()
        return reply, session_id

    # 5️⃣ Build Conversational Prompt
    system_prompt = f"""
{agent.resolved_prompt}

Detected Intent: {intent}

Conversation Stage: {session.stage or "new"}

Knowledge Context:
{context}

Rules:
- Respond conversationally like a human professional.
- Use only the knowledge context.
- If information is missing, say:
  "This information is not mentioned in the uploaded document."
- Do NOT hallucinate.
"""

    reply = generate_response(system_prompt, message)

    session.stage = "active"
    session.save()

    return reply, session_id