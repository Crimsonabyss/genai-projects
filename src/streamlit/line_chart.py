import streamlit as st
import pandas as pd
import numpy as np
import altair as alt 
import time

from snowflake.snowpark.context import get_active_session
session = get_active_session()

# title 
st.title("Snowflake editable table ")
companies = ["C1", 'C2', "C3", "C4", "C5"]

# set date range, 10 days
dates = pd.date_range(end=pd.Timestamp.today(), periods=10)

# first exercise - not tried, create graph
# create editable dataframe
@st.cache_data()
def generate_data():
    df = pd.DataFrame()

    data_list = []
    for company in companies:
        data = pd.DataFrame(
            {
                "Date": dates,
                "Company": company,
                "Active_Users": np.random.randint(10, 50, size=10),
                "Time_Spent": np.random.randint(5000, 20000, size=10),
            }
        )

        # Appending the data to data frame
        data_list.append(data)
    
    # reset the index
    df = pd.concat(data_list)
    df.reset_index(drop=True, inplace=True)
    
    return df

df = generate_data()
st.header("companies' active user all")
st.write(df)

pre_avg = df.drop(columns=["Date"])
averages = pre_avg.groupby(["Company"]).sum()
# add new column 
averages["Chart"] = False 

# display df
averages = st.experimental_data_editor(averages, use_container_width=True)

# select companies
selected_companies = averages[averages["Chart"] == True].index.to_list()

# subset of selected companies 
df_subset = df[df["Company"].isin(selected_companies)]

# select a variable 
variable = st.selectbox("Select a variable to chart", ["Active_Users", "Time_Spent"])

# create chart oject 
chart = (
    alt.Chart(df_subset)
        .mark_line(point=True)
        .encode(
            x="monthdate(Date):T",
            y=f"{variable}:Q",
            color=alt.Color("Company:Q", scale=alt.Scale(scheme="tableau10")),
            tooltip=["Date", f"{variable}:Q"]
        )
)

if selected_companies:
    st.write(df_subset)
    st.altair_chart(chart, use_container_width=True)
    st.line_chart(df_subset, x="Date", y="Active_Users", color="Company", use_container_width=True)

