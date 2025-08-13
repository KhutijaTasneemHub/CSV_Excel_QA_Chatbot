import pandas as pd
import streamlit as st

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.embeddings import OpenAIEmbeddings

from langchain_community.vectorstores import FAISS

from langchain.chains.question_answering import load_qa_chain

from langchain_community.chat_models import ChatOpenAI

# OpenAI API key set up -
import os
from dotenv import load_dotenv

load_dotenv()  # this loads environment variables from .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("API key not found. Please set it in .env file.")

# Replace with your OpenAI API key
# OPENAI_API_KEY = "actual value is stored in .env file"

st.header("CSV_Excel_QA_Chatbot") # Title shown on the app page

# Upload CSV or Excel file
file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if file is not None:
    # Check if the uploaded file is CSV or Excel
    if file.name.endswith(".csv"):  # Read CSV file into a pandas dataframe
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)  # Read Excel file into a pandas dataframe

    # Show the first 5 rows of the data
    # st.write("Here is a preview of your data:")
    # st.dataframe(df.head())

    data_text = df.to_string(index=False)

    # st.write("Here is your data in text format:")
    # st.text(data_text)

    # Create the text splitter instance
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n"],  # Split by new lines
        chunk_size=500,  # Max size of each chunk
        chunk_overlap=50,  # Overlap for context between chunks
        length_function=len
    )

    # Split the data_text into chunks
    chunks = text_splitter.split_text(data_text)

    # st.write(f"Data has been split into {len(chunks)} chunks for processing.")

    # Create OpenAI embeddings
    embeddings = OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY)

    # Store chunks in FAISS vector database
    vector_store = FAISS.from_texts(chunks, embeddings)

    # st.success("✅ Data has been embedded and stored in the vector database.")

    # Ask user for a question
    user_question = st.text_input("Ask a question about your data:")
    if user_question:
        # Search for similar chunks in the vector store
        similar_docs = vector_store.similarity_search(user_question)

        # Load the OpenAI chat model for generating answers
        llm = ChatOpenAI(
            openai_api_key= OPENAI_API_KEY,
            temperature=0,
            model_name="gpt-3.5-turbo"
        )

        # Load a question-answering chain
        chain = load_qa_chain(llm, chain_type="stuff")

        # Generate an answer using the retrieved similar chunks
        answer = chain.run(input_documents=similar_docs, question=user_question)

        # Show the answer to the user
        st.write("### Answer:")
        st.write(answer)
