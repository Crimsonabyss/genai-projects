# import os
import openai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) 

# connect to open ai
kf = open("./DLAI-PEK", "r")
key = kf.read()
client = OpenAI(
    api_key = key
)

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0 # this is the degree of randomness of the model's output
    )
    return response.choices[0].message.content

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )

    # return the entire message not just on input 
    return response.choices[0].message

"""
The first message is the system message as an overall instruction, and follow by the user message  
Then will be a series of user and assistant inputs  
This allows the model remember the context  

LLM can only remember the name if you pass the whole context in.  
"""
messages =  [  
    {'role':'system', 'content':'You are friendly chatbot.'},
    {'role':'user', 'content':'Hi, my name is Isa'},
    {'role':'assistant', 'content': "Hi Isa! It's nice to meet you. Is there anything I can help you with today?"},
    {'role':'user', 'content':'Yes, you can remind me, What is my name?'}  
]
# response = get_completion_from_messages(messages, temperature=1)
# print(str(response))


context = [ {'role':'system', 'content':"""
You are OrderBot, an automated service to collect orders for a pizza restaurant. \
You first greet the customer, then collects the order, and then asks if it's a pickup or delivery. \
You wait to collect the entire order, then summarize it and check for a final time if the customer wants to add anything else. \
If it's a delivery, you ask for an address. \
Finally you collect the payment.\
Make sure to clarify all options, extras and sizes to uniquely identify the item from the menu.\
You respond in a short, very conversational friendly style. \
The menu includes: \
    pepperoni pizza  12.95, 10.00, 7.00 \
    cheese pizza   10.95, 9.25, 6.50 \
    eggplant pizza   11.95, 9.75, 6.75 \
    fries 4.50, 3.50 \
    greek salad 7.25 \
    Toppings: \
    extra cheese 2.00, \
    mushrooms 1.50 \
    sausage 3.00 \
    canadian bacon 3.50 \
    AI sauce 1.50 \
    peppers 1.00 \
    Drinks: \
    coke 3.00, 2.00, 1.00 \
    sprite 3.00, 2.00, 1.00 \
    bottled water 5.00 \
"""} ] 

### conversation .... 
userInput = input("Order anything: ")
msg = {"role": "user", "content": userInput}
context.append(msg)

response = get_completion_from_messages(messages=context, temperature=0.5)
print(response.content)

# update the system message 
messages =  context.copy()
messages.append(
{'role':'system', 'content':"""create a json summary of the previous food order. \
 Itemize the price for each item The fields should be: \
    1) pizza, include size \
    2) list of toppings \
    3) list of drinks, include size  \
    4) list of sides include size  5)total price """},    
)
 #The fields should be 1) pizza, price 2) list of toppings 3) list of drinks, include size include price  4) list of sides include size include price, 5)total price '},    

# ser temp to 0 for consistant output 
response = get_completion_from_messages(messages, temperature=0)
print(response)

