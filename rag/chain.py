from langchain_openai import ChatOpenAI

from config import MODEL, RELEVANCE_THRESHOLD, RETRIEVAL_K
from prompts import SYSTEM_PROMPT
from rag.embeddings import init_vectorsotre
from rag.retriever import retrieve_docs
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

vectorstores = init_vectorsotre()


def clean_source_path(path: str) -> str:
    return (
        path.replace("../knowledge-base/", "")
        .replace("knowledge-base/", "")
        .replace("../", "")
    )


def answer_question(question: str, history=None, category=None):

    if history is None:
        history = []

    # STEP 1: decide docs only
    if len(question.strip().split()) >= 3:
        # Generic off-topic detection using similarity score
        docs_with_score = vectorstores.similarity_search_with_score(
            question, k=RETRIEVAL_K
        )
        best_score = docs_with_score[0][1] if docs_with_score else 999
        print(f"docs with score : {docs_with_score}")
        print(f"Best simialiry score : {best_score}")

        if best_score > RELEVANCE_THRESHOLD:
            return "I don't have enough information to answer that question."

        if category is None or category == "" or category == "All":
            docs = [doc for doc, score in docs_with_score]
        else:
            docs = retrieve_docs(question, category)
    else:
        docs = []

        print(f"docs : {docs}")

    # STEP 2: LLM call — runs for BOTH branches
    context = "\n\n".join(
        f"Source: {doc.metadata.get('source')}\n"
        f"Category: {doc.metadata.get('category')}\n"
        f"Content: {doc.page_content}"
        for doc in docs
    )

    system_prompt = SYSTEM_PROMPT.format(context=context)

    messages = [
        SystemMessage(content=system_prompt),
    ]

    print(history)

    for h in history:
        if h["role"] == "user":
            messages.append(HumanMessage(content=h["content"]))
        elif h["role"] == "assistant":
            messages.append(AIMessage(content=h["content"]))

    messages.append(HumanMessage(content=question))

    llm = ChatOpenAI(model=MODEL, temperature=0)
    response = llm.invoke(messages)
    answer = response.content

    print(answer)
    if "[NO_SOURCES]" in answer:
        answer = answer.replace("[NO_SOURCES]", "").strip()

    if answer == "I don't have enough information to answer that question.":
        return answer

    # In answer_question:
    seen = dict.fromkeys(
        clean_source_path(doc.metadata.get("source", ""))
        for doc in docs
        if doc.metadata.get("source")
    )
    top_sources = list(seen.keys())[:3]
    sources_text = "\n".join(f"- {src}" for src in top_sources)

    if(sources_text):
        return f"{answer}\n\nSources:\n{sources_text}"
    return f"{answer}"
