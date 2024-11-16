#  QUIZ Bot from Docs & YT urls

# Import required modules
import regex as re
import sys
import os 
import time
import getpass
import subprocess
from fpdf import FPDF
import streamlit as st
from langchain import hub
from langchain.chains import RetrievalQA
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_core.documents.base import Document
from langchain_fireworks import FireworksEmbeddings
from langchain_cohere import ChatCohere
from langchain_google_genai import ChatGoogleGenerativeAI

#Load API KEYS
os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')
os.environ["FIREWORKS_API_KEY"] = os.getenv('FIREWORKS_API_KEY')
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')
os.environ["COHERE_API_KEY"] = os.getenv('COHERE_API_KEY')


# UI Title
st.title("Personalized Assessment Bot")

# Initiate LLM Model
# llm = ChatGroq(model="llama3-8b-8192")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

folder_name = "subtitles"  # Folder name to store subtitles

# Create the folder if it doesn't exist
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

subtitle_path = os.path.join(folder_name, "%(title)s.%(ext)s")

# Creating Doc Upload Options (UI)
option = st.radio("Choose an option", ('Upload a Document', 'Paste a URL'))

if option == "Upload a Document":   # Option 1(Doc Upload)
    uploaded_file = st.file_uploader("Choose a file", type= ["pdf", "txt", "docx", "png", "jpg", "jpeg"])
    path = ''
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # st.write("Uploaded file:", uploaded_file.name)
        path = uploaded_file.name
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    # st.success("File uploaded successfully!")

    docs = [Document(metadata={'source': 'pdf'}, page_content='No Doc')]
    # Loading the PDF File
    if path:
        loader = PyPDFLoader(path)
        docs = loader.load()

elif option == 'Paste a URL':      # Option 2 (URL Paste)
    url = st.text_input("Paste a URL")

    if url:
        st.write(f"URL entered: {url}")

        video_url = url

        # Download subtitles only (no video)
        subprocess.run([
            "yt-dlp",
            "--write-auto-sub",   # Download automatic subtitles
            "--sub-lang", "en",   # Subtitle language (e.g., 'en' for English)
            "--skip-download",    # Skip downloading the video itself
             "-o", subtitle_path,  # Output format and folder path
            video_url
        ])

        # Find the downloaded .vtt or .srt file
        # Find the downloaded .vtt or .srt file in the 'subtitles' folder
        subtitle_file = None
        for file in os.listdir(folder_name):
            if file.endswith(".vtt") or file.endswith(".srt"):
                subtitle_file = os.path.join(folder_name, file)
                break


        # If the subtitle file was found, extract only the text and ignore timestamps
        if subtitle_file:
            with open(subtitle_file, "r", encoding="utf-8") as f:
                subtitles = f.read()
                
                # Remove timestamps and other metadata using regex
                cleaned_subtitles = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", "", subtitles)  # For .vtt
                cleaned_subtitles = re.sub(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", "", cleaned_subtitles)  # For .srt
                cleaned_subtitles = re.sub(r"\d+\n", "", cleaned_subtitles)  # Remove subtitle indices (e.g., "1", "2", "3")
                cleaned_subtitles = re.sub(r"<[^>]+>", "", cleaned_subtitles)  # Remove HTML tags (sometimes appear in subtitles)
                
                # Remove empty lines
                cleaned_subtitles = "\n".join([line.strip() for line in cleaned_subtitles.splitlines() if line.strip()])

                # Split subtitles into a list of lines and remove duplicates
                subtitle_lines = cleaned_subtitles.split("\n")
                unique_subtitles = []
                for line in subtitle_lines:
                    if line not in unique_subtitles:
                        unique_subtitles.append(line)
                
                # Join the unique subtitles and print them
                docs = [Document(metadata={'title': 'url'}, page_content= "\n".join(unique_subtitles))]
        else:
            docs = [Document(metadata={'title': 'url'}, page_content= "No Url")]
    else:
        docs = [Document(metadata={'title': 'url'}, page_content="No Url")]


embeddings = FireworksEmbeddings(
    model="nomic-ai/nomic-embed-text-v1.5",
)

# Splitting data
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
splits = text_splitter.split_documents(docs)

# Storing embedding data into vectorstore
vectorstore = InMemoryVectorStore.from_documents(
    splits,
    embedding=embeddings,)

# Setting up retriver
retriever = vectorstore.as_retriever()

# building prompt for rag_chain
template = """ You are a knowledgeable chatbot, ask questions from doc.
    
    Context: {context}
    History: {history}

    User: {question}
    Chatbot:
    """

prompt = PromptTemplate(
        input_variables=["history", "context", "question"],
        template=template,
    )

memory = ConversationBufferMemory(
        memory_key="history",
        return_messages=True,
        input_key="question"
    )

# Create a chain which retrieves documents and generates a response.
rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type='stuff',
            retriever=retriever,
            verbose=False,
            chain_type_kwargs={
                "verbose": False,
                "prompt": prompt,
                "memory": memory,
            }
        )




# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'quiz_active' not in st.session_state:
    st.session_state.quiz_active = True
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []

# Defining Func to generate question
def get_question():
    query = """
        "you are the quiz bot. you need to ask the random questions from the doc"
        "If doc contain passage and followed by question, ask question along with passage"
        "You will read the provided information and generate a multiple-choice question based on the key content. "
        NOTE:[ Don't add any info or details, (No wishes)
        JUST begin with the question, no other text. 
        Only from this pdf. Keep it short. 
        No Hints or clues ]
                *** Follow the following format ***

**Question**: You will receive a multiple-choice question with four options (a, b, c, d). 

a) Option 1 \n
b) Option 2 \n
c) Option 3 \n
d) Option 4 \n

Example 1:

**Question 1**: what rat is eating? 

a) Cake \n
b) Cheese \n
c) Mushroom \n
d) Yogurt \n

Example 2:

**Question**: Where is Alex according to the passage? 

a) France \n
b) Dubai \n
c) Italy \n
d) Russia \n

Example 3: Only if content have passage and question

**Passage**: Brian watching a movie called "Alien" along with his girlfriend Sophia.

**Question**: Who is Brian girlfriend? 

a) Sophia \n
b) Diana \n
c) Sam \n
d) Ashley \n

Present this question to the user and wait for their response.\n"
    """
    result = rag_chain.invoke({"query": query})
    return result['result']

# Defining Func to validate answers
def validate_answers():
    feedback = []
    for question, user_answer in st.session_state.user_answers:
        validation_query = f"""
        You are given a question and an answer from a user. Decide whether the user's answer is correct or not, and provide feedback.
        Question: {question}, User's Answer: {user_answer}
        
        Provide feedback in the following format:
        - If the answer is correct, say "Correct!" and justify the answer.
        - If the answer is incorrect, provide the correct answer and explain why the user's answer was wrong.
        """
        feedback_result = rag_chain.invoke({"query": validation_query})
        feedback.append(feedback_result['result'])
    return feedback

# Defining Func to get overall score
def get_final_score():
    feedback_query = f"""
    Rate the user in percentage based on previous QA session.
    Score: {int(st.session_state.score)}/{st.session_state.total_questions}
    
    Provide feedback in the following format:
    Score: %
    """
    result = rag_chain.invoke({"query": feedback_query})
    return result['result']

# Defining Func to modify the llm output in specific format
def extract_question_and_answers(text):
    # Regular expression patterns
    question_pattern = re.compile(r"^(Who|How|What|Where|When|Why)\b.*?(?=\na\))", re.DOTALL | re.IGNORECASE)
    answer_pattern = re.compile(r"^[a-d]\) .*", re.MULTILINE)
    
    # Find question
    question_match = question_pattern.search(text)
    question = question_match.group(0) if question_match else "Default question here"
    
    # Find answers
    answers = answer_pattern.findall(text)
    
    return question, answers


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if docs[0].page_content == 'No Doc':
    st.markdown("Please Upload doc to start the quiz")
elif docs[0].page_content == 'No Url':
    st.markdown("Please Paste url to start the quiz")

# Get new question if needed
elif st.session_state.quiz_active and st.session_state.current_question is None:
    st.session_state.current_question = get_question()
    with st.chat_message("assistant"):
        
      # Extract question and answers
        question, answers = extract_question_and_answers(st.session_state.current_question)        

        # Initialize session state if not already done
        if 'current_question' not in st.session_state:
            st.session_state.current_question = question

        if 'options' not in st.session_state:
            st.session_state.options = answers

        st.markdown(st.session_state.current_question)
        # st.markdown(st.session_state.current_question)
    st.session_state.messages.append({"role": "assistant", "content": st.session_state.current_question})

# React to user input
if prompt := st.chat_input("Your answer:"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if st.session_state.quiz_active:
        # Store user's answer
        st.session_state.user_answers.append((st.session_state.current_question, prompt))
        
        # Update total questions
        st.session_state.total_questions += 1

        # Check if it's the last question
        if st.session_state.total_questions == 2:
            st.session_state.quiz_active = False
            
            # Validate all answers
            feedback = validate_answers()
            
            # Calculate score
            st.session_state.score = sum(1 for f in feedback if "Correct!" in f)
            
            # Display feedback
            with st.chat_message("assistant"):
                st.markdown("Thank you for participating! Here are your results:")
                feed = ''
                for i, f in enumerate(feedback, 1):
                    st.markdown(f"Question {i}: {f}")
                    result_text = f"Question {i}: {f}"
                    feed += result_text + "\n"
                    
                final_score = get_final_score()
                st.markdown(f"Final {final_score}")
                feed += final_score
                
                # Create a PDF instance
                pdf = FPDF()
                pdf.add_page()

                # Set font
                pdf.set_font("Times", size=12)
            
                # Add the string as text
                pdf.multi_cell(0, 10, feed)

                if not os.path.exists("Results"):
                    os.makedirs("Results")

                # Save the PDF to a file
                pdf.output("Results/feedback.pdf")  
                st.markdown("Feedback have been saved")  
                
                
            
            st.session_state.messages.append({"role": "assistant", "content": "Quiz ended. Results displayed."})
            sys.exit()

        else:
            # Get next question
            st.session_state.current_question = get_question()
            with st.chat_message("assistant"):
                st.markdown(st.session_state.current_question)
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.current_question})
