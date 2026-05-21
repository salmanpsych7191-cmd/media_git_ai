import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
import os
from datetime import datetime

# --- Configuration and Initialization ---

# 1. Load environment variables (for GROQ_API_KEY)
load_dotenv(override=True)

# 2. INITIALIZE THE GROQ CLIENT!
groq_client = None
try:
    groq_client = Groq()
except Exception as e:
    st.error(f"⚠️ Failed to initialize Groq client. Please check your GROQ_API_KEY environment variable. Error: {e}")
    
# 3. Define the candidate's profile
name = "Mohammed Salman"
primary_role_1 = "Assistant Manager (SAP HANA & AI Solutions)"
primary_role_2 = "Enterprise Systems & Innovation Leader"
current_company = "Deloitte Support Services India Pvt. Ltd."

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Data Loading ---

resume_docx = ""
linkedin = ""
summary = ""

resume_docx_path = os.path.join(BASE_DIR, "RESUME_Assistant_Manager_Updated.docx")
pdf_path = os.path.join(BASE_DIR, "me", "linkedin.pdf")
summary_path = os.path.join(BASE_DIR, "me", "summary.txt")

try:
    if os.path.exists(resume_docx_path):
        resume_doc = Document(resume_docx_path)
        resume_docx = "\n".join(
            para.text.strip() for para in resume_doc.paragraphs if para.text and para.text.strip()
        )
except Exception as e:
    st.error(f"Failed to read updated resume DOCX: {e}")

try:
    if os.path.exists(pdf_path):
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                linkedin += text
except Exception as e:
    st.error(f"Error reading LinkedIn PDF: {e}")

try:
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = f.read()
except Exception as e:
    st.error(f"Error reading summary file: {e}")

if not (resume_docx or linkedin or summary):
    st.warning("No profile context files were found. Add at least one context source for best responses.")


# 4. Construct the System Prompt
system_prompt = f"""
You are acting as {name}. You are answering questions on {name}'s professional resume website,
particularly questions related to career background, leadership experience, technical skills, and project delivery.

Current professional positioning:
- Title: {primary_role_1}
- Focus: {primary_role_2}
- Current Company: {current_company}

Behavior requirements:
- Be professional, clear, and concise in English.
- Present {name} as a senior leader with deep SAP HANA expertise and strong AI innovation experience.
- Highlight leadership, governance, mentoring, stakeholder management, and enterprise delivery impact.
- Only use facts from the provided context below.
- Explicitly state when details are not available in the provided information.
- Do not invent numbers, certifications, or employers.

## Updated Resume Content:
{resume_docx}

## Summary:
{summary}

## LinkedIn Profile:
{linkedin}

Always remain in character as {name} and answer as a professional representative profile assistant.
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
            model="llama-3.1-8b-instant",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred while communicating with the Groq API. This could be a connectivity issue or an invalid API key. Error: {e}"


# --- Streamlit Application Layout ---

st.set_page_config(page_title=f"{name} | Assistant Manager Profile", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Source+Serif+4:wght@600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Manrope', sans-serif;
    }

    .hero-wrap {
        background: linear-gradient(125deg, #091827 0%, #12304f 58%, #1f4e77 100%);
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        color: #f4f8fd;
        border: 1px solid #2b557f;
        box-shadow: 0 10px 28px rgba(6, 20, 36, 0.25);
    }

    .hero-title {
        margin: 0;
        font-family: 'Source Serif 4', serif;
        font-size: 2.0rem;
        line-height: 1.1;
    }

    .hero-role {
        font-size: 1.0rem;
        color: #d8e8fb;
        margin-top: 0.35rem;
    }

    .hero-sub {
        margin-top: 0.7rem;
        font-size: 0.95rem;
        color: #c8def4;
    }

    .metric-card {
        background: #f8fbff;
        border: 1px solid #d5e2f0;
        border-radius: 12px;
        padding: 0.9rem;
        min-height: 78px;
    }

    .proof-card {
        background: #fffdfa;
        border: 1px solid #e5d6b6;
        border-left: 4px solid #c79a42;
        border-radius: 10px;
        padding: 0.85rem;
        min-height: 90px;
    }

    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        border: 1px solid #cad8e8;
        background: #f3f7fc;
        color: #23364f;
        font-size: 0.82rem;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
    }

    .facts {
        background: #f9fbfd;
        border: 1px solid #d8e2ec;
        border-radius: 12px;
        padding: 0.9rem;
    }

    .small-note {
        color: #4c637a;
        font-size: 0.84rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="hero-wrap">
        <h2 class="hero-title">{name}</h2>
        <div class="hero-role">{primary_role_1} | {primary_role_2}</div>
        <div class="hero-sub">
            Leadership in SAP HANA operations, cloud transformation, and enterprise AI adoption.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

cta_col1, cta_col2, cta_col3 = st.columns(3)
with cta_col1:
    st.link_button("Email", "mailto:mohammed.salman7191@gmail.com", use_container_width=True)
with cta_col2:
    st.link_button("Call", "tel:+918142471256", use_container_width=True)
with cta_col3:
    if os.path.exists(resume_docx_path):
        with open(resume_docx_path, "rb") as f:
            st.download_button(
                "Download Resume",
                data=f.read(),
                file_name="Mohammed_Salman_Assistant_Manager_Resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
    else:
        st.button("Resume Not Found", disabled=True, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card"><b>Experience</b><br/>11+ years in SAP ecosystem</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><b>Leadership Scope</b><br/>Mentored 15+ SAP BASIS consultants</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><b>Enterprise Delivery</b><br/>99.9% uptime across 150+ applications</div>', unsafe_allow_html=True)

p1, p2, p3 = st.columns(3)
with p1:
    st.markdown('<div class="proof-card"><b>Incident Resolution</b><br/>AI troubleshooting workflows reduced mean resolution time by 60%+.</div>', unsafe_allow_html=True)
with p2:
    st.markdown('<div class="proof-card"><b>Cloud Migration</b><br/>Led SAP ECC/HANA transition from on-premises to GCP with controlled risk.</div>', unsafe_allow_html=True)
with p3:
    st.markdown('<div class="proof-card"><b>Cost Optimization</b><br/>Performance tuning and memory optimization contributed to 25%+ savings.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Recruiter Quick Facts")
    st.markdown("<div class='facts'><b>Current Company:</b> Deloitte Support Services India Pvt. Ltd.<br/><b>Current Role:</b> Assistant Manager (SAP HANA & AI Solutions)<br/><b>Experience:</b> 11+ years<br/><b>Location:</b> Hyderabad, India<br/><b>Focus:</b> SAP HANA, Cloud Migration, AI Agents</div>", unsafe_allow_html=True)
    st.markdown("### Expertise")
    st.markdown("<span class='badge'>SAP HANA 2.0</span><span class='badge'>ECC 6.0</span><span class='badge'>GCP</span><span class='badge'>Azure</span><span class='badge'>AI Agents</span><span class='badge'>IT Governance</span>", unsafe_allow_html=True)
    st.caption("All responses are generated from provided resume/profile context.")

tab_chat, tab_profile, tab_context = st.tabs(["AI Assistant", "Profile Snapshot", "Knowledge Context"])

# Initialize chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": (
                f"Hello. I am {name}'s profile assistant. "
                f"I can help with questions about experience as **{primary_role_1}** "
                f"with focus on SAP HANA operations, AI initiatives, leadership, and delivery impact."
            ),
        }
    ]

def log_user_prompt(user_prompt):
    """Appends the user's prompt with a timestamp to a log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] USER PROMPT: {user_prompt}\n"
    try:
        with open("chat_logs.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error logging prompt: {e}")


def process_prompt(prompt_text):
    """Send user prompt to model and persist complete conversation."""
    log_user_prompt(prompt_text)
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt_text)

    with st.spinner("Preparing a professional response..."):
        full_response = get_groq_response(st.session_state.messages)

    with st.chat_message("assistant", avatar="💼"):
        st.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})


with tab_chat:
    st.markdown("### Recruiter Q&A")
    st.caption("Ask about leadership scope, migration ownership, AI outcomes, governance, and team impact.")

    q1, q2 = st.columns(2)
    q3, q4 = st.columns(2)
    if q1.button("Leadership responsibilities in current role", use_container_width=True):
        process_prompt("What are Mohammed Salman's core leadership responsibilities as Assistant Manager?")
    if q2.button("Cloud migration ownership and impact", use_container_width=True):
        process_prompt("Explain his role in cloud migration and the business impact delivered.")
    if q3.button("AI initiatives and measurable outcomes", use_container_width=True):
        process_prompt("What AI initiatives has he led and what measurable outcomes were achieved?")
    if q4.button("Why hire him for Assistant Manager role", use_container_width=True):
        process_prompt("Why is he a strong fit for Assistant Manager positions in SAP and AI-driven operations?")

    for message in st.session_state.messages:
        avatar = "💼" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask a professional question about the Assistant Manager profile...")
    if prompt:
        process_prompt(prompt)


with tab_profile:
    st.markdown("### Executive Profile Summary")
    st.markdown(
        """
        - Current Company: Deloitte Support Services India Pvt. Ltd.
        - Assistant Manager with 11+ years in SAP HANA and enterprise systems delivery.
        - Leads technical teams, governance practices, and business continuity initiatives.
        - Drives cloud migration programs and AI-enabled operations modernization.
        - Strong track record in uptime, cost optimization, and incident resolution acceleration.
        """
    )
    st.markdown("### Suggested Recruiter Questions")
    st.markdown(
        """
        - What are his leadership responsibilities as Assistant Manager?
        - What measurable outcomes has he delivered in SAP HANA operations?
        - How does he combine AI initiatives with enterprise infrastructure?
        - What was his role in cloud migration and governance?
        """
    )
    st.markdown("<div class='small-note'>Tip: Use the one-click question buttons in the AI Assistant tab for faster recruiter screening conversations.</div>", unsafe_allow_html=True)


with tab_context:
    st.markdown("### Context Loaded into Assistant")
    st.subheader("Updated Resume DOCX")
    st.code(resume_docx[:2500] + "..." if resume_docx else "No updated resume DOCX loaded.", language="text")
    st.subheader("Summary")
    st.code(summary if summary else "No summary loaded.", language="text")
    st.subheader("LinkedIn Profile Snippet")
    st.code(linkedin[:1200] + "..." if linkedin else "No LinkedIn data loaded.", language="text")