import os

import openai



def invoke_llm(prompt: str) -> str:
    openai.api_key = os.getenv('OPENAI_API_KEY')

    client = openai.OpenAI(
        api_key=openai.api_key,
    )

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

def invoke_local_llm(prompt: str) -> str:
    client = openai.OpenAI(
        base_url='http://localhost:11434/v1/',
        api_key='ollama',
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                'role': 'user',
                'content': 'How are you?',
            }
        ],
        model='llama3.2',
    )