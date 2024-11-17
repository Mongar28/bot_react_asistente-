from langchain_chroma import Chroma
import os


def create_verctorstore(docs_split: list, embeddings, file_name: str):
    db_name: str = file_name.replace(".pdf", "").replace(" ", "_").lower()

    persist_directory: str = f"embeddings/{db_name}"

    if not os.path.exists(persist_directory):
        vectordb = Chroma.from_documents(
            persist_directory=persist_directory,
            documents=docs_split,
            embedding=embeddings,
        )
