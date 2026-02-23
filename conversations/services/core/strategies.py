from knowledge.services.retriever import retrieve_relevant_chunks
from conversations.services.azure_openai_service import generate_response


def information_strategy(agent, message, session):
    context = retrieve_relevant_chunks(agent, message)

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

    # 🔹 HANDLE POST-COMPLETION POLITELY
    if session.stage == "completed":

    # If polite closing
        if any(word in message.lower() for word in ["thank", "thanks", "okay", "ok"]):
            return "You're welcome! If you need anything else, feel free to ask."

        # 🔥 NEW: If new question after completion → RESET SESSION
        session.stage = None
        session.state = {}
        session.save()

        # Now let main router handle it as new request
        return information_strategy(agent, message, session)


    # STAGE 1: Ask for date
    if not state.get("date"):
        if session.stage == "collecting_date":
            state["date"] = message
            session.state = state
            session.stage = "collecting_time"
            session.save()
            return "Thank you. Could you please provide the preferred time?"

        session.stage = "collecting_date"
        session.save()
        return "Sure. Could you please provide the preferred date?"

    # STAGE 2: Ask for time
    if not state.get("time"):
        if session.stage == "collecting_time":
            state["time"] = message
            session.state = state
            session.stage = "confirming"
            session.save()
            return f"Thank you. To confirm, your appointment is on {state['date']} at {state['time']}. Should I proceed?"

        session.state = state
        session.stage = "collecting_time"
        session.save()
        return "Could you please provide the preferred time?"

    # STAGE 3: Confirmation
    if session.stage == "confirming":
        if "yes" in message.lower():
            session.stage = "completed"
            session.state = {}
            session.save()
            return "Your appointment has been successfully scheduled. Thank you!"
        else:
            session.state = state
            session.stage = "collecting_date"
            session.save()
            return "No problem. Let's start again. What date would you prefer?"

    return "How can I assist you further?"


def qualification_strategy(agent, message, session):

    state = session.state or {}

    # STEP 1: Collect need
    if not state.get("need"):
        if session.stage == "collecting_need":
            state["need"] = message
            session.state = state
            session.stage = "collecting_budget"
            session.save()
            return "Thank you. Do you have a specific budget range in mind?"

        session.stage = "collecting_need"
        session.save()
        return "May I know what exactly you are looking for?"

    # STEP 2: Collect budget
    if not state.get("budget"):
        if session.stage == "collecting_budget":
            state["budget"] = message
            session.state = state
            session.stage = "advising"
            session.save()

            context = retrieve_relevant_chunks(agent, state["need"])

            system_prompt = f"""
{agent.resolved_prompt}

You are guiding a potential customer.

Customer Need: {state['need']}
Budget: {state['budget']}

Knowledge Context:
{context}

Respond persuasively and professionally.
"""

            return generate_response(system_prompt, message)

        session.stage = "collecting_budget"
        session.save()
        return "Do you have a specific budget range in mind?"

    return "How can I assist you further?"