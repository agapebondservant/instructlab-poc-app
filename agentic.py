from typing import TypedDict, Literal
import json
import random
from langgraph.graph import END, StateGraph
from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod
from langchain_core.messages import HumanMessage
import os
from typing import Annotated, Literal, TypedDict
from langgraph.graph.message import add_messages
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
import functools
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.text_splitter import RecursiveCharacterTextSplitter
import time
import codecs
import templateprompts
from dotenv import load_dotenv

load_dotenv()


class NMAgentState(TypedDict):
    """
    Encapsulates state in our agentic workflow
    """
    messages: Annotated[list, add_messages]

class AgenticWorkflow():
    def __init__(self, llm):
        self.llm = llm
        self.workflow = StateGraph(NMAgentState)
        
        # tools
        google_search_tool = TavilySearchResults(max_results=5, include_answer=True, include_raw_content=True, include_images=True,)
        
        # agents
        searcher_agent = self.create_agent(llm, [google_search_tool], templateprompts.searcher_template)
        analyst_agent = self.create_agent(llm, [], templateprompts.analyst_template)
        
        # nodes
        searcher_node = functools.partial(self.agent_node, agent=searcher_agent, name="Search Agent")
        analyst_node = functools.partial(self.agent_node, agent=analyst_agent, name="Analyst Agent")
        tool_node = ToolNode([google_search_tool])
    
        # add nodes
        self.workflow.add_node("searcher", searcher_node)
        self.workflow.add_node("analyst", analyst_node)
        self.workflow.add_node("tools", tool_node)
        
        # add entrypoint
        self.workflow.set_entry_point("analyst")
        
        # add edges
        self.workflow.add_conditional_edges("searcher", self.should_search)
        self.workflow.add_conditional_edges("analyst", self.should_submit)
        self.workflow.add_edge("tools", "searcher")
        
        # compile the workflow into a graph
        checkpointer = MemorySaver()
        self.graph = self.workflow.compile(checkpointer=checkpointer)
        
        
    def run(self, prompt, st):
        config = {"configurable": {"thread_id": 12, "recursion_limit": 10}}
        try:
            for event in self.graph.stream({"messages": [HumanMessage(content=prompt)]}, config, stream_mode="values"):
                response_content = event['messages'][-1]
                st.markdown(response_content)
                st.session_state.messages2.append({"role": "assistant", "content": response_content})
        except Exception as e:
            print(f"\n\nErrors generating response:\n===============\n {str(e)}")
        
    def create_agent(self, llm, tools, system_message: str):
      """
      Creates an agent with the given LLM, tools, and system message
      """
      prompt = ChatPromptTemplate.from_messages(
          [
              (
                  "system",
                  "{system_message}",
              ),
              MessagesPlaceholder(variable_name="messages"),
          ]
      )
      prompt = prompt.partial(system_message=system_message)
      if tools:
        return prompt | llm.bind_tools(tools)
      else:
        return prompt | llm
    
    #####################################
    ## NODES ##
    #####################################
    def agent_node(self, state, agent, name):
        result = agent.invoke(state)
        return { "messages": [result] }
    
    #####################################
    ## EDGES ##
    #####################################
    def should_search(self, state) -> Literal['tools', 'analyst']:
        if len(state['messages']) and state['messages'][-1].tool_calls:
          return "tools"
        else:
          return "analyst"
        
    def should_submit(self, state) -> Literal['searcher', END]:
        if len(state['messages']) and 'DONE' in state['messages'][-1].content:
          return END
        else:
          return "searcher"

