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
    font-size: 72px !important;    /* FORCE APPLY */
    font-weight: 900 !important;
    color: #FFFFFF !important;
    text-align: center !important;
    line-height: 1.1;

    /* Strong 3D Effect */
    text-shadow:
        3px 3px 0px rgba(0,0,0,0.4),
        6px 6px 0px rgba(0,0,0,0.3),
        9px 9px 0px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* Hide Streamlit top header */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    height: 0px !important;
    
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* Make SIDEBAR fixed and full-height */
[data-testid="stSidebar"] {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    height: 100vh !important;
    overflow-y: auto !important;
    z-index: 999 !important;
}

/* Adjust the main content to avoid overlap */
.main {
    margin-left: 300px !important;   /* sidebar width */
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>

/* ================= MAIN BACKGROUND + SIDEBAR ================= */

.stApp {
    background-color: #C62828 !important;
}


[data-testid="stSidebar"] {
    background-color: #C62828 !important;
}


/* ================= TEXT COLORS ================= */

.stApp, .stTextInput, .stMarkdown, .stRadio, .stButton,
label, h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
}


/* ================= INPUT BOXES ================= */

.stTextInput > div > div > input {
    background-color: #A91F1F !important;  /* slightly darker so visible */
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




</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Fix the main black container behind chat */
.main > div:last-child {
    background-color: transparent !important;
}

/* Fix chat messages */
[data-testid="stChatMessageContainer"] {
    background-color: transparent !important;
}

[data-testid="stChatMessage"] {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px;
    padding: 10px;
}

[data-testid="stChatMessage"] * {
    color: white !important;
}

/* Fix chat input wrapper - YE IMPORTANT HAI */
[data-testid="stBottom"] {
    background-color: transparent !important;
}

[data-testid="stChatInput"] {
    background-color: transparent !important;
}

[data-testid="stChatInput"] > div {
    background-color: rgba(169, 31, 31, 0.8) !important;
    border-radius: 10px;
}

[data-testid="stChatInput"] textarea {
    background-color: #A91F1F !important;
    color: white !important;
    border: 1px solid #ffffff55;
}

/* Bottom container fix */
.stChatFloatingInputContainer {
    background-color: transparent !important;
}

section[data-testid="stBottomBlockContainer"] {
    background-color: transparent !important;
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