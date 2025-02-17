import asyncio
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

async def search_faq(query: str, k: int = 5, threshold: float = 85):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", chunk_size=1000, dimensions=1536)

    vector_store = Chroma(
        collection_name="wise_faq",
        embedding_function=embeddings,
        persist_directory="./wise_faq_db"
    )

    results = await asyncio.to_thread(vector_store.similarity_search_with_score, query, k)

    document = ""
    for res, score in results:
        score *= 100
        if score < threshold:
            print(f"{score} * {res.page_content} [{res.metadata}] [{res.id}]")
            document += res.page_content + " "

    return {"document": str(document)}