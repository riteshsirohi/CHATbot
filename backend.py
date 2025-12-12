from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
nvapi_key = os.getenv("NVIDIA_API_KEY")

model = ChatNVIDIA(
    model="meta/llama-3.1-8b-instruct",
    api_key=nvapi_key
)

class ChatState(TypedDict):
    
    messages : Annotated[list[BaseMessage], add_messages]
    
def bot(state:ChatState)-> ChatState:
    
    message = state['messages']
    
    response = model.invoke(message)
    
    return {'messages': state['messages'] + [response]}

graph = StateGraph(ChatState)
graph.add_node("bot",bot)
graph.add_edge(START, 'bot')
graph.add_edge('bot', END)

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)

workflow = graph.compile(checkpointer=checkpointer)

def retreive_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    

    return list(all_threads)
    