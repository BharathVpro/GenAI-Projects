# Import required modules
import streamlit as st
import re
import sys
import os 
import json
import getpass
import langchain
# pip install langchain==0.1.0
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryMemory
# pip install langchain-groq==0.0.1
from langchain_groq import ChatGroq
from langchain.chains import ConversationChain


os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')
os.environ["GOOGLE_API_KEY"] = os.getenv('GOOGLE_API_KEY')

# llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
llm = ChatGroq(model="llama3-8b-8192")

#memory
memory = ConversationSummaryMemory(llm = llm)

#chain
conversation = ConversationChain(llm = llm, memory=memory)


# Function to get a new question from the AI Tutor
def get_question():
    query = """Generate a any random Sat English Passage followed by 10 random questions, Respond in following format:
    chat history = {chat_history_text}
    Set difficulty level based on previous user answers for questions from chat history, default : Tough (Difficulty levels: Easy, Medium, Hard, Tough, Extreme Tough, Insane.) 
Here’s a clean EXAMPLE format of the passage followed by questions and options: 
NOTE: Response format strictly should starts from passage (NEVER use or copy this example passage as a response):


**Example Passage:**

_"Here's a rewrite of the passage at an SAT English level, expanded into three paragraphs:

For countless generations, women have been confined to indoor spaces, their potential for creativity stifled by societal constraints. This prolonged confinement has left an indelible mark on their surroundings, as if the very walls have absorbed their untapped artistic energy. However, due to forced inactivity, this creative force has deteriorated, much like metal corroding into rust or organic matter decaying into mold.

The metaphorical "five hundred a year" represents financial independence, a crucial factor in fostering intellectual freedom. This sum symbolizes the ability to step back from daily concerns and engage in deep, meaningful contemplation. It provides the means to explore one's thoughts and ideas without the constant pressure of economic survival, allowing for the cultivation of original and innovative thinking.

The imagery of "a lock on the door" goes beyond mere physical security; it represents the power of intellectual autonomy. This lock serves as a barrier against external interruptions and influences, creating a sanctuary for independent thought. It allows individuals to develop their own perspectives, free from the constant intrusion of societal expectations or the opinions of others. This private space becomes a crucible for personal growth and the development of unique ideas, essential for true creative and intellectual expression.

**Questions: (Level:  )**

1. {**What does the phrase “turned to rust and mold” suggest about women’s creative force?**}
   - A. It has been neglected due to inactivity.
   - B. It has been preserved for future generations.
   - C. It has been celebrated by society.
   - D. It has been strengthened through isolation.

2. {**According to Woolf, what does “five hundred a year” symbolize?**}
   - A. The need for women’s financial independence.
   - B. The cost of education.
   - C. The limitations of women’s rights.
   - D. The power to live comfortably.

3. {**What does the speaker imply about the role of inactivity in women’s lives?**}
   - A. It has enhanced their intellectual abilities.
   - B. It has hindered their creative potential.
   - C. It has given them new opportunities.
   - D. It has liberated them from societal norms.

4. {**The “lock on the door” in the passage is symbolic of:**}
   - A. The confinement of women to the home.
   - B. The privacy needed for creative work.
   - C. The lack of opportunities for women.
   - D. The separation of women from society.

5. {**What does Woolf imply is necessary for women to reach their full creative potential?**}
   - A. Financial independence and intellectual freedom.
   - B. Greater access to educational resources.
   - C. Support from the male-dominated society.
   - D. More time spent in isolation.

6. {**What tone does Woolf adopt in this passage?**}
   - A. Reflective.
   - B. Resentful.
   - C. Lighthearted.
   - D. Sarcastic.

7. {**What is the significance of “millions of years” in the passage?**}
   - A. It emphasizes the long history of women’s intellectual confinement.
   - B. It highlights the progress women have made.
   - C. It suggests that women’s role has been static.
   - D. It downplays the significance of change.

8. {**Woolf’s use of the phrase “creative force” refers to:**}
   - A. The physical strength of women.
   - B. The intellectual and artistic potential of women.
   - C. The ability to engage in domestic work.
   - D. The financial contributions of women.

9. {**The passage suggests that Woolf views financial independence as:**}
   - A. A key to intellectual freedom.
   - B. A barrier to creative work.
   - C. Irrelevant to women’s success.
   - D. A sign of societal status.

10. {**Woolf’s argument most strongly supports which of the following?**}
    - A. Women should prioritize financial independence.
    - B. Creative and intellectual freedom requires time and privacy.
    - C. Society should reward women for their domestic contributions.
    - D. Education is the most important tool for women’s empowerment.
    

Note: Response should end like 10th question followed by options. 
"""
    question = conversation.invoke(query)['response']
    return question

# Function to validate the user's answer
def validate_answer(question, user_input):
    validation_query = f"""
    You are given a Passage followed by 10 questions and an answer from a user for each question. 
    Passage, Questions with options: {question}, User's Answers: {user_input} (If user's answer is None, Say like atleast user could have give a try)
    Match the user's answers with questions and validate whether the user's answer is correct or not, and provide feedback.
    Don't say anything, just provide feedback in the following format:
    - If the answer is correct, say "Correct!"
    - If the answer is incorrect, provide the correct answer and explain why the user's answer was wrong. Tell user work on the topic which user lacks
    - Give Feedback which topic or area or context user lacks in 5 lines.
    """
    feedback_result = conversation.invoke(validation_query)['response']
    return feedback_result

# user_input = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None, 10: None}
data = []

# App layout
st.title("Adaptive Sat Eng Quiz Bot")


# Initialize session state variables
if 'question_number' not in st.session_state:
    st.session_state.question_number = 1
if 'show_next_button' not in st.session_state:
    st.session_state.show_next_button = False
if 'submit_button' not in st.session_state:
    st.session_state.submit_button = True
if 'question' not in st.session_state:
    st.session_state.question = get_question()  # Generate the initial question
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to add message to chat history (without displaying)
def add_to_chat(role, content):
    st.session_state.chat_history.append({"role": role, "content": content})

# Main loop for asking questions and getting answers
if st.session_state.question_number <= 2:  # Adjust the number of questions as needed
    # Display the current question
    response = st.session_state.question
    passage = re.search(r'(Passage.*?)(?=Questions)', response, re.DOTALL).group(1)
    questions = re.findall(r'\{(.*?)\}', response, re.DOTALL)
    options = re.findall(r'([A-D]\. .+)', response)
    options_grouped = [options[i:i+4] for i in range(0, len(options), 4)]

    add_to_chat("assistant", f"Question {st.session_state.question_number}:\n{passage}")

    st.sidebar.write(passage)

    data = []
    for i in range(len(questions)):
        a = questions[i]
        selected_option = st.radio(
            a,
            options_grouped[i],
            index=None,
            key=f"question_{i}"
        )
        data.append(selected_option)
        st.write("")

    user_input = str(data)

    if st.button("Submit"):
        add_to_chat("human", f"My answer: {user_input}")
        feedback = validate_answer(st.session_state.question, user_input)
        st.write(f"Feedback: {feedback}")
        add_to_chat("assistant", f"Feedback: {feedback}")
        st.session_state.show_next_button = True
        st.session_state.submit_button = False
    
    if st.session_state.show_next_button:
        if st.button("Next Question"):
            st.session_state.question_number += 1
            st.session_state.show_next_button = False
            st.session_state.question = get_question()
            add_to_chat("assistant", "Moving to the next question.")
            st.rerun()
else:
   
    # Prepare chat history for the conversation
    chat_history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])
    # st.markdown(chat_history_text)
    # Getting overall feedback using chat history
    overall_feedback = conversation.invoke(f"""Based on the following Q/A session:

{chat_history_text}

Please provide:
Feedback :
1. Recap: Summarize the Q/A session and Give Short recap with examples(every session have diferent passage) in 6 lines.
2. Feedback: Explain where the user lacks in terms of context (with examples from the Q/A session along with with context and content). (3 lines)
3. Report: Indicate the current difficulty level the user can handle based on their score. (1 line)
    """)['response']
    
    # st.write("Overall Feedback:")
    st.write(overall_feedback)
    add_to_chat("assistant", f"Overall Feedback:\n{overall_feedback}")

    # # Display the final chat history
    # st.title("Final Chat History")
    # for message in st.session_state.chat_history:
    #     role = message["role"].capitalize()
    #     content = message["content"]
    #     st.text(f"{role}: {content}")
    #     st.write("---")  # Add a separator between messages

    # if st.button("Restart Quiz"):
    #     # Reset all necessary session state variables
    #     st.session_state.question_number = 1
    #     st.session_state.show_next_button = False
    #     st.session_state.submit_button = True
    #     st.session_state.question = get_question()  # Generate the initial question
    #     st.session_state.chat_history = []
    #     st.rerun()

    # # Optional: You can add a download button for the chat history
    # if st.button("Download Chat History"):
    #     chat_history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])
    #     st.download_button(
    #         label="Download Chat History",
    #         data=chat_history_str,
    #         file_name="quiz_chat_history.txt",
    #         mime="text/plain"
    #     )