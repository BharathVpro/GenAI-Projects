
from fastapi import FastAPI
from fastapi import Form
from fastapi import UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI  
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm
import sys
import time
from io import StringIO
import pandas as pd
import plotly.express as px
import streamlit as st
import pymongo
import os
from typing import Literal
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cohere import ChatCohere
import os
import subprocess
import sys
import matplotlib as plt
import plotly 
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
# from AutoClean import AutoClean
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_experimental.agents import create_csv_agent
from langchain_core.tools import Tool
from langchain_experimental.utilities import PythonREPL
from langchain_core.messages import HumanMessage, SystemMessage
# from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.mongodb import MongoDBSaver

MONGODB_URI = "mongodb+srv://b61013740:nPEnQS5XBZ5xSofh@cluster0.eklcy.mongodb.net/"  

app = FastAPI()

# Allow all origins (adjust for production as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    thread_id: int  # Add this field to accept thread id from frontend


class ChatResponse(BaseModel):
    response: str

# Instantiate the LLM once to avoid reinitialization on every request
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
python_repl = PythonREPL()
repl_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
    func=python_repl.run,
)
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
search = TavilySearchResults()
tools = [repl_tool]
config = {"configurable": {"thread_id": "abc123"}}
# df = pd.read_csv('data.csv', sep=None, engine='python')

import pandas as pd

class DataDF:
    def __init__(self):
        """Initialize with an empty DataFrame."""
        self.df = pd.DataFrame()

    def load_data(self, file_path='data.csv', **kwargs):
        try:
            self.df = pd.read_csv(file_path, **kwargs)
            print(f"Data loaded successfully from '{file_path}'.")
        except Exception as e:
            print(f"Error loading data: {e}")

df_manager = DataDF()

df = df_manager.load_data('data.csv', sep=None, engine='python')

checkpointer = InMemorySaver()

import re

def extract_import_html(text: str) -> str:
    """
    Extracts a substring that starts with 'import' and ends with '.html")' or ".html')".
    If such a substring is not found, returns the original text.
    
    Parameters:
        text (str): The input string.
        
    Returns:
        str: The extracted substring if found, otherwise the original string.
    """
    pattern = r'(import.*?\.html(?:\"\)|\'\)))'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    return text


def data_analysis_tool(query: str):

    """'I don't need any data, i already have data, I'm an data visualization agent with existing data provided by user, which can perform analysis based on query on data and 
       can give detailed information about data and
       Also can write python code on this data to plot graphs"""

    agent_executor = create_pandas_dataframe_agent(
        model, 
        df, 
        allow_dangerous_code=True, 
        Tool = repl_tool, 
        checkpointer = checkpointer, 
        handle_parsing_errors=True)
    for chunk in agent_executor.stream(

    {"input": [SystemMessage(
    content=f"""
    You are a smart Data Visualization expert. User need your help in visualizing the data. Help the user to visualize plot using plotly. Always execute the code and also give user a code as a response.
    Always Read the df first and answer the user query accordingly. Don't write code just give answer user. Only write code and execute if user ask to plot graph.
    [*** ALWAYS end code with fig.write_html("../client/public/[title of graph].html") ***]
    I WANT MY GRAPH TO BE SAVED IN ../client/public/[title of graph].html ALWAYS.
    ALWAYS PLOT THE GRAPH COLORFULLY Because User can differentiate the graph easily.
    
    SAMPLE CODE:
    Always start with this code
    [import pandas as pd
    df = pd.read_csv('data.csv', sep=None, engine='python')]

    # Sample map using  choropleth
    fig = px.choropleth(gapminder, locations='iso_alpha', color='lifeExp', hover_name='country', 
                        animation_frame='year', color_continuous_scale=px.colors.sequential.Plasma, projection='natural earth')
    fig.write_html("../client/public/[title of graph].html")


    # Sample Cluster plot:
    import plotly.graph_objects as go
    import numpy as np

    # Create figure
    fig = go.Figure()

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=x0,
            y=y0,
            mode="markers",
            marker=dict(color="DarkOrange")
        )
    )

    fig.add_trace(
        go.Scatter(
            x=x1,
            y=y1,
            mode="markers",
            marker=dict(color="Crimson")
        )
    )

    fig.add_trace(
        go.Scatter(
            x=x2,
            y=y2,
            mode="markers",
            marker=dict(color="RebeccaPurple")
        )
    )

    # Add buttons that add shapes
    cluster0 = [dict(type="circle",
                                xref="x", yref="y",
                                x0=min(x0), y0=min(y0),
                                x1=max(x0), y1=max(y0),
                                line=dict(color="DarkOrange"))]
    cluster1 = [dict(type="circle",
                                xref="x", yref="y",
                                x0=min(x1), y0=min(y1),
                                x1=max(x1), y1=max(y1),
                                line=dict(color="Crimson"))]
    cluster2 = [dict(type="circle",
                                xref="x", yref="y",
                                x0=min(x2), y0=min(y2),
                                x1=max(x2), y1=max(y2),
                                line=dict(color="RebeccaPurple"))]

    fig.update_layout(
        updatemenus=[
            dict(buttons=list([
                dict(label="None",
                    method="relayout",
                    args=["shapes", []]),
                dict(label="Cluster 0",
                    method="relayout",
                    args=["shapes", cluster0]),
                dict(label="Cluster 1",
                    method="relayout",
                    args=["shapes", cluster1]),
                dict(label="Cluster 2",
                    method="relayout",
                    args=["shapes", cluster2]),
                dict(label="All",
                    method="relayout",
                    args=["shapes", cluster0 + cluster1 + cluster2])
            ]),
            )
        ]
    )

    # Update remaining layout properties
    fig.update_layout(
        title_text="Highlight Clusters",
        showlegend=False,
    )

    fig.write_html("../client/public/Highlight_Clusters.html")

    *** YOUR FINAL RESPONSE SHOULD LIKE ALWAYS LIKE THIS " I have created a bar graph at  '../agentbuilder/public/CountofLoan_Status.html' ". NOTHING MORE NOTHING LESS] ***

    If user ask for bubble chart, write code for bubble chart with animation.
    If user ask for Distribution plot, write code for either Histogram , Kernel Density Plot (KDE), Box Plot (or Box-and-Whisker Plot). You decide which makes more suitable based on data.
    ONLY WRITE CODE IF USER USE WORDS Like 'plot', 'graph', 'diagram' or 'figure'. other wise just give text answer to user.
    DO NOT WRITE THE SAMPLE CODE, TAKE IT AS AN REFERNCE.
    DO NOT WRITE CODE WITH RANDOM or SAMPLE DATA. USE THE DATA WHAT USER HAS PROVIDED.
    

    """
    ),
    HumanMessage(content=f"Read the df and {query}")]}, config):
        if "output" in chunk and chunk["output"]:
            response = chunk["output"]
            response

            return response

alice = create_react_agent(
    model,
    [data_analysis_tool, create_handoff_tool(agent_name="Bob")],
    prompt="You are Alice, an Data Expert. You have data_analysis_tool tool which is response for data analysis with existing data where user expect some details from it (data(df)). NEVER ASK USER TO PROVIDE DATA Because pandas tool already have DATA",
    name="Alice",
)

bob = create_react_agent(
    model,
    [search, create_handoff_tool(agent_name="Alice", description="Transfer to Alice, she can help with query related to Data")],
    prompt="You are Bob, a smart assistant from telugu speaking state, but only speaks telugu when user stated asking in telugu otherwise stick with English",
    name="Bob",
)


# Create a checkpointer and compile the swarm once for state persistence
workflow = create_swarm(
    [alice, bob],
    default_active_agent="Bob"  # Change to "Alice" if desired
)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    query: str = Form(...),
    thread_id: int = Form(...),
    file: UploadFile = File(None)
):
    file_response = ""
    # If a file is provided, process it first.
    if file is not None:
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        file_location = os.path.join(temp_dir, file.filename)
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        # Load the uploaded file into your DataFrame; adjust separator if needed.
        df_manager.load_data(file_location, sep=';')
        file_response = f"File '{file.filename}' saved at '{file_location}' and loaded successfully."

        # Proceed with chat functionality.
        with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
            compiled_swarm = workflow.compile(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": str(thread_id)}}
            messages = [{"role": "user", "content": query}]
            
            result = compiled_swarm.invoke({"messages": messages}, config)
            result = result['messages'][-1]
            ai_response = result.content if hasattr(result, "content") else str(result)
            ai_response = str(ai_response)
            print(ai_response)
            
            # Retrieve conversation history (if needed)
            checkpoint_tuple = checkpointer.get_tuple(config)
            history = {"messages": []}
            raw_messages = checkpoint_tuple.checkpoint.get("channel_values", {}).get("messages", [])
            for msg in raw_messages:
                if hasattr(msg, "content"):
                    msg_repr = str(msg)
                    if "HumanMessage" in msg_repr:
                        history["messages"].append({"role": "user", "content": msg.content})
                    elif "AIMessage" in msg_repr and msg.content.strip() != "":
                        history["messages"].append({"role": "assistant", "content": msg.content})
        
        # Return a combined response if file was uploaded.
        if file_response:
            combined_response = f"{file_response}\nChat Response: {ai_response}"
            return ChatResponse(response=combined_response)
        else:
            return ChatResponse(response=ai_response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)