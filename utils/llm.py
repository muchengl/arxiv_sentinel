import os

import openai

openai.api_key = os.getenv('OPENAI_API_KEY')

client = openai.OpenAI(
    api_key=openai.api_key,
)

def invoke_llm(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o",
            max_tokens=3000,
        )

        output = response.choices[0].message.content
    except Exception as e:
        output = f"Exception: {e}"

    return output