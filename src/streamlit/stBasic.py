"""create a basic streamlit interface
the triple qoute (\"\"\") style comment must be declared before the import
os it won't display on the webpage 

Parameters 
---------- 
st.session_state['num'] : int
keep the random number

Returns 
------- 
void 
""" 

import streamlit as st
import random 

st.title('Welcome to Number Guess')
st.write('### where you guess a number ')

if 'num' in st.session_state:
    num = st.session_state['num']
    # tips use prefix to indecate the input type. text meam a text box
    txt_guess = int(st.text_input('Enter a number between 1 and 5: ', 0))
else:
    num = random.randrange(1, 5)
    st.session_state['num'] = num
    txt_guess = int(st.text_input('Enter a number between 1 and 5: ', 0))

st.write('#### :red[the number you guess is:]', txt_guess)

# st always execute the script from top to  bottom enerytime it receive the event, 
# like user input or click button, it run the entire script
btn_start = st.button('Start Again')
if btn_start:
    num = random.randrange(1, 5)
    # ====>!! store the session value !!
    st.session_state['num'] = num 

btn_guess = st.button('Make Guess')
# btn_guess is a button, when click, it trigger the if statement. 
if btn_guess:
    if txt_guess == num:
        st.write('You Win')
        st.balloons()
    else:
        st.write('Sorry. Wrong number. Try again.')

btn_show = st.button('Show Number')
if btn_show:
    st.write('The number is ', num)
    st.write("session_state[num]:", st.session_state['num'])
""" test !!!  asefwaef aw"""
# 
with st.expander("Help..."):
    st.write('''
    Press Start and a random number between 1 and 5 will be generated.
    Try to guess the number by entering your guess in the text box and
    clicking "Make Guess"
    ''')

with st.sidebar:
    st.markdown('#### Copyright Acme Games 2023')
    st.success('Licencse Validated')
    st.slider('Rate this game: ', 0, 10) 

