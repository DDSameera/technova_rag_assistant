import subprocess
import modal

app = modal.App("technova-rag-assistant")

image = (
    modal.Image.debian_slim(python_version="3.11")
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
    .env({"GRADIO_SERVER_NAME": "0.0.0.0"})
    .workdir("/app")
)

@app.function(
    image=image,
    secrets=[modal.Secret.from_name("openai-api-key")],
    timeout=600,
)
@modal.web_server(7860, startup_timeout=120)
def serve():
    subprocess.Popen(["python", "app.py"])