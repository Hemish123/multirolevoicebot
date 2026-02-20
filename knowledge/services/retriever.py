# from knowledge.models import KnowledgeChunk


# def retrieve_relevant_chunks(agent, query, limit=3):
#     chunks = KnowledgeChunk.objects.filter(
#         knowledge_file__agent=agent
#     )[:limit]

#     return "\n\n".join([c.content for c in chunks])















from knowledge.models import KnowledgeChunk
from conversations.services.azure_openai_service import generate_response
import json
import re


# def retrieve_relevant_chunks(agent, query, limit=3):
#     chunks = KnowledgeChunk.objects.filter(
#         knowledge_file__agent=agent
#     )

#     chunk_map = {str(i): chunk.content for i, chunk in enumerate(chunks)}

#     # Prepare chunk summary for GPT
#     chunk_list_text = "\n\n".join(
#         [f"{i}: {chunk.content[:300]}" for i, chunk in enumerate(chunks)]
#     )

#     retrieval_prompt =  f"""
# You are a retrieval system.

# From the list of document chunks below,
# select the chunk numbers that best answer the user question.

# IMPORTANT:
# - Return ONLY a valid JSON list.
# - Do NOT explain.
# - Do NOT write text.
# - Do NOT wrap in markdown.
# - Example valid output: [1, 3]

# User Question:
# {query}

# Chunks:
# {chunk_list_text}
# """

#     response = generate_response("You are a retrieval system.", retrieval_prompt)

#     try:
#         json_text = re.search(r"\[.*?\]", response).group()
#         indexes = json.loads(json_text)
#     except:
#         indexes = []

#     selected_chunks = [
#         chunk_map[str(i)] for i in indexes if str(i) in chunk_map
#     ]

#     return "\n\n".join(selected_chunks[:limit])




STOP_WORDS = {
    "what", "is", "are", "the", "a", "an", "in", "on", "of", "for", "to",
    "and", "or", "does", "do", "how", "much", "many", "please", "tell",
    "me", "about", "give", "show", "list", "explain"
}

NUMERIC_HINT_WORDS = {
    "fee", "fees", "cost", "price", "amount",
    "seat", "seats", "intake", "quota",
    "aiq", "gq", "mq", "nri"
}


# -------------------------
# Utility functions
# -------------------------

def normalize(text: str) -> str:
    """
    Normalize text for matching:
    - lowercase
    - remove symbols except numbers and $
    """
    return re.sub(r"[^a-z0-9$ ]+", " ", text.lower())


def extract_keywords(query: str):
    normalized = normalize(query)
    return [
        w for w in normalized.split()
        if w not in STOP_WORDS and len(w) > 2
    ]


def is_numeric_query(query: str) -> bool:
    q = query.lower()
    return any(word in q for word in NUMERIC_HINT_WORDS) or any(
        char.isdigit() for char in q
    )


# -------------------------
# Main Retriever
# -------------------------

def retrieve_relevant_chunks(agent, query, limit=5):
    """
    Returns concatenated relevant document chunks.
    If nothing relevant is found, returns empty string.
    """

    chunks = KnowledgeChunk.objects.filter(
        knowledge_file__agent=agent
    )

    if not chunks.exists():
        return ""

    keywords = extract_keywords(query)
    numeric_query = is_numeric_query(query)

    # --------------------------------------------------
    # STEP 1: Keyword + Score-based Retrieval (Primary)
    # --------------------------------------------------

    scored_chunks = []

    for chunk in chunks:
        content = chunk.content
        normalized_content = normalize(content)

        score = 0

        # keyword matching
        for kw in keywords:
            if kw in normalized_content:
                score += 2

        # numeric relevance boost
        if numeric_query:
            digit_count = sum(c.isdigit() for c in content)
            score += min(digit_count, 10)

        # college-name boost
        if "," in content and any(k in normalized_content for k in keywords):
            score += 2

        if score > 0:
            scored_chunks.append((score, content))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    if scored_chunks:
        return "\n\n".join(
            [c for _, c in scored_chunks[:limit]]
        )

    # --------------------------------------------------
    # STEP 2: STRICT LLM FALLBACK (NO GUESSING)
    # --------------------------------------------------

    chunk_map = {
        str(i): chunk.content
        for i, chunk in enumerate(chunks)
    }

    chunk_preview = "\n\n".join(
        f"{i}: {chunk.content[:400]}"
        for i, chunk in enumerate(chunks)
    )

    retrieval_prompt = f"""
You are a STRICT document retrieval system.

Rules:
- Select chunks ONLY if they clearly contain the answer
- If the answer is NOT present, return []
- Do NOT guess or infer
- Return ONLY a JSON array like [0, 2]

User Question:
{query}

Document Chunks:
{chunk_preview}
"""

    response = generate_response(
        system_prompt="You retrieve document chunks only.",
        user_prompt=retrieval_prompt
    )

    indexes = []

    try:
        match = re.search(r"\[[0-9,\s]*\]", response)
        if match:
            indexes = json.loads(match.group())
    except Exception:
        indexes = []

    selected_chunks = [
        chunk_map[str(i)]
        for i in indexes
        if str(i) in chunk_map
    ]

    if not selected_chunks:
        return ""
