from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from services.embeddings import get_embeddings
from config import PINECONE_API_KEY, PINECONE_INDEX

pc = Pinecone(api_key=PINECONE_API_KEY)

def get_vectorstore():
    embeddings = get_embeddings()
    
    # Ensure index exists
    if PINECONE_INDEX not in pc.list_indexes().names():
        pc.create_index(
            name=PINECONE_INDEX,
            dimension=1536, 
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    
    return PineconeVectorStore(
        index_name=PINECONE_INDEX, 
        embedding=embeddings,
        pinecone_api_key=PINECONE_API_KEY
    )

def upsert_documents(chunks, ):
    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
    return len(chunks)

def search_documents(query, top_k=5):
    vectorstore = get_vectorstore()
    docs =vectorstore.max_marginal_relevance_search(
        query,
        k=top_k,        
        fetch_k=20,     
        lambda_mult=0.6
    )
    return [d.page_content for d in docs]