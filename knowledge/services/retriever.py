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


def retrieve_relevant_chunks(agent, query, limit=3):
    chunks = KnowledgeChunk.objects.filter(
        knowledge_file__agent=agent
    )

    chunk_map = {str(i): chunk.content for i, chunk in enumerate(chunks)}

    # Prepare chunk summary for GPT
    chunk_list_text = "\n\n".join(
        [f"{i}: {chunk.content[:300]}" for i, chunk in enumerate(chunks)]
    )

    retrieval_prompt =  f"""
You are a retrieval system.

From the list of document chunks below,
select the chunk numbers that best answer the user question.

IMPORTANT:
- Return ONLY a valid JSON list.
- Do NOT explain.
- Do NOT write text.
- Do NOT wrap in markdown.
- Example valid output: [1, 3]

User Question:
{query}

Chunks:
{chunk_list_text}
"""

    response = generate_response("You are a retrieval system.", retrieval_prompt)

    try:
        json_text = re.search(r"\[.*?\]", response).group()
        indexes = json.loads(json_text)
    except:
        indexes = []

    selected_chunks = [
        chunk_map[str(i)] for i in indexes if str(i) in chunk_map
    ]

    return "\n\n".join(selected_chunks[:limit])