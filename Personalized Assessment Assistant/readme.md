# Q/A Quiz Bot using LangChain.


Implementation:
1. Tools to run code: Python, API KEYS (for Gemini & Fireworks), a Docker.
2. If you want to run the code locally, call the command "docker run -p 8501:8501 quiz_app" in the terminal. 

Used Tools and models:
1. We used Gemini with model gemini-1.5-pro for Chat Conversation.
2. For Embeddings, we used Fireworks llm.
3. InMemoryVectorStore is used to store and retrieve data.
4. Streamlit is used for Web Interface.

How it Works:
1. Intially, Bot gonna ask user to upload the document or paste the youtube url to start the quiz.
2. Bot Starts, straight 10 Q/A Quiz session.
3. Generate the results along with feedback based on user answers at the end.

Features:
1. It can take any document type like Pdf, txt, Docx.
2. Also, It can take Youtube URLs.
3. We can setup How many questions need to be asked.
4. It saves the feedback along with Q/A Corrections as PDF in Result folder.
5. Also, it save the subtitles in subtitles folder.

  
