from anthropic import Anthropic
import os

def get_completion_anthropic(client : Anthropic, prompt):
    try:
        # 3. Use the messages.create method 'model' must match the 'model_name' in your config.yaml
        message = client.messages.create(
            model="bedrock/anthropic.claude-4-5-sonnet",
            # max_tokens: the maximum number of tokens to generate before stopping. 
            # Note that Claude may stop before reaching this maximum. 
            max_tokens=1024,
            # an array of input messages.
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        
        # Return the text from the first content block
        return message.content[0].text

    except Exception as e:
        return f"Anthropic SDK Error: {e}"

def get_multiplication_anthropic(client : Anthropic, multiplication_message : list, system_prompt : str, stop_sequences : str):
    try:
        message = client.messages.create(
            model="bedrock/anthropic.claude-4-5-sonnet",
            max_tokens=1024,
            # an array of input messages.
            system=system_prompt,
            messages=multiplication_message,
            stop_sequences=stop_sequences
        )
        
        # Return the text from the first content block
        return message.content[0].text

    except Exception as e:
        return f"Anthropic SDK Error: {e}"
    
if __name__ == "__main__":
    # 1. This prevents your local call from being hijacked by a corporate/VPN gateway
    os.environ["NO_PROXY"] = "127.0.0.1,localhost,0.0.0.0"

    # 2. Initialize Anthropic client pointing to your local Proxy
    # Note: Anthropic SDK uses /v1/messages, which LiteLLM Proxy supports
    client = Anthropic(
        base_url="http://127.0.0.1:4000", 
        api_key=os.getenv("ANTHROPIC_AUTH_TOKEN") # Placeholder; real auth is in your Proxy/AWS
    )
    print("Connecting to LiteLLM Proxy via Anthropic SDK...")
    result = get_completion_anthropic(client, "(<function_calls> [...] </function_calls>) is a structure Claude has been specifically trained ")
    print(f"\nResult: {result}")

