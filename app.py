import streamlit as st
import requests
from pymongo import MongoClient
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain.schema import AIMessage

# ----------------- LLM -----------------
llm = ChatGoogleGenerativeAI(
    api_key="AIzaSyDbTBJAWFB3xxSLIZ6o09ll7nZ47pvtDD8",
    model="gemini-2.5-flash",
    temperature=0
)

# ----------------- Tool -----------------
def get_weather(city: str) -> str:
    """Fetch real weather data for a given city."""
    try:
        response = requests.get(f"https://p2pclouds.up.railway.app/v1/learn/weather?city={city}")
        response.raise_for_status()
        data = response.json()
        return data.get("weather", str(data)) if isinstance(data, dict) else str(data)
    except Exception as e:
        return f"Error: {e}"

# ----------------- Memory -----------------
MONGODB_URI = "mongodb+srv://agent123:7Lv1SXXddCJGGmgg@cluster0.4wpe5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo_client = MongoClient(MONGODB_URI)
checkpointer = MongoDBSaver(mongo_client)

# ----------------- Agent -----------------
agent = create_react_agent(
    model=llm,
    tools=[get_weather],
    prompt="You are a helpful assistant",
    checkpointer=checkpointer
)

# ----------------- Streamlit UI -----------------
st.title("Memory Agent with Weather Tool")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "user12345"
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

# User input
user_input = st.chat_input("Ask me anything:")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Call agent
    response = agent.invoke(
        {"messages": st.session_state.messages},
        config={"configurable": {"thread_id": st.session_state.thread_id}}
    )

    # Extract only content (universal)
    if hasattr(response, "content"):
        assistant_reply = response.content
    elif isinstance(response, dict):
        if "content" in response:
            assistant_reply = response["content"]
        elif "messages" in response and len(response["messages"]) > 0:
            last_msg = response["messages"][-1]
            assistant_reply = last_msg.get("content", str(last_msg)) if isinstance(last_msg, dict) else str(last_msg)
        else:
            assistant_reply = str(response)
    else:
        assistant_reply = str(response)

    # Display
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    st.chat_message("assistant").write(assistant_reply)



# if user_input:
#     st.session_state.messages.append({"role": "user", "content": user_input})
#     st.chat_message("user").write(user_input)

#     # Call the agent
#     response = agent.invoke(
#         {"messages": st.session_state.messages},
#         config={"configurable": {"thread_id": st.session_state.thread_id}}
#     )

    #  Universal extraction of assistant reply
    # if hasattr(response, "content"):  # AIMessage
    #     assistant_reply = response.content
    # elif isinstance(response, dict) and "messages" in response:
    #     last_msg = response["messages"][-1]
    #     assistant_reply = last_msg["content"] if isinstance(last_msg, dict) else str(last_msg)
    # else:
    #     assistant_reply = str(response)




    # # Display assistant reply
    # st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    # st.chat_message("assistant").write(assistant_reply)


# Extract only the main assistant reply

