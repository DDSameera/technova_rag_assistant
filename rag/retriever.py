from langchain_chroma import vectorstores

from config import RETRIEVAL_K
from rag.embeddings import init_vectorsotre


def retrieve_docs(question: str, category: str | None = None, k: int = RETRIEVAL_K):

    search_kwargs = {"k": k}

    if category:
        search_kwargs["filter"] = {"category": category}

    vectorstores = init_vectorsotre()

    return vectorstores.as_retriever(
        search_type="similarity", search_kwargs=search_kwargs
    ).invoke(question)
