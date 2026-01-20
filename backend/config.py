"""
Configuration settings for the Drug Information Chatbot
"""
import os

# LM Studio Configuration
LM_STUDIO_BASE_URL = "http://127.0.0.1:1234/v1"
LM_STUDIO_MODEL = "mistral-7b-instruct-v0.2"  # Must match model ID from LM Studio

# LLM Parameters
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 512
LLM_TOP_P = 0.9

# Embedding Model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Chunking Parameters
CHUNK_SIZE = 600  # tokens (roughly 400-700 words)
CHUNK_OVERLAP = 100  # tokens

# Retrieval Parameters
TOP_K_CHUNKS = 5
SIMILARITY_THRESHOLD = 0.3

# Memory Settings
MAX_HISTORY_MESSAGES = 5

# File Paths
UPLOAD_DIR = "uploads"
VECTOR_STORE_DIR = "vector_stores"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
