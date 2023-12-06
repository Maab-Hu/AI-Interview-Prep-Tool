import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from secret_key import openapi_key
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.schema import (AIMessage, HumanMessage, SystemMessage)
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationBufferWindowMemory
import json
from templates import choose_template, extract_template, interview_feedback_template, interview_question_template

st.set_page_config(page_icon='rex.png', layout='wide')

with open('dataset.json', 'r') as file:
    data = json.load(file)

st.title("Warm Up Round : Getting Comfortable with the Interview")

category = st.selectbox("Which type of questions do you want to practice?",
                        ['Technical', 'Behavioural', 'Culture Fit'])

while category is None:
    st.markdown('Please select question category')

if not st.session_state.openai_key:
    st.info("Please add your API key to continue")
    st.stop()

os.environ['OPENAI_API_KEY'] = st.session_state.openai_key

chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.3)

memory = ConversationBufferMemory()

### Extract previously asked Questions from the history

system_template_e = extract_template

system_message_prompt_e = SystemMessagePromptTemplate.from_template(system_template_e)

human_template_e = "{text}"
human_message_prompt_e = HumanMessagePromptTemplate.from_template(human_template_e)

chat_prompt_e = ChatPromptTemplate.from_messages([system_message_prompt_e, human_message_prompt_e])

extract_chain = LLMChain(llm=chat, prompt=chat_prompt_e)

### Choose question based on action

system_template_c = choose_template

system_message_prompt_c = SystemMessagePromptTemplate.from_template(system_template_c)

human_template_c = "{text}"
human_message_prompt_c = HumanMessagePromptTemplate.from_template(human_template_c)

chat_prompt_c = ChatPromptTemplate.from_messages([system_message_prompt_c, human_message_prompt_c])

choose_chain = LLMChain(llm=chat, prompt=chat_prompt_c)

### Asking the questions
system_template_q = interview_question_template

system_message_prompt_q = SystemMessagePromptTemplate.from_template(system_template_q)

human_template_q = "{text}"
human_message_prompt_q = HumanMessagePromptTemplate.from_template(human_template_q)

chat_prompt_q = ChatPromptTemplate.from_messages([system_message_prompt_q, human_message_prompt_q])

question_chain = LLMChain(llm=chat, prompt=chat_prompt_q)

### Provide Feedback

system_template_f = interview_feedback_template

system_message_prompt_f = SystemMessagePromptTemplate.from_template(system_template_f)

human_template_f = "{text}"
human_message_prompt_f = HumanMessagePromptTemplate.from_template(human_template_f)

chat_prompt_f = ChatPromptTemplate.from_messages([system_message_prompt_f, human_message_prompt_f])

feedback_chain = LLMChain(llm=chat, prompt=chat_prompt_f)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "action" not in st.session_state:
    st.session_state.action = "Next"


if "history" not in st.session_state:
    st.session_state.history = []

if "questions" not in st.session_state:
    st.session_state.questions = []

for message in st.session_state.messages:
    if message['role'] == "user":
        name = "user"
        avatar = "user.png"
    else:
        name = "assistant"
        avatar = "rex.png"

    with st.chat_message(name, avatar=avatar):
        st.markdown(f"{message['content']}")

if inp := st.chat_input("Type here"):
    with st.chat_message("user",avatar='user.png'):
        st.markdown(inp)
    st.session_state['messages'].append({'role': 'user', 'content': inp})

question = None

if st.session_state.messages != [] and st.session_state.messages[-1]['role'] == "feedback":
    option = st.radio(label="Which question would you like to do?", options=["Next", "Repeat"], index=None)
    while option is None:
        pass
    st.session_state.action = option

if st.session_state.action == "Next" or "Repeat" and (
        st.session_state.messages == [] or st.session_state.messages[-1]['role'] == "feedback"):

    if st.session_state.questions != []:
        extracts = extract_chain.run(history=st.session_state.questions, text="")
    else:
        extracts = "No previous Questions"
    chosen_q = choose_chain.run(action=st.session_state.action, questions=extracts, data=data, text="",details=st.session_state["Resume Info"])
    response = question_chain.run(question=chosen_q, history=st.session_state.history, text=inp,details=st.session_state["Resume Info"])

    with st.chat_message("assistant", avatar='rex.png'):
        st.markdown(response)

        st.session_state.action = "Feedback"
    st.session_state['messages'].append({'role': 'interviewer', 'content': response})
    memory.save_context({"input": ""}, {"output": response})
    st.session_state['history'].append(memory.buffer_as_messages[-2:])
    st.session_state['questions'].append({'Question': response})
    question = chosen_q
    st.stop()

if st.session_state.messages[-1]['role'] == "user" and st.session_state.action == "Feedback":
    feedback = feedback_chain.run(question=question, response=inp, history=st.session_state.history[-4:], text=inp)

    with st.chat_message("assistant", avatar='rex.png'):
        st.markdown(feedback)
    st.session_state['messages'].append({'role': 'feedback', 'content': feedback})
    memory.save_context({"input": inp}, {"output": feedback})
    st.session_state['history'].append(memory.buffer_as_messages[-2:])

st.button("Continue")



