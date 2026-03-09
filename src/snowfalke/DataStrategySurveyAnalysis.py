# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import numpy as np

# Write directly to the app
st.title("Data Strategy Survey Analysis")

# Get the current credentials
session = get_active_session()

st.code('for i in range(8): foo()')

st.metric('My metric', 42, -2)

data = {
    'Role': ['Executive', 'Middle Management', 'First-Level Management', 'Associate / Non-Management'],
    'Count': [4, 12, 23, 64],
    'Percent': [0.039, 0.117, 0.223, 0.621]
}

str = f"""
Analyse the following JSON object and 
provide a short sentence, no more than 50 words, 
describing your interpretation of its contents: data
"""

st.write(str)

st.table(data)

# Initialize connection.
conn = st.experimental_connection('snowpark')

df = session.sql(f"""
    SELECT CONSUMER_COMPLAINT_NARRATIVE
    FROM CONSULTANT_DB.ALANBLUWOL.CONSUMER_COMPLAINTS
    LIMIT 10
""")

df.collect()

st.area_chart(df)
st.bar_chart(df)
st.line_chart(df)
