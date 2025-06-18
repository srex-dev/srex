from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embedder():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
