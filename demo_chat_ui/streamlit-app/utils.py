import time
import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate,ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# from langchain.chains import LLMChain
from langchain.schema.output_parser import StrOutputParser

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def generate_response(input_text, vector_store_retriever):
    print("RequestIn: Generate ChatBot Response.")
    template = """Imagine there are three legal expert required to answer legal queries based only on the following context:
    {context}

    Please ensure your answers:
    1. Are based solely on the provided context.
    2. Include specific references to the relevant sections of the law.
    3. Are structured with a brief overview followed by detailed information if necessary.
    4. Offer clarity on any ambiguous queries by asking for additional details if needed.
     experts are answering this question.

    Examples:
    Question: When can police arrest without a warrant?
    Answer: 
    Police can arrest without a warrant in the following situations:
    1. If a person is involved in a cognizable offence or against whom a reasonable complaint has been made, or credible information has been received.
    2. If a person is found in possession of implements of housebreaking without lawful excuse.
    3. If a person is proclaimed as an offender.
    4. If a person obstructs a police officer in their duties.

    References:
    THE CODE OF CRIMINAL PROCEDURE, 1898, CHAPTER V OF ARREST, ESCAPE AND RETAKING, Section 54.

    Question: When can an inquiry or trial take place?
    Answer:
    An inquiry or trial can occur within the local limits of the jurisdiction where the offense was committed or where the consequences ensued.

    References:
    THE CODE OF CRIMINAL PROCEDURE, 1898, PART VI PROCEEDINGS IN PROSECUTIONS, CHAPTER XV OF THE JURISDICTION OF THE CRIMINAL COURTS IN INQUIRIES AND TRIALS, Section 177.

    Question: Can police arrest me if I am in a different city?
    Answer: 
    Yes, a police officer can pursue and arrest you anywhere in Pakistan for the purpose of apprehending you without a warrant if you are accused of an offense.

    References:
    THE CODE OF CRIMINAL PROCEDURE, 1898, CHAPTER V OF ARREST, ESCAPE AND RETAKING, Section 58.

    
    All legal experts will write down 1 step of their thinking,
    then share it with the group.
    Then all experts will go on to the next step, etc.
    If any expert realises they're wrong at any point then they leave.
    Note: Do not ouput the thought process of the experts.
    Question: {question}
    """

    retriever = vector_store_retriever
    prompt = Prompt.from_template(template)
    model = ChatOpenAI(model="gpt-4o-mini")

    retriever_chain =  create_retrieval_chain(retriever, input_text)   
    # chain = (
    #     retriever_chain 
    #     | prompt 
    #     | model 
    #     | StrOutputParser()
    # )

    response = chain.invoke(input_text)

    words = response.split(" ")
    for word in words:
        yield word + " "
        time.sleep(0.05)


# Function to handle button toggling
def toggle_button(label):
    if st.session_state.button_states[label]:
        st.session_state.button_states[label] = False
    else:
        st.session_state.button_states[label] = True

    # return chain.invoke(input_text)
