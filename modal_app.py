import modal

app = modal.App("technova-rag-assistant")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libsqlite3-dev")
    .pip_install_from_pyproject("pyproject.toml")
    .add_local_dir(
        ".",
        remote_path="/app",
        copy=True,
        ignore=[
            ".git/**",
            ".venv/**",
            "__pycache__/**",
            ".env",
            ".DS_Store",
            ".vscode/**",
        ],
    )
    .workdir("/app")
)


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("openai-api-key")],
    timeout=600,
)
@modal.asgi_app()
def serve():
    import gradio as gr
    from fastapi import FastAPI
    from rag.chain import answer_question
    from rag.loader import get_documents

    _, categories = get_documents()
    select_categories = gr.Dropdown(categories, label="Select Category")

    demo = gr.ChatInterface(
        fn=answer_question,
        title="TechNova RAG Assistant",
        additional_inputs=select_categories,
    )

    fastapi_app = FastAPI()
    return gr.mount_gradio_app(fastapi_app, demo, path="/")
