import streamlit as st
from ddgs import DDGS
import ollama
import sqlite3

from io import BytesIO
from html import escape
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)


# ==========================================
# 1. PAGE SETTINGS
# ==========================================

st.set_page_config(
    page_title="AI Web Research Agent",
    page_icon="🔎",
    layout="wide"
)


# ==========================================
# 2. DARK THEME CSS
# ==========================================

st.markdown("""
<style>

/* Main background */

.stApp {
    background: linear-gradient(
        135deg,
        #080d1b,
        #10172a,
        #111827
    );
    color: #f8fafc;
}

/* Main content */

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Headings */

h1, h2, h3 {
    color: #f8fafc !important;
    font-weight: 700 !important;
}

/* Normal text */

p, label, span {
    color: #d1d5e5;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #111827,
        #0b1020
    );
    border-right: 1px solid #293653;
}

/* Input fields */

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    background-color: #151e32 !important;
    color: white !important;
    border: 1px solid #53618a !important;
    border-radius: 12px !important;
}

/* Buttons */

.stButton button {
    background: linear-gradient(
        90deg,
        #7c3aed,
        #2563eb
    );
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1rem;
    font-weight: 700;
    transition: 0.3s;
}

.stButton button:hover {
    background: linear-gradient(
        90deg,
        #9333ea,
        #0ea5e9
    );
    transform: translateY(-2px);
}

/* Download button */

.stDownloadButton button {
    background: linear-gradient(
        90deg,
        #0891b2,
        #2563eb
    );
    color: white !important;
    border: none;
    border-radius: 12px;
}

/* Metric cards */

[data-testid="stMetric"] {
    background: #151e32;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #35456a;
}

/* Expanders */

[data-testid="stExpander"] {
    background-color: #151e32;
    border: 1px solid #35456a;
    border-radius: 12px;
}

/* Horizontal line */

hr {
    border-color: #35456a !important;
}

/* Success message */

[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Links */

a {
    color: #60a5fa !important;
}

/* Chat messages */

[data-testid="stChatMessage"] {
    background-color: #151e32;
    border: 1px solid #35456a;
    border-radius: 12px;
}

/* Footer */

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. DATABASE FUNCTIONS
# ==========================================

def create_database():

    conn = sqlite3.connect("research_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            summary TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_research(topic, summary):

    conn = sqlite3.connect("research_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO research (topic, summary, created_at)
        VALUES (?, ?, ?)
    """, (
        topic,
        summary,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_research_history():

    conn = sqlite3.connect("research_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, topic, summary, created_at
        FROM research
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    conn.close()

    return records


def delete_research(research_id):

    conn = sqlite3.connect("research_history.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM research WHERE id = ?",
        (research_id,)
    )

    conn.commit()
    conn.close()


create_database()


# ==========================================
# 4. SESSION STATE
# ==========================================

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = {}


# ==========================================
# 5. HEADER
# ==========================================

st.markdown("""
<div style="
    background: linear-gradient(120deg, #111c3b, #25205a, #075985);
    padding: 30px;
    border-radius: 20px;
    border: 1px solid #53618a;
    margin-bottom: 25px;
">

<h1 style="color:white; margin:0;">
🔎 AI Web Research Agent
</h1>

<p style="font-size:18px; color:#c7d2fe;">
Your Personal AI-Powered Research Assistant
</p>

<p style="color:#93c5fd;">
Research Smarter. Discover Faster. Understand Better.
</p>

</div>
""", unsafe_allow_html=True)


# ==========================================
# 6. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("⚙️ Settings")

    st.subheader("🤖 AI Model")

    provider = st.selectbox(
        "Select AI Provider",
        ["Free - Ollama"]
    )

    st.divider()

    st.subheader("📊 Research Depth")

    depth = st.selectbox(
        "Select Research Depth",
        [
            "Quick Research",
            "Standard Research",
            "Detailed Research"
        ]
    )

    st.divider()

    st.markdown("""
    ### 🚀 AI Web Research Agent

    Smarter Research.

    Deeper Insights.
    """)

    st.divider()

    st.markdown("""
    ### ✨ Features

    🌐 Automatic Web Search

    🤖 AI Research Summary

    📚 Research History

    🔍 Fact Checking (planned)

    📄 PDF Report

    💬 Chat with Research
    """)

    st.divider()

    st.caption("Built with Python, Streamlit and Ollama ❤️")


# ==========================================
# 7. DASHBOARD METRICS
# ==========================================

history = get_research_history()

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "🤖 AI Provider",
        "Ollama"
    )

with col2:

    st.metric(
        "🟢 Research Status",
        "Ready"
    )

with col3:

    st.metric(
        "📄 Reports Generated",
        len(history)
    )


st.divider()


# ==========================================
# 8. START NEW RESEARCH
# ==========================================

st.header("📝 Start New Research")

topic = st.text_area(
    "Enter your research topic",
    placeholder="Example: Impact of AI on Education in India",
    height=110
)


if st.button(
    "🚀 Start Research",
    use_container_width=True
):

    if topic.strip():

        try:

            st.success("Research started!")

            st.write("**Research Topic:**", topic)

            # WEB SEARCH

            with st.spinner("🌐 Searching the web..."):

                results = list(
                    DDGS().text(
                        topic,
                        max_results=5
                    )
                )

            if results:

                research_data = ""

                for result in results:

                    research_data += (
                        f"Title: {result['title']}\n"
                        f"Description: {result['body']}\n\n"
                    )

                # AI SUMMARY

                st.subheader("🤖 AI Research Summary")

                with st.spinner("🧠 Qwen AI is analyzing..."):

                    response = ollama.chat(

                        model="qwen3.5:4b",

                        messages=[

                            {
                                "role": "system",

                                "content": (
                                    "You are an expert research assistant. "
                                    "Summarize only the provided information. "
                                    "Do not invent facts. "
                                    "Mention important findings and limitations."
                                )
                            },

                            {
                                "role": "user",

                                "content": (
                                    f"Research Topic: {topic}\n\n"
                                    f"Research Depth: {depth}\n\n"
                                    f"Search Results:\n{research_data}\n\n"
                                    "Create a clear research summary with "
                                    "headings and bullet points."
                                )
                            }

                        ]
                    )

                summary = response["message"]["content"]

                st.write(summary)

                # SAVE IN DATABASE

                save_research(topic, summary)

                st.success("Research saved successfully! ✅")

                # WEB RESULTS

                st.subheader("🌐 Web Search Results")

                for i, result in enumerate(results, start=1):

                    with st.expander(
                        f"{i}. {result['title']}"
                    ):

                        st.write(result["body"])

                        st.markdown(
                            f"[Read Full Article]({result['href']})"
                        )

                # ==================================
                # PDF GENERATION
                # ==================================

                st.divider()

                st.subheader("📄 Download Research Report")

                pdf_buffer = BytesIO()

                document = SimpleDocTemplate(
                    pdf_buffer,
                    pagesize=A4,
                    rightMargin=45,
                    leftMargin=45,
                    topMargin=45,
                    bottomMargin=45
                )

                styles = getSampleStyleSheet()

                report_content = []

                report_content.append(
                    Paragraph(
                        "AI Web Research Report",
                        styles["Title"]
                    )
                )

                report_content.append(Spacer(1, 20))

                report_content.append(
                    Paragraph(
                        f"<b>Research Topic:</b> {escape(topic)}",
                        styles["Normal"]
                    )
                )

                report_content.append(Spacer(1, 15))

                report_content.append(
                    Paragraph(
                        f"<b>Research Depth:</b> {escape(depth)}",
                        styles["Normal"]
                    )
                )

                report_content.append(Spacer(1, 20))

                report_content.append(
                    Paragraph(
                        "AI Research Summary",
                        styles["Heading2"]
                    )
                )

                summary_text = escape(summary).replace(
                    "\n",
                    "<br/>"
                )

                report_content.append(
                    Paragraph(
                        summary_text,
                        styles["BodyText"]
                    )
                )

                report_content.append(Spacer(1, 20))

                report_content.append(
                    Paragraph(
                        "Web Search Sources",
                        styles["Heading2"]
                    )
                )

                for i, result in enumerate(results, start=1):

                    title = escape(result["title"])

                    url = escape(
                        result["href"],
                        quote=True
                    )

                    report_content.append(
                        Paragraph(
                            f"{i}. {title}<br/>"
                            f'<link href="{url}" color="blue">'
                            f"{url}</link>",
                            styles["BodyText"]
                        )
                    )

                    report_content.append(Spacer(1, 12))

                document.build(report_content)

                st.download_button(

                    label="⬇️ Download PDF Report",

                    data=pdf_buffer.getvalue(),

                    file_name="AI_Research_Report.pdf",

                    mime="application/pdf",

                    use_container_width=True
                )

            else:

                st.warning("No search results found.")

        except Exception as e:

            st.error(f"Research Error: {e}")

    else:

        st.warning("Please enter a research topic.")


# ==========================================
# 9. RESEARCH HISTORY
# ==========================================

st.divider()

st.header("📚 Research History")

history = get_research_history()

if history:

    for record in history:

        research_id, old_topic, old_summary, created_at = record

        with st.expander(
            f"🔎 {old_topic} — {created_at}"
        ):

            st.write("**Research ID:**", research_id)

            st.write("**Research Topic:**", old_topic)

            st.write("**AI Summary:**")

            st.write(old_summary)

            if st.button(
                "🗑️ Delete Research",
                key=f"delete_{research_id}"
            ):

                delete_research(research_id)

                st.session_state.chat_messages.pop(
                    research_id,
                    None
                )

                st.success("Research deleted!")

                st.rerun()

else:

    st.info("No previous research available yet.")


# ==========================================
# 10. CHAT WITH RESEARCH
# ==========================================

st.divider()

st.header("💬 Chat with Research")

st.write(
    "Ask questions about your previously saved research."
)

history = get_research_history()

if history:

    research_options = {
        f"{record[1]} — {record[3]}": record
        for record in history
    }

    selected_label = st.selectbox(
        "Select Research",
        list(research_options.keys())
    )

    selected_record = research_options[selected_label]

    research_id = selected_record[0]

    selected_topic = selected_record[1]

    selected_summary = selected_record[2]

    if research_id not in st.session_state.chat_messages:

        st.session_state.chat_messages[research_id] = []

    # DISPLAY OLD MESSAGES

    for message in st.session_state.chat_messages[research_id]:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # USER QUESTION

    question = st.text_input(
        "Ask your question",
        placeholder="Example: What are the main findings?"
    )

    if st.button(
        "🚀 Ask AI",
        use_container_width=True
    ):

        if question.strip():

            messages = [

                {
                    "role": "system",

                    "content": (
                        "You are a helpful research assistant. "
                        "Answer questions using the saved research summary. "
                        "If the answer is not present in the research, "
                        "clearly say that the information is not available "
                        "in the saved research. Do not invent facts.\n\n"
                        f"Research Topic: {selected_topic}\n\n"
                        f"Research Summary:\n{selected_summary}"
                    )
                }

            ]

            messages.extend(
                st.session_state.chat_messages[research_id]
            )

            messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            try:

                with st.spinner("🤖 AI is thinking..."):

                    response = ollama.chat(
                        model="qwen3.5:4b",
                        messages=messages
                    )

                answer = response["message"]["content"]

                st.session_state.chat_messages[research_id].append(
                    {
                        "role": "user",
                        "content": question
                    }
                )

                st.session_state.chat_messages[research_id].append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

                st.rerun()

            except Exception as e:

                st.error(f"Chat Error: {e}")

        else:

            st.warning("Please enter a question.")

else:

    st.info(
        "First complete a research topic. "
        "Then you can chat with your saved research."
    )


# ==========================================
# 11. UPCOMING FEATURES
# ==========================================

st.divider()

st.header("✨ Upcoming Features")

col1, col2 = st.columns(2)

with col1:

    st.write("🌐 Multiple Source Collection")

    st.write("🤖 Multiple AI Research Agents")

    st.write("📚 Advanced Research Library")

with col2:

    st.write("🔍 Fact Checking")

    st.write("📊 Research Analytics")

    st.write("🌍 Multi-language Research")


st.divider()

st.caption(
    "AI Web Research Agent | Python • Streamlit • Ollama • SQLite"
)