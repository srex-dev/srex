def retrieve_docs(query, k=3):
    try:
        from langchain_community.vectorstores import Chroma
        from .embedder import get_embedder
    except ImportError:
        raise RuntimeError("RAG dependencies missing: install `langchain-community` to use document retrieval.")

    vectordb = Chroma(persist_directory="rag/chroma_db", embedding_function=get_embedder())
    vectordb.add_texts(["SLOs should have targets like 99.9% availability..."])
    docs = vectordb.similarity_search(query, k=k)
    return [doc.page_content for doc in docs]