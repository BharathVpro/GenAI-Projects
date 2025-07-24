import streamlit as st
import sys
import time
from io import StringIO
import pandas as pd
from AutoClean import AutoClean
import plotly.express as px
import streamlit as st
import pandas as pd
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cohere import ChatCohere
import os
import subprocess
import sys
import matplotlib as plt
import plotly 
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from AutoClean import AutoClean
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
from langchain_cohere import ChatCohere

# Setting up API
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')
os.environ["COHERE_API_KEY"] = os.getenv('COHERE_API_KEY')

#LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature= 0.7)
# llm = ChatCohere(temperature=0.7,model="command-r7b-12-2024")
python_repl = PythonREPL()
repl_tool = Tool(
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
    func=python_repl.run,
)
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

memory = MemorySaver()

search = TavilySearchResults()
tools = [search, repl_tool]
config = {"configurable": {"thread_id": "abc123"}}
   
def extract_code_without_fig_show(code):
        start_index = code.find("import")
        end_index = code.find("st.plotly_chart(fig)")
        
        if start_index == -1 or end_index == -1:
            return "Error: Could not find required sections in the input string."
        
        return code[start_index:end_index].strip()

# Function to clean data and yield logs
def run_autoclean_with_logs(uploaded_file):
    try:
        # Capture logs from AutoClean
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        log_stream = StringIO()
        sys.stdout = log_stream
        sys.stderr = log_stream

        # Load and clean data
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
        cleaned_df = AutoClean(df, mode='auto', verbose=True, logfile=False, extract_datetime=False).output

        # Restore stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr

        # Stream logs in real-time and store in session state
        log_stream.seek(0)
        for log_line in log_stream:
            st.session_state.logs.append(log_line)  # Store log in session state
            st.session_state.real_time_log = "".join(st.session_state.logs)  # Update full log in session state
            yield log_line  # Stream current log line in real time
            time.sleep(0.1)

        st.session_state.cleaned_data = cleaned_df
        st.session_state.logs.append("Data cleaning completed successfully.\n")
        st.session_state.real_time_log = "".join(st.session_state.logs)

    except Exception as e:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        error_message = f"An error occurred during data cleaning: {str(e)}\n"
        st.session_state.logs.append(error_message)
        st.session_state.real_time_log = "".join(st.session_state.logs)
        yield error_message

# Streamlit app UI
st.markdown("<h1 style='text-align: center;'>Dynamic Data Visualizer</h1>", unsafe_allow_html=True)

# Initialize session state keys
if "clean_data_logs" not in st.session_state:
    st.session_state["clean_data_logs"] = None

if "cleaned_df" not in st.session_state:
    st.session_state["cleaned_df"] = None

if "selected_column" not in st.session_state:
    st.session_state["selected_column"] = None

# Initialize session state
if "cleaned_data" not in st.session_state:
    st.session_state.cleaned_data = None
if "logs" not in st.session_state:
    st.session_state.logs = []  # Persistent logs as a list
if "real_time_log" not in st.session_state:
    st.session_state.real_time_log = ""  # Real-time log display
if "user_input" not in st.session_state:
    st.session_state.user_input = ""  # Persistent input text

# # Streamlit app UI
# st.title("Data Cleaner with AutoClean")

# st.subheader("File Upload for Data Cleaning")
uploaded_file = st.file_uploader("Upload your CSV file for cleaning", type=["csv"])

# Show the "Clean Data" button only after a file is uploaded
if uploaded_file:
    st.success("File uploaded successfully!")
    if st.button("Clean the Data"):
        st.session_state.cleaned_data = None  # Clear previous cleaned data
        st.session_state.logs = []  # Clear previous logs
        st.session_state.real_time_log = ""  # Clear real-time log
        with st.spinner("Reading data to start cleaning data..."):
            log_display = st.empty()  # Placeholder for real-time log display
            for log in run_autoclean_with_logs(uploaded_file):
                log_display.text(st.session_state.real_time_log)  # Update real-time log display

        st.success("Data cleaning completed successfully!")

# Display logs persistently after cleaning
if st.session_state.real_time_log:
    # st.subheader("Logs")
    st.text(st.session_state.real_time_log)  # Display stored real-time logs

# Display cleaned data after cleaning
if st.session_state.cleaned_data is not None:
    st.subheader("Cleaned Data")
    st.dataframe(st.session_state.cleaned_data.head(10))

    # Show input text box and persist entered text in session state
    # st.subheader("Additional Input After Cleaning")
    user_input = st.text_input("Ask me any query about clean data:")

    if st.button("Submit"):
        st.session_state.user_input = user_input
        if user_input:
            # Dropdown to select a column
            df = st.session_state.cleaned_data
            agent_executor = create_pandas_dataframe_agent(llm, df, allow_dangerous_code=True, Tool = repl_tool, checkpointer=memory, handle_parsing_errors=True)
            for chunk in agent_executor.stream(
            
                {"input": [SystemMessage(
                content=f"""You are a smart Data Visualization expert. I need your help in visualizing the data. Help the user to visualize plot using plotly. Do not execute the code. Just give the final code.
                Always Read the df first and answer the user query accordingly. Don't write code just give answer user. Only write code if user ask to plot graph.
                Always end code with st.plotly_chart(fig) without commenting it.
                
                
                SAMPLE CODE:

              # Sample bubble chart with animation:
                fig = px.scatter(gapminder, x='gdpPercap', y='lifeExp', color='continent', size='pop', size_max=40, 
                hover_name='country',log_x=True, animation_frame='year',
                 animation_group='country', range_x=[25, 10000], range_y=[25,90], 
                labels=dict(pop="Population", gdpPercap="GDP Per Capita", lifeExp="Life Expectency"))
                
                st.plotly_chart(fig)

                

                # Sample map using  choropleth
                fig = px.choropleth(gapminder, locations='iso_alpha', color='lifeExp', hover_name='country', 
                                    animation_frame='year', color_continuous_scale=px.colors.sequential.Plasma, projection='natural earth')
                st.plotly_chart(fig) 

            
                # Sample Cluster plot:
                import plotly.graph_objects as go

                # Generate dataset
                import numpy as np
                np.random.seed(1)

                x0 = np.random.normal(2, 0.4, 400)
                y0 = np.random.normal(2, 0.4, 400)
                x1 = np.random.normal(3, 0.6, 600)
                y1 = np.random.normal(6, 0.4, 400)
                x2 = np.random.normal(4, 0.2, 200)
                y2 = np.random.normal(4, 0.4, 200)

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

                st.plotly_chart(fig)

                If user ask for bubble chart, write code for bubble chart with animation.
                If user ask for Distribution plot, write code for either Histogram , Kernel Density Plot (KDE), Box Plot (or Box-and-Whisker Plot). You decide which makes more suitable based on data.
                ONLY WRITE CODE IF USER USE WORDS Like 'plot', 'graph', 'diagram' or 'figure'. other wise just give text answer to user.
                Always create an plot like just like mentioned sample plot code when user ask to plot graph. DO NOT WRITE THE SAMPLE CODE, TAKE IT AS AN REFERNCE.
                DO NOT WRITE CODE WITH RANDOM or SAMPLE DATA. USE THE DATA WHAT USER HAS PROVIDED.

                """
                ),
                HumanMessage(content=f"Read the df and {st.session_state.user_input}")]}, config):
                if "output" in chunk and chunk["output"]:
                    response = chunk["output"]

                    if "import" in response:
                        response = extract_code_without_fig_show(response)
                        response+='\n'+'st.plotly_chart(fig)'
                        response = response.replace("# st.pydeck_chart(deck)", "st.pydeck_chart(deck)")
                        st.write(response)
                        # Display the code in a text area for editing
                        st.subheader("Generated Code")
                        code = st.text_area("Edit the code below:", value=response, height=300)
                        button_clicked = st.button("Run Code", key="hidden_button")
                        # Execute the code in the text area when the user clicks "Run"
                        if button_clicked:
                            try:
                                exec(code)
                            except Exception as e:
                                st.error(f"Error in the code: {e}")
                        try:
                            exec(response)
                        except (ValueError, TypeError):
                            st.write("Sorry, I'm unable solve the query. Please try again.")
                    else:
                        try:
                            st.write(response)
                        except ValueError:
                            st.write("Sorry, I'm unable solve the query. Please try again.")
                else:
                    st.write('')
        else:
            st.write("Please enter some query before submitting.")

