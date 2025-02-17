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
            # print(type(res.page_content))
            document += res.page_content + " "

    # print(type(document))
    # return document
    return {"document": str(document)}

# Example usage:
# asyncio.run(search_faq("What information or documentation is required if my bank is located in Australia or New Zealand?"))
# asyncio.run(search_faq("I have an issue with the payment. It says that my transfer is complete but my money has not been received."))
# print("--------------------------------------------------------------")
# asyncio.run(search_faq("When will my money arrive?"))
# asyncio.run(search_faq("I transferred money but my recipient says the money hasn’t arrived yet"))
# asyncio.run(search_faq("My recipient says the money hasn’t arrived yet"))
# asyncio.run(search_faq("What is a proof of payment?"))
# print("--------------------------------------------------------------")
# asyncio.run(search_faq("What information is requiredd if my bank is located in Australia?"))
# print("--------------------------------------------------------------")
# asyncio.run(search_faq("My bank is located in Australia do I need to give any extra Information?"))