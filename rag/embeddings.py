import os



from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.loader import get_documents
from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DB_NAME,
    EMBEDING_MODEL,
    PERSIST_DIRECTORY,
    OPENAI_KEY
)


def init_vectorsotre():
    if not OPENAI_KEY:
        raise ValueError("OPENAI_API_KEY is not set. Add it to your .env file.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )

    documents, categories = get_documents()
    chunks = text_splitter.split_documents(documents)
    vectorstore = None
    embedding_model = OpenAIEmbeddings(model=EMBEDING_MODEL, api_key=OPENAI_KEY)

    if os.path.exists(PERSIST_DIRECTORY) and os.listdir(PERSIST_DIRECTORY):
       
        vectorstore = Chroma(
            collection_name=DB_NAME,
            embedding_function=embedding_model,
            persist_directory=PERSIST_DIRECTORY,
        )

    else:
      
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            collection_name=DB_NAME,
            persist_directory=PERSIST_DIRECTORY,
        )

    return vectorstore
