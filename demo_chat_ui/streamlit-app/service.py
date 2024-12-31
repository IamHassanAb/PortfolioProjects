import requests
import streamlit as st

# My Method
from utils import *
from langchain_core.load import load, loads
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


embeddings = OpenAIEmbeddings()


#  Getting Categoiries
with st.sidebar:
    if "categories" not in st.session_state:
        response = requests.get("http://127.0.0.1:8000/get_categories")
        if response.status_code == 200:
            st.session_state.categories = response.json()
            # st.json(response.json())
        else:
            st.error("Failed to fetch catgories...")
    else:
        st.success("Categories already available in App....")


    options = st.multiselect(
        "What is your query about?",
        [cat['category'] for cat in st.session_state.categories]
    )

    st.write("You selected:", options)

    # Button For Generating Vectors
    if st.button("Generate Vector"):
        with st.spinner("Generating vector..."):
            if "retriever" not in st.session_state:
                response = requests.get("http://127.0.0.1:8000/generate_vector")  # Adjust URL as needed
                if response.status_code == 200:
                    vectorstore = FAISS.load_local("../index", embeddings,allow_dangerous_deserialization=True)
                    st.session_state.retriever = vectorstore.as_retriever()
                    st.success("Vector generated successfully!")
                    st.json(response.json())
                    # st.session_state.retriever = loads(response.json()["data"])
                else:
                    st.error("Failed to generate vector")
            else:
                st.success("Vector Already Available In App....")
    # # Initialize session state if not already present
    # if 'button_states' not in st.session_state:
    #     st.session_state.button_states = {cat['category']: False for cat in st.session_state.categories}


    # for cat in st.session_state.categories:
    #     button_clicked = st.button(f"{cat['category']} {'✔' if st.session_state.button_states[cat['category']] else '✘'}", key=cat['category'])
    #     if button_clicked:
    #         toggle_button(cat['category'])
    #     # st.session_state.button_states = {label: False for label in button_labels}

    # # Display the status of each button
    # st.write("Current button states:")
    # for label, state in st.session_state.button_states.items():
    #     st.write(f"{label}: {'Clicked' if state else 'Unclicked'}")








# st.logo("../SHeer Ghar-transparent.png")
# st.image("../SHeer Ghar-transparent.png")
st.title("ChatBot ⚖️",)

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Assuming generate_response is your function to get the response
            response = generate_response(prompt, st.session_state.retriever)
            
            # Initialize output as an empty string
            output = ''
            for text in response:
                output += text  # Concatenate each text chunk to output
                # You can yield text here if you're doing streaming output
                
            st.markdown(output)  # Display the final output in the assistant message
            
    message = {"role": "assistant", "content": output}
    st.session_state.messages.append(message)

st.divider()


# with st.form("my_form"):
#     text = st.text_area(
#         "Enter text:",
#         "Do cats have claws?",
#     )
#     submitted = st.form_submit_button("Submit")
#     if not openai_api_key.startswith("sk-"):
#         st.warning("Please enter your OpenAI API key!", icon="⚠")
#     if submitted and openai_api_key.startswith("sk-"):
#         generate_response(text)l