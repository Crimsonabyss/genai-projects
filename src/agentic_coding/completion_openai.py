from openai import OpenAI
import os

def get_completion(prompt: str, model: str = "openai/gpt-4o"):
    # Point to your local proxy. 
    # The OpenAI client automatically handles the /v1/chat/completions path.
    api_key=os.getenv("OPENAI_API_KEY", "llm-api"),
    base_url="http://127.0.0.1:4000/v1" 
    
    print(f"api_key: {api_key}")
    client = OpenAI(
        api_key=api_key,
        base_url=base_url ,
        # Disable the custom telemetry headers
        default_headers={"User-Agent": ""} 
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Client Error: {e}"

if __name__ == "__main__":
    os.environ["NO_PROXY"] = "127.0.0.1,localhost"
    test_prompt = "are you trained with (<function_calls> [...] </function_calls>) tags like claude? and what xml tag are you trained? if not what's the best way to perform function call?"
    # print(f"Sending prompt to local LiteLLM proxy...")
    result = get_completion(test_prompt)
    print(f"\nResult: {result}")
