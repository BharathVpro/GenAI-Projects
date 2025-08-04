from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import os
import time
import re
from gpt_researcher import GPTResearcher
import asyncio
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import google.generativeai as genai
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.utilities import PythonREPL
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_cohere import CohereEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
import json
# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"]) 

# Set up Tavily API key
os.environ["TAVILY_API_KEY"] = ""
from langchain_groq import ChatGroq
from langchain_cohere import ChatCohere

import os
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')
os.environ["COHERE_API_KEY"] = os.getenv('COHERE_API_KEY')
os.environ["TAVILY_API_KEY"] = os.getenv('TAVILY_API_KEY')
llm1 = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are a useful Smart Assistant respond to user. 
                      Use right tool only when it is necessary, otherwise continue regular conversation.
                      If user response or question is not clear or non relative, ask user to make it clear or ask him what he is talking about?
                      If User ask for code, just him code and ask hime to execute or not. If he say yes then only use python_tool to excute the code.
                      If User ask for anything by mentioning 'doc', use the tool doc_reader.
                      """),
        ("placeholder", "{messages}"),
    ]
)

UPLOAD_FOLDER = './'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def extract_summary(bot_response):
    # Try to extract the JSON part and the summary part
    try:
        # Split the response to isolate the JSON part and the summary part
        json_part, summary_part = re.split(r']\s*', bot_response, maxsplit=1)
        # Load the JSON part to ensure it's valid JSON
        json.loads(json_part + ']')
        # Clean up the summary part to return just the string
        return summary_part.strip().replace('"', '')
    except (ValueError, json.JSONDecodeError):
        return "Invalid response format."

@tool
def python_tool(code: str) -> str:
    """Execute Python code and return the result."""
    return PythonREPL().run(code)
@tool
def web_search(name: str) -> str:
    """Tool to perform a web search."""
    search = TavilySearchResults(max_results=2)
    return search.invoke(name)


@tool
def doc_reader(name: str, file: str) -> str:
    """Tool to query the doc which is in retriver (Rag)"""
    # Provide the path to your PDF file
    loader = PyPDFLoader(file)
    docs = loader.load()
    embeddings = CohereEmbeddings( model='embed-english-v3.0')
    # # Splitting data
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)

    # Storing embedding data into vectorstore
    vectorstore = Chroma.from_documents(splits, embedding=embeddings,collection_name="query_doc", persist_directory= f'./{name}_db')

    # Setting up retriever
    retriever = vectorstore.as_retriever()
    return retriever.invoke(name)


@tool
def gpt_researcher(query: str) -> str:   
    async def fetch_report(query):
        """
        Fetch a research report based on the provided query and report type.
        """
        researcher = GPTResearcher(query=query)
        await researcher.conduct_research()
        report = await researcher.write_report()
        return report

    async def generate_research_report(query):
        """
        This is a sample script that executes an async main function to run a research report.
        """
        report = await fetch_report(query)
        print(report)

    if __name__ == "__main__":
        QUERY = "What happened in the latest burning man floods?"
        asyncio.run(generate_research_report(query=QUERY))

@tool
def process_video_and_describe(video_name: str, prompt: str) -> str:
    """Process a video and generate a description of the video."""
    myfile = genai.upload_file(video_name)

    # Wait for the video to finish processing
    while myfile.state.name == "PROCESSING":
        time.sleep(5)
        myfile = genai.get_file(myfile.name)

    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    result = model.generate_content([myfile, prompt])
    return result.text

# Initialize memory and LangChain model
memory = MemorySaver()
model = llm2  # Use your preferred model settings
agent = create_react_agent(
    model,
    tools=[web_search, python_tool, process_video_and_describe, doc_reader, gpt_researcher],
    checkpointer=memory,
    state_modifier=prompt,
)

thread_id = uuid.uuid4()
config = {"configurable": {"thread_id": thread_id}}
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    # LangChain interaction
    input_message = HumanMessage(content=user_message)
    bot_response = ""

    # Stream LangChain response
    for event in agent.stream({"messages": [input_message]}, config, stream_mode="values"):
        bot_response += event["messages"][-1].content

    # Clean up the response to remove echoed input and tags
    cleaned_response = re.sub(r"<.*?>", "", bot_response)
    cleaned_response = cleaned_response.replace(user_message, "").strip()
    cleaned_response = str(cleaned_response)
    return jsonify({'response': cleaned_response})


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    try:
        # Save the file with its original filename
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'filePath': file_path}), 200
    except Exception as e:
        return jsonify({'message': f'Failed to upload file: {str(e)}'}), 500



if __name__ == '__main__':
    app.run(debug=True)
