import glob
import os

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from tomlkit import document

from config import KNOWLEDGE_BASE_PATH


def clean_text(text):
    lines = text.split("\n")
    return "\n".join(" ".join(line.split()) for line in lines)


def get_documents():

    folders = glob.glob(KNOWLEDGE_BASE_PATH)

    documents = []
    categories = ["All"]

    for folder in folders:
        doc_category = os.path.basename(folder)
        categories.append(doc_category)

        loader = DirectoryLoader(
            path=folder,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )

        folder_docs = loader.load()

        for folder_doc in folder_docs:
            folder_doc.metadata["category"] = doc_category
            folder_doc.page_content = clean_text(folder_doc.page_content)
            documents.append(folder_doc)

    return documents, categories
