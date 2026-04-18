from openai import OpenAI
from config import OPENAI_API_KEY
from services.vectorstore import search_documents

client = OpenAI(api_key=OPENAI_API_KEY)

def chat_with_rag(query,):
    context_chunks = search_documents(query)
    context = "\n\n".join(context_chunks)

    # In chat.py
    messages = [
    {
        "role": "system", 
        "content": ("You are a professional assistant. "
                    "When providing lists, use Markdown formatting (e.g., 1., 2. or *, -) "
                    "and ensure each point is on a new line."
                    )
    },
    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
]

    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=messages,
        temperature=0.1 
    )

    return response.choices[0].message.content