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


#**********************/////////////////////**********************/////////////////
#reduce time backup code

# from openai import AzureOpenAI
# from django.conf import settings
# import time

# client = AzureOpenAI(
#     api_key=settings.AZURE_OPENAI_API_KEY,
#     azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
#     api_version=settings.AZURE_OPENAI_API_VERSION,
# )

# def generate_response(system_prompt, user_message):

#     start_time = time.time()

#     response = client.chat.completions.create(
#         model=settings.AZURE_OPENAI_DEPLOYMENT,
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_message},
#         ],
#         temperature=0.3,
#         max_tokens=300,
#         top_p=0.9,
#     )

#     result = response.choices[0].message.content.strip()

#     end_time = time.time()
#     print("🔥 GPT CALL TIME:", round(end_time - start_time, 2), "seconds")

#     return result


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
