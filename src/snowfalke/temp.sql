SELECT SNOWFLAKE.CORTEX.COMPLETE( 
    'llama2-70b-chat', 
    [ 
        {'role': 'system', 'content': 'You are a helpful AI assistant. Analyze the movie review text and determine the overall sentiment. Answer with just \"Positive\", \"Negative\", or \"Neutral\"' }, 
        {'role': 'user', 'content': 'this was really good'} 
    ] ,
    {
        'temperature': 0.7,
        'max_tokens': 10
    }
) as response; 

GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE consultant;
