import os
from pathlib import Path

#FOLDER PATHS
DATA_FOLDER='data'
LOGS_FOLDER='logs'
VECTOR_DB_PATH='chroma_db'

#AI MODEL SETTINGS

AI_MODEL='neural-chat'
EMBEDDING_MODEL="nomic-embed-text"


#DOCUMENT PROCESSING SETTINGS
CHUNK_SIZE=1500
CHUNK_OVERLAP=150
NUM_SEARCH_RESULTS=3

#WEB SERVER SETTINGS

SERVER_HOST='0.0.0.0'
SERVER_PORT=8000

#CREATE FOLDERS IF THEY DON'T EXIST

for folder in [DATA_FOLDER, LOGS_FOLDER]:
    folder_path = Path(folder)
    if folder_path.exists():
        print(f"{folder} already exists.")
    else:
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"Created folder: {folder}")