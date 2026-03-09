import streamlit as st 
from promptEngineering.config import * 
from src.llmFrameworks.responsefunctions import generate_response
from src.llmFrameworks.langChainBeginner import *

st.set_page_config(page_title="")
st.title('Prompt Engineering App powered by: ' + CONFIG["LLM"]["model"])


with st.form("prompt_form"):
    team_name_rendered = prompt_template_team.format(city='Sydney', colour='red')
    st.write(f"langchain template: {team_name_rendered}") 
    st.write(f"template file is saved at: {file}")
    st.write(jdata)

    # render the prompt, specify the variable in the format funciton only
    team_lineup_rendered = prompt_template_team_lineup.format(lineup_format='sniper, grenadier, rifleman and shield positions')
    
    # text = st.text_area(f"langchain template: {rendered}, and the template is ")
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.info(generate_response(team_name_rendered))
        st.info(generate_response(team_lineup_rendered))


with st.form("few_shots_form"):
    fewShotPromptRandered = fewShotTemp_player.format(input="MATHIEU HERBAUT")
    st.write(f"Few shots rendered: ") 
    st.write(f"{fewShotPromptRandered}")
    
    submitted = st.form_submit_button("Show Answer")
    if submitted:
        st.info(generate_response(fewShotPromptRandered))
    