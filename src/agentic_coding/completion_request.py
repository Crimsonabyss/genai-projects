import requests
import json
import os

def get_completion(prompt, model="openai/gpt-4o"):
    # Using 127.0.0.1 is more stable for local Python-to-Proxy comms
    url = "http://127.0.0.1:4000/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', 'anything')}"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error {response.status_code}: {response.text}"

if __name__ == "__main__":
    # Test OpenAI
    print("Testing OpenAI...")
    print(get_completion("What is 2+2?", model="openai/gpt-4o"))
    
    print("\n" + "-"*30 + "\n")
    
    # Test Anthropic via Bedrock
    print("Testing Anthropic...")
    print(get_completion("What is the capital of France?", model="bedrock/anthropic.claude-4-sonnet"))
    