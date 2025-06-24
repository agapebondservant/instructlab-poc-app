import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from io import StringIO
from agentic import AgenticWorkflow
from dotenv import load_dotenv

st.set_page_config(page_title="Simple GenAI App", page_icon="🤖")

load_dotenv()

tab1, tab2 = st.tabs(["Chat", "Agentic"])

try:
    llm = ChatOpenAI(
        temperature=0,
        model="granite-3-8b-instruct",
        request_timeout=240
    )
except Exception as e:
    st.error(f"An error occurred during model initialization: {str(e)}")
    st.info("Please check your API key and try again.")

with tab1:
    st.title("🤖 Simple Chat App")
    st.write("This app demonstrates integrating with InstructLab-tuned LLMs for various generative AI tasks.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask me a question!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = llm.invoke([HumanMessage(content=prompt)])
                    response_content = response.content
                    st.markdown(response_content)
                    st.session_state.messages.append({"role": "assistant", "content": response_content})
                except Exception as e:
                    st.error(f"Error: {str(e)}")
with tab2:
    st.title("🤖 Simple Agentic App")
    st.write("This app demonstrates integrating with InstructLab-tuned LLMs for various agentic AI tasks.")
    
    if "messages2" not in st.session_state:
        st.session_state.messages2 = []
            
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        prompt = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
        st.session_state.messages2.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    workflow = AgenticWorkflow(llm)
                    workflow.run(prompt, st)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    