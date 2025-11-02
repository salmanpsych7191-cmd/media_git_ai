# enhanced_app.py

import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader
import os

# --- Configuration and Initialization ---

# 1. Load environment variables (for GROQ_API_KEY)
load_dotenv(override=True)

# 2. INITIALIZE THE GROQ CLIENT!
groq_client = None
try:
    groq_client = Groq()
except Exception as e:
    st.error(f"⚠️ Failed to initialize Groq client. Please check your GROQ_API_KEY environment variable. Error: {e}")
    
# 3. Define the candidate's name and primary roles
name = "Salman Mohd"
primary_role_1 = "SAP HANA Administrator"
primary_role_2 = "Agentic AI Beginner"

# --- Data Loading ---

# NOTE: The paths "me/linkedin.pdf" and "me/summary.txt" must be correct 
# relative to where you run the streamlit script.
# **CRITICAL**: Ensure 'me/linkedin.pdf' and 'me/summary.txt' exist in your file system.

linkedin = ""
pdf_path = "me/linkedin.pdf"
try:
    if os.path.exists(pdf_path):
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                linkedin += text
    else:
        st.warning(f"📄 LinkedIn PDF not found at: {pdf_path}. Chatbot context may be limited.")
except Exception as e:
    st.error(f"❌ Error reading LinkedIn PDF: {e}")

summary = ""
summary_path = "me/summary.txt"
try:
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = f.read()
    else:
        st.warning(f"📝 Summary file not found at: {summary_path}. Chatbot context may be limited.")
except Exception as e:
    st.error(f"❌ Error reading summary file: {e}")


# 4. Construct the System Prompt
system_prompt = f"""
You are acting as {name}. You are answering questions on {name}'s website, 
particularly questions related to {name}'s career, background, skills, and experience as a 
**{primary_role_1}** and **{primary_role_2}**.
Your responsibility is to represent {name} for interactions on the website as faithfully as possible.
You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions.
Be professional, engaging, and don't use any other language other than English, as if talking to a potential client or future employer who came across the website.
When discussing the SAP HANA Admin role, focus on database administration, performance tuning and security which is mentioned in the PDF. Also mention in the interaction that all responses are with in the information provided by {name} not from LLM search
When discussing on AI agents, LLMs, and leveraging large models for complex tasks.
If you don't know the answer, say so clearly and professionally.

## Summary:
{summary}

## LinkedIn Profile:
{linkedin}

With this context, please chat with the user, always staying in character as {name}.
"""

# --- Chat Function ---

def get_groq_response(chat_history):
    """Formats the Streamlit history and calls the Groq API for a response."""
    if not groq_client:
        return "The Groq client is not initialized. Cannot generate a response."

    # Format history for API: [system_prompt, *history_from_session_state]
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Add history from session_state
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant", # A good balance of speed and capability
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred while communicating with the Groq API. This could be a connectivity issue or an invalid API key. Error: {e}"


# --- Streamlit Application Layout ---

st.set_page_config(page_title=f"{name}'s AI Resume Chatbot 🤖", layout="wide")

# Main Header Section
st.title(f"🤝 Chat with {name}'s AI Assistant")
st.markdown(f"""
### **{name}** | {primary_role_1} & {primary_role_2}
""")

st.caption("Powered by **Groq** (for fast LLM responses) and Streamlit.")

# --- Context Expansion for Visibility ---
with st.expander("🔍 View Context Provided to the AI"):
    st.subheader("Summary")
    st.code(summary if summary else "No summary loaded.", language='text')
    st.subheader("LinkedIn Profile Snippet")
    st.code(linkedin[:500] + "..." if linkedin else "No LinkedIn data loaded.", language='text')
    st.caption("This data is used to inform the AI's responses.")

st.markdown("---")

# Initialize chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": f"Hello! I'm {name}'s AI assistant. I can answer questions about Salman's experience in **{primary_role_1}** and **{primary_role_2}**. What would you like to know?"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    # Use a relevant icon for the assistant
    avatar = "🤖" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask about SAP HANA Administration, Agentic AI projects, or any of my skills..."):
    # *** NEW LOGGING CODE STARTS HERE ***
    
    # Define a function to log the prompt
    def log_user_prompt(user_prompt):
        """Appends the user's prompt with a timestamp to a log file."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] USER PROMPT: {user_prompt}\n"
        try:
            # 'a' mode appends to the file. Creates it if it doesn't exist.
            with open("chat_logs.txt", "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            # You might want to log this error somewhere else too
            print(f"Error logging prompt: {e}")

    # Call the logging function immediately after receiving the prompt
    log_user_prompt(prompt)
    
    # *** NEW LOGGING CODE ENDS HERE ***
    
    # 1. Add user message to chat history and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Get the model's response
    # Pass the updated history list including the user's latest prompt
    with st.spinner("🧠 Thinking... Generating response in milliseconds via Groq..."):
        full_response = get_groq_response(st.session_state.messages)
        
    # 3. Display assistant response
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(full_response)
        
    # 4. Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})