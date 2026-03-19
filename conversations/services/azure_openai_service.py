# from openai import AzureOpenAI
# from django.conf import settings

# client = AzureOpenAI(
#     api_key=settings.AZURE_OPENAI_API_KEY,
#     azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
#     api_version=settings.AZURE_OPENAI_API_VERSION,
# )


# def generate_response(system_prompt, user_message):
#     response = client.chat.completions.create(
#         model=settings.AZURE_OPENAI_DEPLOYMENT,  # deployment name
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_message},
#         ],
#         temperature=0.7,
#     )

#     return response.choices[0].message.content


from openai import AzureOpenAI
from django.conf import settings
import time  # ✅ added

client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_version=settings.AZURE_OPENAI_API_VERSION,
)


def generate_response(system_prompt, user_message):
    llm_start = time.time()  # ✅ start timer

    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
    )

    print("⏱ LLM Time:", time.time() - llm_start)  # ✅ log time

    return response.choices[0].message.content