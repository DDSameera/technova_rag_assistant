import os

from dotenv import load_dotenv
load_dotenv(override=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIRECTORY = os.path.join(BASE_DIR, "vector_db")
KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "knowledge-base", "*")
QUESTION_FILE_PATH = os.path.join(BASE_DIR, "evaluation/questions.json")
EVAL_RESULT_FILE_PATH = os.path.join(BASE_DIR, "evaluation/eval_results.json")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")


MODEL = "gpt-4.1-nano"
EMBEDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
RETRIEVAL_K = 13
RELEVANCE_THRESHOLD = 3
DB_NAME = "vector_db"
