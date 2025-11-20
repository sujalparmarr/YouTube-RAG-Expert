import time

from dotenv import load_dotenv
import re
import streamlit as st

from youtube_transcript_api import YouTubeTranscriptApi

from langchain_text_splitters import RecursiveCharacterTextSplitter

# FREE EMBEDDINGS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


# Function to extract video ID from a YouTube URL (Helper Function)
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if match:
        return match.group(1)
    st.error("Invalid YouTube URL. Please enter a valid video link.")
    return None


# function to get transcript from the video.
def get_transcript(video_id, language):
    ytt_api = YouTubeTranscriptApi()
    try:
        transcript = ytt_api.fetch(video_id, languages=[language])
        full_transcript = " ".join([i.text for i in transcript])
        time.sleep(10)
        return full_transcript
    except Exception as e:
        st.error(f"Error fething video {e}")


# initialize gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.2
)


# translation
def translate_transcript(transcript):
    try:
        prompt = ChatPromptTemplate.from_template("""
        You are an expert translator...
        
        Transcript:
        {transcript}
        """)

        chain = prompt | llm
        response = chain.invoke({"transcript": transcript})
        return response.content
    except Exception as e:
        st.error(f"Error fething video {e}")


# important topics
def get_important_topics(transcript):
    try:
        prompt = ChatPromptTemplate.from_template("""
        Extract 5 important topics...

        Transcript:
        {transcript}
        """)

        chain = prompt | llm
        response = chain.invoke({"transcript": transcript})
        return response.content

    except Exception as e:
        st.error(f"Error fething video {e}")


# notes
def generate_notes(transcript):
    try:
        prompt = ChatPromptTemplate.from_template("""
        You are an AI note-taker...

        Transcript:
        {transcript}
        """)

        chain = prompt | llm
        response = chain.invoke({"transcript": transcript})
        return response.content

    except Exception as e:
        st.error(f"Error fething video {e}")


# chunks
def create_chunks(transcript):
    text_splitters = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=300)
    doc = text_splitters.create_documents([transcript])
    return doc


# FREE embedding vectorstore (huggingface)
def create_vector_store(docs):
    try:
        embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        vector_store = Chroma.from_documents(
            docs,
            embedding
        )

        return vector_store
    except Exception as e:
        st.error(f"Error creating vector store: {e}")
        return None


# RAG function
def rag_answer(question, vectorstore):
    results = vectorstore.similarity_search(question, k=4)
    context_text = "\n".join([i.page_content for i in results])

    prompt = ChatPromptTemplate.from_template("""
        You are a kind assistant...

        Context:
        {context}

        Question:
        {question}

        Answer:
    """)

    chain = prompt | llm
    response = chain.invoke({"context": context_text, "question": question})

    return response.content
