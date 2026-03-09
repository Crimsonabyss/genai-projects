from litellm import completion, _turn_on_debug
import os
import sys

##################################### NOT WORKING #####################################

def get_completion(prompt: str, model: str = "openai/gpt-4o"):
    # 1. Get the base URL #os.getenv("OPENAI_BASE_URL", "http://0.0.0.0:4000/v1")
    base_url =  "http://0.0.0.0:4000" 
    api_key = os.getenv("OPENAI_API_KEY", "llm-api")
    
    print(f"Using base URL: {base_url}", flush=True)
    print(f"Using model: {model}", flush=True)
    
    response = completion(
        model=model,
        api_base=base_url,
        api_key=api_key,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.0,
        # This force-tells LiteLLM to treat the endpoint as an OpenAI-compatible proxy
        # custom_llm_provider="openai" 
    )
    return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    import traceback
    
    print("=" * 60, flush=True)
    print("LiteLLM Proxy Test", flush=True)
    print("=" * 60, flush=True)
    
    # Check environment variables
    base_url = "http://0.0.0.0:4000" # os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not base_url:
        print("⚠️  Warning: OPENAI_BASE_URL not set, using default: http://0.0.0.0:4000", flush=True)
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY not set, using default", flush=True)
    
    print(f"Base URL: {base_url or 'http://0.0.0.0:4000'}", flush=True)
    print("=" * 60, flush=True)
    
    # Enable debug mode to see detailed logs
    # _turn_on_debug()
    
    test_prompt = "What is the capital of France?"
    print(f"\nSending prompt: {test_prompt}", flush=True)
    print("-" * 60, flush=True)
    
    result = get_completion(test_prompt, model="openai/gpt-4o")
    
    print("-" * 60, flush=True)
    print(f"✓ Success! Response: {result}", flush=True)
    print("=" * 60, flush=True)
    
    # try:
    #     print(f"\nSending prompt: {test_prompt}", flush=True)
    #     print("-" * 60, flush=True)
        
    #     result = get_completion(test_prompt, model="gpt-4o")
        
    #     print("-" * 60, flush=True)
    #     print(f"✓ Success! Response: {result}", flush=True)
    #     print("=" * 60, flush=True)
        
    # except Exception as e:
    #     print("\n" + "=" * 60, flush=True)
    #     print("✗ ERROR", flush=True)
    #     print("=" * 60, flush=True)
    #     print(f"Error: {e}", flush=True)
    #     print(f"Type: {type(e).__name__}", flush=True)
    #     print("\nFull traceback:", flush=True)
    #     traceback.print_exc(file=sys.stdout)
    #     print("=" * 60, flush=True)
    #     sys.exit(1)

