import streamlit as st
import pandas as pd 
import numpy as np
# import altair as alt 
# import time 

from snowflake.snowpark.context import get_active_session
# Get the current credentials
# this is the setp to get the cridential of the session
session = get_active_session()
# Initialize connection.
conn = st.experimental_connection('snowpark')

def get_data_insights(prompt, data):
    completion_model = '    llama3-8b'

    prompt_prefix = """
        You are an assistant helping derive insights from a dataset containing order information from a good company. 
        I will provide you with a question and a dataset, and you will respond
        Provide answers based only on the provided data. 
        the data I provide you is weekly forecase data, so your respond should also analyis the data by week
        step 1: 
            What forecast are trending base on the item price?
            Are there any days of the week where forecast overperform or underperform?

        step 2:            
            provde me a sales strategy, what week should I run the sales compain? 
        
        Respond with a nutual analytical tone, Limit your response to 200 words.
    """

    if type(data) == pd.core.frame.DataFrame:
        data_string = data.to_string(index=False)
    else:
        data_string = data.to_pandas().to_string(index=False)

    prompt = f"""select snowflake.cortex.complete(
                                '{completion_model}', 
                                $$
                                    {prompt_prefix}
                                    {prompt}
                                    ###
                                    {data_string}
                                    ###
                                $$) as INSIGHT
             """

    return session.sql(prompt).collect()[0]["INSIGHT"]

# title 
st.title("Snowflake editable table for forecast")
st.header("Update the unit price")

# 2nd exercise, user input
sftable_future = "DEMO_DB.FORECAST.PATTIES_FUTURE_SALES"
df_user_input = session.table(sftable_future).to_pandas()

# create a spark dataframe
with st.form("forecast write"):
    st.write("Note down users' discount price")
    edit_df = st.data_editor(df_user_input, use_container_width=True)
    snowpark_df = session.create_dataframe(edit_df)
    write_to_snowflake = st.form_submit_button("Update")

if write_to_snowflake:
    with st.spinner("Re-creating the forecast..."):
        snowpark_df.write.mode("overwrite").save_as_table(sftable_future)
    st.success("forecast pricing updated")

st.header("Forecast")
result = session.sql("CALL forecast.produce_forecast()").collect()

# Convert the result to a pandas DataFrame if needed
df = pd.DataFrame(result, columns=['customer', 'SKU', 'week', 'forecast', 'unit_price', 'lower_bound', 'upper_bound'])
df1 = df[['week', 'SKU', 'forecast', 'unit_price']]

# display the line
df['unit_price'] = df['unit_price'].apply(lambda x: x*500)
st.line_chart(df, x="week", y=["forecast", "unit_price"], color=['#1725c2', '#e0bc09'])

st.header("Insignt")
resp = get_data_insights(f""" """, df1)
st.write("Insights:")
st.write(resp)
