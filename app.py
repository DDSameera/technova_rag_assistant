import gradio as gr

from rag.chain import answer_question
from rag.loader import get_documents


def load_gradio_ui():

    documents, categories = get_documents()

    select_categories = gr.Dropdown(
        categories,
        label="Select Category",
    )
    gr.ChatInterface(
        fn=answer_question,
        title="TechNova RAG Assistant",
        additional_inputs=select_categories,
    ).queue().launch(server_port=7860, server_name="0.0.0.0")


if __name__ == "__main__":
    load_gradio_ui()
