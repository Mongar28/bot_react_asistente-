from rag.split_docs import load_split_docs
from rag.llm import load_llm_openai
from rag.embeddings import load_embeddins
from rag.retriever import create_retriever
from rag.vectorstore import create_verctorstore
from rag.rag_chain import create_rag_chain

dir_pdfs: str = 'documents/pdfs/'
file_name: str = 'onecluster_info.pdf'
file_path: str = 'onecluster_info.pdf'

docs_split: list = load_split_docs(file_path)
embeddings_model = load_embeddins()
llm = load_llm_openai()
create_verctorstore(
    docs_split,
    embeddings_model,
    file_path
)
retriever = create_retriever(
    embeddings_model,
    persist_directory="embeddings/onecluster_info"
)
qa = create_rag_chain(
    llm, retriever)

prompt: str = "Dame información detallada sobre los sercivios que ofrese OneCluster."
respuesta = qa.invoke(
    {"input": prompt, "chat_history": []}
)

print(respuesta["answer"])
