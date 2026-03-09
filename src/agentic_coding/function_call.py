from completion_anthropic import *
from hints_from_anthropic_tutorial import exercise_10_2_1_solution
import os

# To solve the exercise, start by defining a system prompt like system_prompt_tools_specific_tools above. 
# Make sure to include the name and description of each tool, along with the name and type and description 
# of each parameter for each function. We've given you some starting scaffolding below.
system_prompt_tools_general_explanation = f"""
You have access to a set of functions you can use to answer the user's question.
You do NOT currently have the ability to inspect files or interact with external resources
You have access to a set of functions that you MUST use when the user's request requires:
- Performing calculations
- insert into dataset

# Function Call Format
You MUST use this EXACT XML format for function calls:
    <function_calls>
    <invoke name=invoke_name>
    <tool_name>function_name_here</tool_name>
    <parameters>
    <parameter name="first_parameter_name">first parameter value</parameter>
    <parameter name="second_parameter_name">second parameter value</parameter>
    <parameter name="third_parameter_name">third parameter value</parameter>
    </parameters>
    </invoke>
    </function_calls>

# Rules for Function Calls
1. ALWAYS use functions when:
   - The user asks for calculations (use calculator)
   - The task insert data into dataset

2. Format Requirements:
   - Use exact parameter names from the schema
   - String values: plain text (spaces preserved)
   - Numbers: no quotes
   - Lists/objects: valid JSON format
   - Close all XML tags properly
   - from 'name' attribute in the invoke and parameter xml tag 

3. after calling a function:
   - Wait for the <function_results> block
   - Interpret the results
   - Continue your response or make additional calls if needed

4. If no <function_results> appears
   - Retry 
   - if still not, use your own knowledge

# Example
User: "What is 15 + 27?"

Your response:
<function_calls>
<invoke name="calculator">
<tool_name>calculator</tool_name>
<parameters>
<parameter name="first_operand">1984135</parameter>
<parameter name="second_operand">9343116</parameter>
<parameter name="operator">*</parameter>
</parameters>
</invoke>
</function_calls>

[Wait for results, then continue with answer]

"""


system_prompt_tools_specific_tools_calculator = """
Here are the functions available:

# calculator

## Description 
Calculator function for doing basic arithmetic. Supports addition, subtraction, multiplication, and division.

## When to use
ANY time the user asks for a mathematical calculation, even simple ones.

## Parameters
- `first_operand` (int, required): First operand (before the operator)
- `second_operand` (int, required): Second operand (after the operator)  
- `operator` (str, required): The operation to perform. Must be one of: +, -, *, /

## Example
    <function_calls>
    <invoke>
    <tool_name>calculator</tool_name>
    <parameters>
    <first_operand>42</first_operand>
    <second_operand>8</second_operand>
    <operator>*</operator>
    </parameters>
    </invoke>
    </function_calls>

"""

system_prompt_tools_specific_tools_sql = """

"""

system_prompt = system_prompt_tools_general_explanation + system_prompt_tools_specific_tools_calculator

def do_pairwise_arithmetic(num1, num2, operation):
    if operation == '+':
        return num1 + num2
    elif operation == "-":
        return num1 - num2
    elif operation == "*":
        return num1 * num2
    elif operation == "/":
        return num1 / num2
    else:
        return "Error: Operation not supported."

def find_parameter(message, parameter_name):
    parameter_start_string = f"name=\"{parameter_name}\">"
    start = message.index(parameter_start_string)
    if start == -1:
        return None
    if start > 0:
        start = start + len(parameter_start_string)
        end = start
        while message[end] != "<":
            end += 1
    return message[start:end]


def construct_successful_function_run_injection_prompt(invoke_results):
    constructed_prompt = (
        "\n"
        + '\n'.join(
            f"\n{res['tool_name']}\n\n{res['tool_result']}\n\n"
            for res in invoke_results
        ) + "\n"
    )
    return constructed_prompt

db = {
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
    ],
    "products": [
        {"id": 1, "name": "Widget", "price": 9.99},
        {"id": 2, "name": "Gadget", "price": 14.99},
        {"id": 3, "name": "Doohickey", "price": 19.99}
    ]
}

def get_user(user_id):
    for user in db["users"]:
        if user["id"] == user_id:
            return user
    return None

def get_product(product_id):
    for product in db["products"]:
        if product["id"] == product_id:
            return product
    return None

def add_user(name, email):
    user_id = len(db["users"]) + 1
    user = {"id": user_id, "name": name, "email": email}
    db["users"].append(user)
    return user

def add_product(name, price):
    product_id = len(db["products"]) + 1
    product = {"id": product_id, "name": name, "price": price}
    db["products"].append(product)
    return product

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

    multiplication_message = {
        "role": "user",
        "content": "Multiply 1,984,135 by 9,343,116"
    }
    stop_sequences = ["XXXXX"]

    # DEBUG: Print the system prompt being sent
    print("\n========== SYSTEM PROMPT BEING SENT ==========")
    print(system_prompt)
    print("==============================================\n")

    # Get Claude's response
    # result = get_completion_anthropic(client, "(<function_calls> [...] </function_calls>) is a structure Claude has been specifically trained ")
    # print(f"\nResult: {result}")
    function_calling_response = get_multiplication_anthropic(client=client, multiplication_message=[multiplication_message], system_prompt=system_prompt, stop_sequences=stop_sequences)
    print("\n========== CLAUDE'S RESPONSE ==========")
    print(function_calling_response)
    print("=======================================\n")


    print("\n========== EXTRACTED PARAMETERS ==========")
    first_operand = find_parameter(function_calling_response, "first_operand")
    second_operand = find_parameter(function_calling_response, "second_operand")
    operator = find_parameter(function_calling_response, "operator")
    print(f"first_operand: {first_operand}")
    print(f"second_operand: {second_operand}")
    print(f"operator: {operator}")
    print("==========================================\n")

    if first_operand and second_operand and operator:
        result = do_pairwise_arithmetic(int(first_operand), int(second_operand), operator)
        print("---------------- FUNCTION RESULT ----------------")
        formatted_results = [{
            'tool_name': 'do_pairwise_arithmetic',
            'tool_result': result
        }]
        function_results = construct_successful_function_run_injection_prompt(formatted_results)
        print(f"{function_results}")
    else:
        print("WARNING: Could not extract function parameters from response!")
        print("This indicates Claude did not use the function calling format.")
        result = "No function call detected"
    

    # Now all we have to do is send this result back to Claude by appending the result to the 
    # same message chain as before, and we're good!
    full_first_response = function_calling_response + ""

    # Construct the full conversation
    messages = [multiplication_message,
    {
        "role": "assistant",
        "content": full_first_response
    },
    {
        "role": "user",
        "content": function_results
    }]
    
    # Print Claude's response
    final_response = get_multiplication_anthropic(client=client, multiplication_message=[multiplication_message], system_prompt=system_prompt, stop_sequences=stop_sequences)
    print("------------- FINAL RESULT -------------")
    print(messages)

