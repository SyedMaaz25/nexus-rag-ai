from services.loader import load_pdf
from services.chunker import split_documents
from services.vectorstore import upsert_documents

def ingest_pdf(file_path):
    print("Loading PDF...")
    docs = load_pdf(file_path)

    print("Chunking...")
    chunks = split_documents(docs)

    print(f"Total chunks: {len(chunks)}")

    print("Upserting to Pinecone...")
    count = upsert_documents(chunks)

    print(f"Stored {count} vectors in Pinecone")

if __name__ == "__main__":
    ingest_pdf("data/linkedin.pdf")