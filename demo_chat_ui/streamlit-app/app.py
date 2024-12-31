import streamlit as st
import pandas as pd
import requests
import json
import time

def generate_response(prompt):
    if prompt:
        import random
        
        answers = [
            "The answer lies in your heart",
            "I do not know",
            "Almost certainly",
            "No",
            "Yes",
            "Why do you need to ask?",
            "Go away. I do not wish to answer at this time.",
            "Time will only tell",
        ]
        return random.choice(answers)




st.write(st.__version__)
st.write("Hello!!!")

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]


# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# messages = st.container(height=300)
# if prompt := st.chat_input("Say something"):
#     messages.chat_message("user").write(prompt)
#     messages.chat_message("assistant").write(f"Echo: {prompt}")


# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)



# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            time.sleep(2)
            response = generate_response(prompt) 
            st.write(response) 
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)


# prompt = st.chat_input("Say something")


# messages = st.container(height=300)
# if prompt := st.chat_input("Say something"):
    # try:

    #     # r = requests.get('http://10.42.0.158:7002/retriver/files')
    #     print("After the Request...")
    #     data = eval(r.text)['data']

    #     messages.chat_message("ai").write(pd.DataFrame(data))
    # except requests.exceptions.RequestException as e:  # This is the correct syntax
    #     print("In the Exception....")
    #     st.write(e)
#     messages.chat_message("user").write(prompt)
#     print("Getting the Request...")
#     
        