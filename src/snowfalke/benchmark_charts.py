# Import python packages
import streamlit as st
import altair as alt
import pandas as pd 
import math
from snowflake.snowpark.context import get_active_session

session = get_active_session()
conn = st.experimental_connection('snowpark')

def get_data_insights(df):
    completion_model = 'llama3-8b'

    msg_system = """
        I want you to act as a professional Data analyist.
        do not make up information that is not in the dataset. say 'no relevant information'
        For each analysis I ask for, provide me with the exact and definitive answer
    """
    
    msg_prompt = """
        # CONTEXT # 
        I work for Vivanti, we are IT consultant company, and we are doing a benchmark comparsion between three data warehouse products on the market: Snowflake, Databricks and Bigquery
        
        ############# 
        # OBJECTIVE # 
        I want you analysis the dataset provide in <<< >>> 
        
        The columns and the meaning of each column from the dataset I will provide you are: 
        -- DATA_WAREHOUSE: database name
        -- ENGINE_SIZE: the size of the compute power (exclude bigquery, marked as 'NA')
        -- DATA_VOLUME: the size of the data set for benchmark queries, the data set may no contains all the data_volumne list downbelow
            --- SF1: 9.46 million rows
            --- SF10: 94.6 million rows
            --- SF100: 946 million rows 
            --- SF1000: 9.46 billion rows 
            --- SF10000: 94.6 billion rows 
        
        -- CONCUTTENCY: how many sql we let the database to run at the same time. remember the sql may stay in the queue
        -- QUERY_TYPE: Transactional(Single Row Retrieval); Reporting (Large Aggregation / Joins / Filters); Analytical Queries (Large Time Series / CTEs / Window functions); Highly Concurrent Workloads (All the above, simultaneously, forcing queries to queue)
        -- TOTAL_ELAPSED_TIME: total time cost queries to run 
        -- TOTAL_QUERY_COST: the cost to run the query 
        
        =============
        COMPARSION: how does each DATA_WAREHOUSE perform compare to the other databases in regard to the TOTAL_ELAPSED_TIME and TOTAL_QUERY_COST base on their ENGINE_SIZE, DATA_VOLUME, CONCUTTENCY and QUERY_TYPE. what is the strenth and weakness of each database?
        
        ############# 
        
        # STYLE # 
        technical analytics report
        
        ############# 
        
        # TONE # 
        Professional, technical
        
        ############# 
        
        # AUDIENCE # 
        Clients, business partners
        they can easily understand 
         
        ############# 
        
        # RESPONSE # 
        Write a short pargraph for each database and comparison between the database
        the length of the output can fit into 2 presentation slides 
        do not make up information that is not in the dataset. say 'no relevant information'
        
        ############# 
        the data set you need to analysis is: 
    """
    
    # df is shit 
    csv_string = df.drop(columns=['DW']).to_csv(index=False)

    sql_string = f"""select snowflake.cortex.complete(
                                '{completion_model}', 
                                $$
                                    {prompt}
                                    <<<
                                    {csv_string}
                                    >>>
                                $$) as INSIGHT
             """

    return session.sql(sql_string).collect()[0]["INSIGHT"]


def display_chart(df, data_volume, query_type, time_cost, processes):
    con = ''
    # scale_max = math.ceil(df[time_cost].max())

    if processes == 2 : 
        con = '8-32'
    else : 
        con = '32-128'

    if time_cost == 'TOTAL_ELAPSED_TIME_SECONDS':
        dfTime = df.drop(columns=["TOTAL_QUERY_COST"])
        
        dfMelted = dfTime.melt(
            id_vars=['DW', 'DATA_WAREHOUSE', 'SIZE_ORDER', 'SESSIONS', 'PROCESSES'],
            value_vars=['TOTAL_EXECUTION_TIME_SECONDS', 'TOTAL_QUEUED_OVERLOAD_TIME_SECONDS', 'TOTAL_OTHER_OVERLOAD_TIME_SECONDS'],
            var_name='TIME_SECONDS',
            value_name='Time'
        )
        dfMelted['DW_TIME'] = dfMelted['DW'] + ' -- ' + dfMelted['TIME_SECONDS']
        color_range = alt.Scale(scheme='tableau20')
    
        chart = alt.Chart(dfMelted).mark_bar().encode(
            x=alt.X('DW:N', sort=engine_size_order, axis=alt.Axis(title='', labelFontSize=0)),
            y=alt.Y('sum(Time):Q', axis=alt.Axis(title='Total Time (s)')),
            # color=alt.Color('DW:N', scale=color_scale, legend=None),
            color=alt.Color('DW_TIME:N', scale=color_range, legend=None),
            column='SESSIONS:O',
            order=alt.Order(
                  # Sort the segments of the bars by this field
                  'TIME_SECONDS',
                  sort='ascending'
                ),
            tooltip=['DW', 'DATA_WAREHOUSE', 'SESSIONS', 'TIME_SECONDS', 'Time']
        ).properties(
            width=alt.Step(15),
            title=f'No scale: Query type: {query_type} | Data Volume: {data_volume} | SESSIONS: {con} | meansure by: {time_cost}'
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )
    
        st.altair_chart(chart)
    elif time_cost == 'TOTAL_QUERY_COST':
        dfCost = df.drop(columns=['TOTAL_EXECUTION_TIME_SECONDS', 'TOTAL_QUEUED_OVERLOAD_TIME_SECONDS', 'TOTAL_OTHER_OVERLOAD_TIME_SECONDS'])
        
        chart1 = alt.Chart(dfCost).mark_bar().encode(
            x=alt.X('DW:N', sort=engine_size_order, axis=alt.Axis(title='', labelFontSize=0)),
            # y=alt.Y(f'{time_cost}:Q', scale=alt.Scale(type='log'), axis=alt.Axis(title=time_cost)),
            y=alt.Y(f'{time_cost}:Q', axis=alt.Axis(title=time_cost)),
            # color=alt.Color('DW:N', scale=color_scale, legend=alt.Legend(title="Platform", labelFontSize=14, titleFontSize=14, labelLimit=300, orient="right")),
            # color=alt.Color('DW:N', scale=color_scale, legend=None),
            column='SESSIONS:O'
        ).properties(
            width=alt.Step(15),
            title=f'No scale: Query type: {query_type} | Data Volume: {data_volume} | SESSIONS: {con} | meansure by: {time_cost}'
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )
    
        # chart2 = alt.Chart(dfSub).mark_bar().encode(
        #     x=alt.X('DW:N', sort=engine_size_order, axis=alt.Axis(title='', labelFontSize=0)),
        #     y=alt.Y(f'{time_cost}:Q', scale=alt.Scale(type='log'), axis=alt.Axis(title=time_cost)),
        #     # y=alt.Y(f'{time_cost}:Q', axis=alt.Axis(title=time_cost)),
        #     # color=alt.Color('DW:N', scale=color_scale, legend=alt.Legend(title="Database:")),
        #     color=alt.Color('DW:N', scale=color_scale, legend=None),
        #     column='SESSIONS:O'
        # ).properties(
        #     width=alt.Step(15),
        #     title=f'scale: Query type: {query_type} | Data Volume: {data_volume} | SESSIONS: {con} | meansure by: {time_cost}'
        # ).configure_axis(
        #     labelFontSize=12,
        #     titleFontSize=14
        # ).configure_title(
        #     fontSize=16
        # )

        st.altair_chart(chart1)
        # st.altair_chart(chart2)

    
    ######################## does NOT work ###########################
    # # color_range = alt.Scale(scheme='tableau20')
    # color_scales = {
    #     'Snowflake': alt.Scale(scheme='blues'),
    #     'Databricks': alt.Scale(scheme='reds'),
    #     'Bigquery': alt.Scale(scheme='greens'),
    #     'Redshift': alt.Scale(scheme='yellows'),
    # }
    
    # charts = []
    # for warehouse in dfMelted['DATA_WAREHOUSE'].unique():
    #     chart = alt.Chart(dfMelted[dfMelted['DATA_WAREHOUSE'] == warehouse]).mark_bar().encode(
    #         x=alt.X('DW:N', sort=engine_size_order, axis=alt.Axis(title='', labelFontSize=0)),
    #         y=alt.Y('sum(Time):Q', axis=alt.Axis(title='Total Time (s)')),
    #         # color=alt.Color('DW:N', scale=color_scale, legend=None),
    #         color=alt.Color('DW_TIME:N', scale=color_scales[warehouse], sort=time_type_order, legend=None),
    #         column='SESSIONS:O',
    #         tooltip=['DW', 'DATA_WAREHOUSE', 'SESSIONS', 'TIME_SECONDS', 'Time']
    #     ).properties(
    #         width=alt.Step(15),
    #         title=f'No scale: Query type: {query_type} | Data Volume: {data_volume} | SESSIONS: {con} | meansure by: {time_cost}'
    #     )
    #     charts.append(chart)

    # final_chart = alt.vconcat(*charts).configure_axis(
    #         labelFontSize=12,
    #         titleFontSize=14
    #     ).configure_title(
    #         fontSize=16
    #     )
        
    # st.altair_chart(final_chart)
    
    
    # chart1 = alt.Chart(dfSub).mark_bar().encode(
    #     x=alt.X('DW:N', sort=engine_size_order, axis=alt.Axis(title='', labelFontSize=0)),
    #     # y=alt.Y(f'{time_cost}:Q', scale=alt.Scale(type='log'), axis=alt.Axis(title=time_cost)),
    #     y=alt.Y(f'{time_cost}:Q', axis=alt.Axis(title=time_cost)),
    #     # color=alt.Color('DW:N', scale=color_scale, legend=alt.Legend(title="Platform", labelFontSize=14, titleFontSize=14, labelLimit=300, orient="right")),
    #     color=alt.Color('DW:N', scale=color_scale, legend=None),
    #     column='SESSIONS:O'
    # ).properties(
    #     width=alt.Step(15),
    #     title=f'No scale: Query type: {query_type} | Data Volume: {data_volume} | SESSIONS: {con} | meansure by: {time_cost}'
    # ).configure_axis(
    #     labelFontSize=12,
    #     titleFontSize=14
    # ).configure_title(
    #     fontSize=16
    # )

    # chart2 = alt.Chart(dfSub).mark_bar().encode(
    #     x=alt.X('DW:N', sort=engine_size_order, axis=alt.Axis(title='', labelFontSize=0)),
    #     y=alt.Y(f'{time_cost}:Q', scale=alt.Scale(type='log'), axis=alt.Axis(title=time_cost)),
    #     # y=alt.Y(f'{time_cost}:Q', axis=alt.Axis(title=time_cost)),
    #     # color=alt.Color('DW:N', scale=color_scale, legend=alt.Legend(title="Database:")),
    #     color=alt.Color('DW:N', scale=color_scale, legend=None),
    #     column='SESSIONS:O'
    # ).properties(
    #     width=alt.Step(15),
    #     title=f'scale: Query type: {query_type} | Data Volume: {data_volume} | SESSIONS: {con} | meansure by: {time_cost}'
    # ).configure_axis(
    #     labelFontSize=12,
    #     titleFontSize=14
    # ).configure_title(
    #     fontSize=16
    # )

    

# Define color scale
color_scale = alt.Scale(domain=[
    'Snowflake--X-Small', 'Snowflake--Small', 'Snowflake--Medium', 'Snowflake--Large', 'Snowflake--X-Large', 
    'Databricks--2X-Small', 'Databricks--X-Small', 'Databricks--Small', 'Databricks--Medium', 'Databricks--Large', 'Databricks--X-Large', 
    'Bigquery--N/A',
    'Redshift--ns-benchmark-8-8', 'Redshift--ns-benchmark-16-16', 'Redshift--ns-benchmark-8-64', 'Redshift--ns-benchmark-32-32', 'Redshift--ns-benchmark-64-64'],
                        range=[
    '#CCCCFF', '#9999FF', '#6666FF', '#3333FF', '#0000CC',
    '#FFCCCC', '#FF9999', '#FF6666', '#FF3333', '#CC0000', '#630100',
    '#00CC00',
    '#FFFF99', '#fce3a7', '#edca79', '#ad7b0c', '#523800'
])
engine_size_order = [
    'Snowflake--X-Small', 'Snowflake--Small', 'Snowflake--Medium', 'Snowflake--Large', 'Snowflake--X-Large', 
    'Databricks--2X-Small', 'Databricks--X-Small', 'Databricks--Small', 'Databricks--Medium', 'Databricks--Large', 'Databricks--X-Large', 
    'Bigquery--N/A',
    'Redshift--ns-benchmark-8-8', 'Redshift--ns-benchmark-16-16', 'Redshift--ns-benchmark-8-64', 'Redshift--ns-benchmark-32-32', 'Redshift--ns-benchmark-64-64']
qurey_typies = ["Baseline", "Transaction", "Report", "Analytic"]	
data_volume = ["sf1", "sf10", "sf100"]	
time_cost = ["TOTAL_ELAPSED_TIME_SECONDS", "TOTAL_QUERY_COST"]
processes = [2, 8]
# qurey_typies = ["Baseline"]	
# data_volume = ["sf1"]	
# time_cost = ["TOTAL_ELAPSED_TIME_SECONDS"]
# processes = [2, 8]

    
queriesSfview = """
    SELECT 
        DATA_WAREHOUSE || '--' || ENGINE_SIZE as DW
        , DATA_WAREHOUSE
        , ENGINE_SIZE
        , case 
            when ENGINE_SIZE = 'N/A' then 0
            when ENGINE_SIZE = '2X-Small' then 1
            when ENGINE_SIZE = 'X-Small' then 2
            when ENGINE_SIZE = 'Small' then 3
            when ENGINE_SIZE = 'Medium' then 4
            when ENGINE_SIZE = 'Large' then 5
            when ENGINE_SIZE = 'X-Large' then 6
            when ENGINE_SIZE = 'ns-benchmark-8-8' then 7
            when ENGINE_SIZE = 'ns-benchmark-16-16' then 8
            when ENGINE_SIZE = 'ns-benchmark-8-64' then 9
        end as size_order
        , DATA_VOLUME
        , SESSIONS
        , PROCESSES
        , THREADS
        , QUERY_TYPE 
        , sum(ELAPSED_TIME_SECONDS) TOTAL_ELAPSED_TIME_SECONDS
        , sum(cost_per_query_$_v2) TOTAL_QUERY_COST
        , sum(queued_overload_time_seconds) TOTAL_QUEUED_OVERLOAD_TIME_SECONDS
        , sum(execution_time_seconds) TOTAL_EXECUTION_TIME_SECONDS
        , sum(OTHER_OVERLOAD_TIME_SECONDS) TOTAL_OTHER_OVERLOAD_TIME_SECONDS
    from BENCHMARK_REPORTING.BENCHMARK_REPORTING.QUERIES_REPORT
    group by 
        DW 
        , DATA_WAREHOUSE
        , ENGINE_SIZE
        , SIZE_ORDER
        , DATA_VOLUME
        , SESSIONS
        , PROCESSES
        , THREADS
        , QUERY_TYPE
"""
dfAll = session.sql(queriesSfview).to_pandas()

for query_type in qurey_typies:
    for vol in data_volume:
        for tc in time_cost:
            for ps in processes:
                # select the subset 
                dfSub = dfAll.query(f'DATA_VOLUME == "{vol}" & QUERY_TYPE == "{query_type}" & PROCESSES == {ps}')\
                        [["DW", "DATA_WAREHOUSE", "SIZE_ORDER", "SESSIONS", "PROCESSES", "TOTAL_QUERY_COST", "TOTAL_QUEUED_OVERLOAD_TIME_SECONDS", "TOTAL_EXECUTION_TIME_SECONDS", "TOTAL_OTHER_OVERLOAD_TIME_SECONDS"]]
                # dfSub.sort_values(by=["DATA_WAREHOUSE", "SIZE_ORDER", "SESSIONS"])
                display_chart(dfSub, vol, query_type, tc, ps)
                # st.write(dfSub)
                # resp = get_data_insights(dfSub)
                # st.write(resp)
