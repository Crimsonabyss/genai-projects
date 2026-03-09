import streamlit as st
import altair as alt
import numpy as np
import pandas as pd


df1=pd.DataFrame(10*np.random.rand(4,3),index=["A","B","C","D"],columns=["I","J","K"])
df2=pd.DataFrame(10*np.random.rand(4,3),index=["A","B","C","D"],columns=["I","J","K"])
df3=pd.DataFrame(10*np.random.rand(4,3),index=["A","B","C","D"],columns=["I","J","K"])

def prep_df(df, name):
    df = df.stack().reset_index()
    df.columns = ['c1', 'c2', 'values']
    df['DF'] = name
    return df

df1 = prep_df(df1, 'DF1')
st.write(df1)
df2 = prep_df(df2, 'DF2')
st.write(df2)
df3 = prep_df(df3, 'DF3')
st.write(df3)

df = pd.concat([df1, df2, df3])
st.write(df)

# chart1 = alt.Chart(df).mark_bar().encode(
#     x=alt.X('c2:N', title=None),
#     y=alt.Y('sum(values):Q', axis=alt.Axis(grid=False, title=None)),
#     column=alt.Column('c1:N', title=None),
#     color=alt.Color('DF:N', scale=alt.Scale(range=['#96ceb4', '#ffcc5c','#ff6f69']))
# ).configure_view(
#     strokeOpacity=0    
# )

# st.altair_chart(chart1) 

