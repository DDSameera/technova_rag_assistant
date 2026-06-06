import json

from langchain_openai import ChatOpenAI
from config import (
    EVAL_RESULT_FILE_PATH,
    MODEL,
    QUESTION_FILE_PATH,
    RELEVANCE_THRESHOLD,
    RETRIEVAL_K,
)
from prompts import JUDGE_SYSTEM_PROMPT, SYSTEM_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from rag.chain import clean_source_path
from rag.embeddings import init_vectorsotre
from rag.retriever import retrieve_docs

vectorstores = init_vectorsotre()


def llm_judge(
    question: str,
    answer: str,
    must_mention: list[str],
    expected_sources,
    actual_sources,
):

    must_mention_text = ", ".join(must_mention)
    actual_sources_list = ", ".join(actual_sources)
    expected_sources_list = ", ".join(expected_sources)

    user_prompt = f"""
        Question: {question}

        Required facts (must be present, can be paraphrased):
        {must_mention_text}
        
        Expected Sources
        {expected_sources_list}
        
        Actual Sources
        { actual_sources_list }

        Assistant's answer:
        {answer}

        Score according to the rubric. Return JSON only.
    """

    messages = [
        SystemMessage(content=JUDGE_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    llm = ChatOpenAI(model=MODEL, temperature=0)
    response = llm.invoke(messages)

    # Parse JSON – handle possible markdown wrapping
    content = response.content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.endswith("```"):
        content = content[:-3]

    try:
        result = json.loads(content)
    except:
        # Fallback
        result = {
            "score": 0,
            "reason": "Failed to parse judge output",
            "missing_facts": must_mention,
        }
    return result


def evaluate_answer():
    with open(QUESTION_FILE_PATH, "r", encoding="utf-8") as f:
        evaluation_data = json.load(f)
        questions = evaluation_data["questions"]

    results = []

    total_question = len(questions)
    retrieval_hits = 0

    out_of_scope_total = 0
    out_of_scope_refused = 0
    total_score = 0

    for q in questions:

        id = q["id"]
        question = q["question"]
        must_mention = q["must_mention"]
        expected_sources = q["expected_sources"]

        answer, actual_sources = answer_question_for_eval(
            question=question, history=None, category=None
        )

        print(actual_sources)
        # raise SystemExit

        is_out_of_scope = len(expected_sources) == 0
        if is_out_of_scope:
            out_of_scope_total += 1
            if "I don't have enough information to answer that question" in answer:
                out_of_scope_refused += 1

        if any(actual.endswith(expected) for expected in expected_sources for actual in actual_sources):
            retrieval_hits += 1

        # Judge it
        judgement = llm_judge(
            question, answer, must_mention, expected_sources, actual_sources
        )
        score = judgement["score"]
        total_score += score

        print(f"retrieveal_hits : {retrieval_hits}")
        results.append(
            {
                "id": id,
                "question": question,
                "predicted_answer": answer,
                "retrieved_sources": actual_sources,
                "score": score,
            }
        )

    refused_correctly = (
        out_of_scope_refused == out_of_scope_total if out_of_scope_total > 0 else False
    )

    average_score = round(total_score / total_question, 2)
    retrieval_precision = round(retrieval_hits / total_question, 3)
    output = {
        "summary": {
            "total_questions": total_question,
            "retrieval_precision": retrieval_precision,
            "answer_score_avg": average_score,
            "refused_correctly": refused_correctly,
        },
        "per_question": results,
    }

    with open(EVAL_RESULT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    return output


def answer_question_for_eval(question: str, history=None, category=None):

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
            return ("I don't have enough information to answer that question.", [])

        if category is None or category == "" or category == "All":
            docs = [doc for doc, score in docs_with_score]
        else:
            docs = retrieve_docs(question, category)
    else:
        docs = retrieve_docs(question)

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
        return answer, []

    # In answer_question:
    seen = dict.fromkeys(
        clean_source_path(doc.metadata.get("source", ""))
        for doc in docs
        if doc.metadata.get("source")
    )
    actual_sources = list(seen.keys())[:3]

    return answer, actual_sources


if __name__ == "__main__":
    evaluate_answer()
