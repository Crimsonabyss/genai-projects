import json 
from promptEngineering.config import * 
from langchain.prompts.prompt import PromptTemplate
from langchain.prompts import load_prompt
from langchain.prompts.few_shot import FewShotPromptTemplate

# define the template to reuse 
prompt_template_team = PromptTemplate(
  input_variables = ['city', 'colour'],
  template = "Create a esport team name from {city} and main colour is: {colour} for the CS GO competition"
)

prompt_template_team.save(os.path.dirname(__file__) + "/longChainBeginner_template_team.json")
load_prompt = load_prompt(os.path.dirname(__file__) + "/longChainBeginner_template_team.json")
file = open(os.path.dirname(__file__) + "/longChainBeginner_template_team.json") 
jdata = json.load(file)

# 2nd format, do not need to specify the variables, see how it get rendered below
# do not create the PromptTemp class but use the **method** 
prompt_template_team_lineup = PromptTemplate.from_template(
    template="Make up a lineup for the esport team for the CS GO competition, use a {lineup_format}"
)
# output is in the streamlit 


# few-shot template 
# you can put real work and data in, the LLM will do the search for you on line and 
# fullfill the template 
shots = [
    {
        "player" : "Havard 'Rain' Nygaard",
        "teams": "FaZe Clan",
        "country" : "Norway",
        "stats" : """ 
        teamplay: 88
        skills: 86
        consistency: 93
        exp: 99
        media: 94
        """
    },
    {
        "player" : "Finn 'karrigan' Andersen",
        "teams": "MOUZ, FaZe Clan",
        "country" : "Norway",
        "stats" : """ 
        teamplay: 78
        skills: 73
        consistency: 97
        exp: 99
        media: 98
        """
    },
    {
        "player" : "Robin 'ROPZ' Kool",
        "teams": "FaZe Clan",
        "country" : "Montenegro",
        "stats" : """ 
        teamplay: 89
        skills: 92
        consistency: 94
        exp: 99
        media: 99
        """
    }
]

promteTemp_player = PromptTemplate(
    input_variables=["player", "country", "stats"], 
    template="player: {player},\n{country},\n{teams},\nstats:{stats}"
)

# actual prompt 
fewShotTemp_player = FewShotPromptTemplate(
    examples=shots,
    example_prompt=promteTemp_player,
    suffix="Player: {input}",
    input_variables=["input"]
)

