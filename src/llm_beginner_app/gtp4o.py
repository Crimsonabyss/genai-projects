from promptEngineering.config import *
from openai import OpenAI

def get_completion(prompt, model=CONFIG['LLM']['model'], temperature=0):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature # this is the degree of randomness of the model's output
    )
    return response.choices[0].message.content

client = OpenAI(
    api_key = OPENAI_PEK
)

prompt = f"""
Generate a list of three made-up book titles along with their authors and genres. 
Provide them in JSON format with the following keys: 
book_id, title, author, genre.
"""

response = get_completion(prompt=prompt, temperature=0)
print(response)

