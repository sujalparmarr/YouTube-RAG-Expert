import streamlit as st
from streamlit import spinner
from streamlit.web.server.server import server_port_is_manually_set

from supporting_functions import (
     extract_video_id,
     get_transcript,
     translate_transcript,
     generate_notes,
     get_important_topics,
     create_chunks,
     create_vector_store,
     rag_answer
)

st.markdown("""
<style>
.yt-title-3d {
    font-size: 72px !important;
    font-weight: 900 !important;
    color: #FFFFFF !important;
    text-align: center !important;
    line-height: 1.1;
    text-shadow:
        3px 3px 0px rgba(0,0,0,0.4),
        6px 6px 0px rgba(0,0,0,0.3),
        9px 9px 0px rgba(0,0,0,0.2);
}

/* Hide Streamlit top header */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    height: 0px !important;
}

/* Make SIDEBAR fixed and full-height */
[data-testid="stSidebar"] {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    height: 100vh !important;
    overflow-y: auto !important;
    z-index: 999 !important;
    background-color: #C62828 !important;
}

/* Adjust the main content to avoid overlap */
.main {
    margin-left: 300px !important;
    background-color: #C62828 !important;
}

/* ================= FORCE RED EVERYWHERE ================= */
.stApp,
.stApp > header,
.stApp > div,
body,
html,
[data-testid="stAppViewContainer"],
.main,
section {
    background-color: #C62828 !important;
}

/* ================= TEXT COLORS ================= */
.stApp, .stTextInput, .stMarkdown, .stRadio, .stButton,
label, h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
}

/* ================= INPUT BOXES ================= */
.stTextInput > div > div > input {
    background-color: #A91F1F !important;
    color: white !important;
    border: 1px solid #ffffff55;
}

/* ================= RADIO BUTTONS ================= */
.stRadio > label,
.stRadio > div > label {
    color: white !important;
}

/* ================= BUTTONS ================= */
.stButton > button {
    background-color: white !important;
    color: #C62828 !important;
    border-radius: 8px;
    border: 2px solid #ffffff;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #f0f0f0 !important;
    color: #C62828 !important;
}

/* ================= ULTIMATE BLACK BOX KILLER ================= */

/* Kill ALL possible black/dark backgrounds */
* {
    scrollbar-color: #A91F1F #C62828 !important;
}

/* Every single div, section, and container */
div, section, main, article, aside {
    background-color: inherit !important;
}

/* But force root containers to red */
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.stApp,
.main,
[data-testid="stMainBlockContainer"] {
    background-color: #C62828 !important;
}

/* Chat specific - ABSOLUTE OVERRIDE */
section[data-testid="stBottom"],
section[data-testid="stBottom"] *,
[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"] *,
[data-testid="stChatFloatingInputContainer"],
[data-testid="stChatFloatingInputContainer"] *,
.stChatFloatingInputContainer,
.stChatFloatingInputContainer * {
    background-color: #C62828 !important;
    background: #C62828 !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    background-color: #C62828 !important;
}

[data-testid="stChatInput"] > div {
    background-color: #C62828 !important;
    padding: 10px;
}

[data-testid="stChatInput"] textarea {
    background-color: #A91F1F !important;
    color: white !important;
    border: 1px solid #ffffff55 !important;
    border-radius: 10px !important;
}

/* Chat messages */
[data-testid="stChatMessageContainer"] {
    background-color: #C62828 !important;
}

[data-testid="stChatMessage"] {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px;
    padding: 10px;
}

[data-testid="stChatMessage"] * {
    color: white !important;
}

/* Override any inline styles that might be setting black */
[style*="background-color: rgb(0, 0, 0)"],
[style*="background-color: black"],
[style*="background: rgb(0, 0, 0)"],
[style*="background: black"] {
    background-color: #C62828 !important;
    background: #C62828 !important;
}

/* Target the specific problematic container */
.main > div[data-testid="block-container"] ~ div {
    background-color: #C62828 !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Make radio buttons compact and aligned */
.stRadio > div {
    background-color: rgba(0, 0, 0, 0.2) !important;
    padding: 5px !important;
    border-radius: 10px !important;
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
}

/* Radio button text labels - SUPER TIGHT */
.stRadio label {
    color: #FFFFFF !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    padding: 7px 12px !important;
    display: block !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    margin: 0px !important;
}

/* Hide ONLY the radio circle, not the text */
.stRadio [data-baseweb="radio"] > div {
    display: none !important;
}

/* Keep the label text visible */
.stRadio label > div:last-child {
    display: block !important;
    color: white !important;
}

/* When selected - highlight with WHITE background */
.stRadio input[type="radio"]:checked + div {
    background-color: rgba(255, 255, 255, 0.3) !important;
    border: 2px solid white !important;
    border-radius: 8px !important;
    padding: 7px 12px !important;
    font-weight: 700 !important;
}

/* Not selected - subtle background */
.stRadio input[type="radio"]:not(:checked) + div {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 2px solid transparent !important;
    border-radius: 8px !important;
    padding: 7px 12px !important;
}

/* Hover effect */
.stRadio label:hover {
    background-color: rgba(255, 255, 255, 0.15) !important;
}

/* ZERO gap between radio items */
.stRadio > div > label {
    margin-bottom: 0px !important;
}

.stRadio > div > label:last-child {
    margin-bottom: 0 !important;
}

/* Remove extra spacing in radio group */
.stRadio [role="radiogroup"] {
    gap: 0px !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Make "Choose what you want to generate:" label bigger */
.stRadio > label,
.stRadio > div > label:first-child,
[data-testid="stWidgetLabel"] {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: white !important;
    margin-bottom: 8px !important;
}

/* Specifically target the radio group label */
.stRadio > label > div {
    font-size: 16px !important;
}

</style>
""", unsafe_allow_html=True)

# --- Sidebar (Inputs) ---
with st.sidebar:
    st.title("🎬YouTube Analyzer")
    st.markdown("---")
    st.markdown("Transform any YouTube video into key topics, a podcast, or a chatbot.")
    st.markdown("### Input Details")

    youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    language = st.text_input("Video Language Code", placeholder="e.g., en, hi, es, fr", value="en")

    task_option = st.radio(
        "Choose what you want to generate:",
        ["Chat with Video", "Notes For You"]
    )

    submit_button = st.button("✨ Start Processing")
    st.markdown("---")
    # The "New Chat" button has been removed from here.

# --- Main Page ---
st.markdown("<h1 class='yt-title-3d'>YouTube RAG Expert</h1>", unsafe_allow_html=True)
st.markdown("Paste a video link and select a task from the sidebar.")




# --- Processing Flow ---
if submit_button:
    if youtube_url and language:
        video_id= extract_video_id(youtube_url)
        if video_id:
            with spinner("Step 1/3 : Fetching Transcript....."):
                full_transcript= get_transcript(video_id, language)

                if language!="en":
                    with spinner("Step 1.5/3 : Translating Transcript into English, This may take few moments......"):
                        full_transcript= translate_transcript(full_transcript)


            if task_option=="Notes For You":
                with spinner("Step 2/3: Extracting important Topics..."):
                    import_topics= get_important_topics(full_transcript)
                    st.subheader("Important Topics")
                    st.write(import_topics)
                    st.markdown("---")

                with spinner("Step 3/3 : Generating Notes for you."):
                    notes= generate_notes(full_transcript)
                    st.subheader("Notes for you")
                    st.write(notes)

                st.success("Summary and Notes Generated.")

            if task_option == "Chat with Video":
                with st.spinner("Step 2/3: Creating chunks and vector store...."):
                    chunks = create_chunks(full_transcript)
                    vectorstore = create_vector_store(chunks)
                    st.session_state.vector_store = vectorstore
                st.session_state.messages=[]
                st.success('Video is ready for chat.....')


# chatbot session
if task_option=="Chat with Video" and "vector_store" in st.session_state:
    st.divider()
    st.subheader("Chat with Video")

    # Display the entire history
    for message in st.session_state.get('messages',[]):
        with st.chat_message(message['role']):
            st.write(message['content'])

    # user_input
    prompt= st.chat_input("Ask me anything about the video.")
    if prompt:
        st.session_state.messages.append({'role':'user','content':prompt})
        with st.chat_message('user'):
            st.write(prompt)

        with st.chat_message('assistant'):
           response= rag_answer(prompt,st.session_state.vector_store)
           st.write(response)
        st.session_state.messages.append({'role': 'assistant', 'content':response})