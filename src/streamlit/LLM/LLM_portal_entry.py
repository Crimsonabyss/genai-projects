"""
This is a landing page for all LLM and Langchain/langgraph etc related application UI
each page should have a separate .py file for stream UI and one more for llm

Returns 
------- 
void 
""" 

import streamlit as st
st.title("LLM UI Portal")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

st.markdown("#### This is a landing page for all LLM and Langchain/langgraph etc related application UI")
st.markdown("#### Each page should have a separate .py file for stream UI and one more for LLM")
st.markdown("#### :red[run command:] `export PYTHONPATH=$(pwd)` in src folder and streamlit run ")
st.markdown("#### :red[⬅⬅⬅⬅⬅] Select from the side bar")
