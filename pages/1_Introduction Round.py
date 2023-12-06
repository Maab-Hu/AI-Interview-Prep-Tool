import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from secret_key import openapi_key
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.schema import (AIMessage,HumanMessage,SystemMessage)
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationBufferWindowMemory

st.set_page_config(page_icon='rex.png', layout='wide')

st.title("Introduction Round : Getting Familiar")

if not st.session_state.openai_key:
    st.info("Please add your API key to continue")
    st.stop()

if not st.session_state["Resume Info"]:
    st.info("Please upload your Resume")
    st.stop()

os.environ['OPENAI_API_KEY'] = st.session_state.openai_key

chat = ChatOpenAI(temperature=0.3)

system_template_q = """Your task is to get a user familiar with an interview process that will contain three type of questions :
                        1.Techinical questions, testing hard skills.
                        2.Behavioral questions to assess the candidates personality and work style, and soft skills.
                        3.Culutural Fit questions to assess the candidates viability to fit in the company culture.
                        
                        Instruct the user that they can do a practice round if they navigate to the Warm Up round section
                        of the , and then they can do actual interviews by navigating to the Interview round section , 
                        where they will be provided live feedback and score for their responses. The user can also repeat 
                        the questions if they want to improve the response.
                        
                        Answer to the best of your abilities , but do not make any information up. 
                        
                        Use this information about the user to address them and use relevant details : {user_info}
                        
                        Be succinct and precise with your responses, a wordy answer might just confuse the user.
                        
                  """


system_message_prompt_q = SystemMessagePromptTemplate.from_template(system_template_q)

human_template_q = "{text}"
human_message_prompt_q = HumanMessagePromptTemplate.from_template(human_template_q)

chat_prompt_q = ChatPromptTemplate.from_messages([system_message_prompt_q,human_message_prompt_q])

intro_chain = LLMChain(llm=chat, prompt=chat_prompt_q)

with st.chat_message("assistant", avatar='rex.png'):
    st.markdown("Hey, I am here to assist you with any questions you have about the interview , how may I help you?")

if "intro_messages" not in st.session_state:
    st.session_state["intro_messages"] = []

for intro_message in st.session_state["intro_messages"]:
    with st.chat_message(intro_message['role']):
        st.markdown(intro_message['content'])


if query := st.chat_input("Type here to talk to AI assistant"):
    with st.chat_message("user"):
        st.markdown(query)

    st.session_state['intro_messages'].append({'role': 'user', 'content': query})

if query is not None:
    reply = intro_chain.run(text=query, user_info=st.session_state["Resume Info"])
    with st.chat_message("assistant"):
        st.markdown(reply)
    st.session_state['intro_messages'].append({'role': 'assistant', 'content': reply})


