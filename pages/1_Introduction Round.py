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
import time,random

st.set_page_config(page_icon='rex.png', layout='wide')

st.title("Introduction Round : Getting Familiar")
st.info("""
    Hey there! In the Introduction Round, we aim to get to know you better and create a comfortable environment for a productive 
interview experience. We'll begin by explaining the interview structure, providing you with a clear roadmap of what to
expect. Following this, we'll kick things off with an icebreaker question to break the ice and ease you into the 
conversation. Moving forward, we'll explore your professional background, educational journey, and delve into your 
skills and strengths. You'll have the opportunity to share your career goals and aspirations, allowing us to understand
the unique qualities you bring to the table. If there are any specific achievements or points you'd like to highlight, 
this is the moment to shine. As we approach the conclusion of the round, we'll wrap up with a closing discussion and 
seamlessly transition to the next stage. This round is designed to be informative, engaging, and to help you showcase 
your best self. Let's embark on this journey together!""", icon="🤖")

if not st.session_state.openai_key:
    st.info("Please add your API key to continue")
    st.stop()



if "Resume Info" not in st.session_state or not st.session_state["Resume Info"]:
    st.info("Please upload your Resume")
    st.stop()

os.environ['OPENAI_API_KEY'] = st.session_state.openai_key

chat = ChatOpenAI(temperature=0.3, model_name="gpt-4")

system_template_q = """ You are to take the user through a guided introduction session before an interview, this session is divided into the following rounds/stages:

You are to choose just ONE round based on the conversation from the previous round : {previous}

                            1. Welcome Message
                            2. Explain the Interview Structure
                            3. Professional Background
                            4. Educational Background"
                            5. Skills and Strengths"
                            6. Goals and Aspirations
                            7. Any Specific Points to Highlight
                            8. Closing and Transition
                            
                        
                            
                        Use the previous round info to choose the next question. For example if the previous round asked about skills and strengths.
                        The next question should be about goals and aspirations. Do not give all of the information above at the same time. ONLY ask/give info with respect to the round.


                        Relevant Information related to the interview :

                        The interview process that will contain three type of questions :
                        1.Techinical questions, testing hard skills.
                        2.Behavioral questions to assess the candidates personality and work style, and soft skills.
                        3.Culutural Fit questions to assess the candidates viability to fit in the company culture.

                        Instruct the user that they can do a practice round if they navigate to the Warm Up round section
                        of the , and then they can do actual interviews by navigating to the Interview round section ,
                        where they will be provided live feedback and score for their responses. The user can also repeat
                        the questions if they want to improve the response.

                        Answer to the best of your abilities , but do not make any information up.

                        Use this information about the user to address them and use relevant details : {user_info}

                        Before giving your output , make sure, it is only related to that specific round, do not print out all of the rounds and ask everything at once.
                        
                        Use this logic for your output :
                        
                        The previous round was which round ? And which round should I choose, what question should I ask for that round.
                        
                        Use the past messages : {messages} , to make sure no question is repeated. Where the assistant messages are your previous messages. 
                        Do not ask about one specific topic too much, ask questions and let the user respond , and move on to the next. Embolden any key words in your response by 
                        enclosing the word in **.
                        

                  """


system_message_prompt_q = SystemMessagePromptTemplate.from_template(system_template_q)

human_template_q = "{text}"
human_message_prompt_q = HumanMessagePromptTemplate.from_template(human_template_q)

chat_prompt_q = ChatPromptTemplate.from_messages([system_message_prompt_q,human_message_prompt_q])

intro_chain = LLMChain(llm=chat, prompt=chat_prompt_q)


if "round" not in st.session_state:
    st.session_state["round"] = 1

if "intro_messages" not in st.session_state:
    st.session_state["intro_messages"] = []
    st.session_state['intro_messages'].append({'role': 'assistant', 'content': "Hello! Welcome to the interview. I'm here to help you through the process. In this guided introduction "
                "session, we'll explore different aspects of your background. By the end, you'll have a "
                "chance to practice and improve your interview skills. Let's begin! How are you doing today?"})

for intro_message in st.session_state["intro_messages"]:
    if intro_message['role'] == "assistant":
        avatar = "rex.png"
    else:
        avatar = "user.png"
    with st.chat_message(intro_message['role'],avatar=avatar):
        st.markdown(intro_message['content'])


if query := st.chat_input("Type here to talk to AI assistant"):
    with st.chat_message("user",avatar="user.png"):
        st.markdown(query)

    st.session_state['intro_messages'].append({'role': 'user', 'content': query})

if query is not None:
    reply = intro_chain.run(text=query, user_info=st.session_state["Resume Info"], previous=st.session_state["intro_messages"][-2],
                            messages=st.session_state["intro_messages"])
    with st.chat_message("assistant",avatar="rex.png"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in reply.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        #st.markdown(reply)

    st.session_state['intro_messages'].append({'role': 'assistant', 'content': reply})


if "round" in st.session_state and st.session_state["round"] < 9:
    st.session_state["round"] = st.session_state["round"] + 1



