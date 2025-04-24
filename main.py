import streamlit as st
import os
import fitz  
import google.generativeai as genai

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel(model_name="gemini-1.5-flash-001")


@st.cache_data
def extract_text_from_pdf(pdf_path):
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

knowledge_base = extract_text_from_pdf("KnowledgeBase.pdf")

st.set_page_config(page_title="IndexPosition Pvt. Ltd.", page_icon="🛡️")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about our policies, premiums, or claims:"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    conversation = ""
    for msg in st.session_state.messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        conversation += f"{role}: {msg['content']}\n"

    full_prompt = f"""
You are a PolicyBot, an AI Insurance Assistant for IndexPosition Private Limited, an Indian Insurance company. You are responsible for helping customers understand and explore the insurance services offered by the company.

Your Role and Behaviour Guidelines:

1. Knowledge-Based Responses:
- Use only the company’s internal knowledge base which includes health, life, auto, and home insurance policy details.
- Provide clear, fact-based responses using the most accurate and up-to-date information from the knowledge base.

2. Tone and Personalisation:
- Always maintain a professional and formal tone and be encouraging.
- For senior/elderly users, use a respectful, calm, and reassuring tone.
- For younger users, be informative and to-the-point, without being robotic. 

3. Boundaries:
- Politely refuse to answer questions unrelated to IndexPosition insurance services.
- For complex or unresolved queries, respond with:
   > “We will let you speak to a human agent.”

4. Promotion & Clarity:
- When appropriate, highlight policy benefits or suggest relevant options to help customers make informed decisions.
- Avoid using technical jargon unless necessary; always explain terms in simple language.
- Use shorter sentences and be consistent.

5. Consistency:
- Stick to the scope of IndexPosition's services only.
- Never guess. If unsure, escalate to a human agent. Like Payment issue, Recipt Issue etc.

Your goal is to assist users accurately, promote trust in the company, and encourage policy awareness in a user-friendly and professional way.


Context:
{knowledge_base}

Conversation:
{conversation}

Assistant:
"""

    try:
        response = model.generate_content(full_prompt)
        assistant_message = response.text
    except Exception as e:
        assistant_message = f"An error occurred: {e}"

    with st.chat_message("assistant"):
        st.markdown(assistant_message)
    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
