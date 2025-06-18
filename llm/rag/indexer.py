from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from .embedder import get_embedder

def build_vector_store():
    loader = DirectoryLoader("rag/base_docs", glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = splitter.split_documents(documents)
    vectordb = Chroma.from_documents(texts, get_embedder(), persist_directory="rag/chroma_db")
    vectordb.persist()
    print("✅ Vector store built and persisted.")
