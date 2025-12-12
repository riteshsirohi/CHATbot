import streamlit as st
from backend import workflow, retreive_all_threads
from langchain_core.messages import HumanMessage
import uuid


#--------------------------------------------------UTILITY SETUP---------------------------------------------------------------
def generate_uuid():
    thread_id =  uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_uuid()
    st.session_state['thread_id'] = thread_id
    #addthread(st.session_state['thread_id'])
    st.session_state['message_history'] = []
    
# def addthread(thread_id):
#     if thread_id not in st.session_state['chat_thread']:
#         st.session_state['chat_thread'].append(st.session_state['thread_id'])
        
def load_conversations(thread_id):
    state = workflow.get_state(config={'configurable':{'thread_id': thread_id}})
    values = state.values
    
    if 'messages' not in values or values['messages'] is None:
        return []
    
    return values['messages']


#--------------------------------------------------SESSION SETUP---------------------------------------------------------------

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_uuid()
    
if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = retreive_all_threads()
    
    #addthread(st.session_state['thread_id'])
    

#--------------------------------------------------SIDEBAR SETUP---------------------------------------------------------------
st.sidebar.title("Langgraph Chatbot")
    
if st.sidebar.button("New Chat"):
        reset_chat()
    
st.sidebar.header("New Conversations")

for thread_id in st.session_state['chat_thread']:
    if st.sidebar.button(str(thread_id)[:8]):
        st.session_state['thread_id'] = thread_id
        messages = load_conversations(thread_id)
    
        temp_message = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_message.append({'role':role, 'content':msg.content})
    
        st.session_state['message_history'] = temp_message
                
    

#--------------------------------------------------MAIN UI---------------------------------------------------------------

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

CONFIG = {'configurable':{'thread_id': st.session_state['thread_id']},
         'metadata':{'thread_id': st.session_state['thread_id']}
         }

user_input = st.chat_input("Type here..")

if user_input:
    
    if st.session_state['thread_id'] not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(st.session_state['thread_id'])
    
    st.session_state['message_history'].append({'role':'user', 'content':user_input})
    with st.chat_message('user'):
        st.text(user_input)
   
    with st.chat_message('assistant'):
        
        ai_message = st.write_stream(
            message_chunk.content for message_chunk , metadata in  
            workflow.stream({'messages':[HumanMessage(content=user_input)]}, config=CONFIG, stream_mode='messages')
        )

    st.session_state['message_history'].append({'role':'assistant', 'content':ai_message})
        
        

        