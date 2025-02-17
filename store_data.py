import asyncio
import os
import re
import uuid
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Define function to clean extracted text
def clean_text(text):
    text = re.sub(r'<[^>]*>', '', text)  # Remove HTML tags
    text = re.sub(r'#+\s', '', text)  # Headers
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # Images
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)  # Bold, italics
    text = re.sub(r'http\S+|www\.\S+', '', text)  # Remove URLs
    return re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace

# Function to extract concern from URL
def extract_concern_from_url(url):
    concern = url.rstrip("/").split("/")[-1]  # Get the last part of the URL
    return concern.replace("-", " ").capitalize()  # Replace hyphens with spaces and capitalize

# Function to save text embeddings to ChromaDB
def save_to_chroma(chunks, vector_store, concern):
    embeddings_model = OpenAIEmbeddings()
    
    for chunk in chunks:
        doc_id = str(uuid.uuid4())  # Unique ID for each chunk
        metadata = {
            "source": concern,
        }

        embedding = embeddings_model.embed_documents([chunk])  # Generate embeddings
        vector_store.add_texts([chunk], ids=[doc_id], metadatas=[metadata], embeddings=embedding)

# Function to split text into smaller chunks
def split_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", ".", "?", "!"]
    )
    return text_splitter.split_text(text)

async def main():
    browser_config = BrowserConfig()
    run_config = CrawlerRunConfig()

    async with AsyncWebCrawler(config=browser_config) as crawler:
        urls = [
            "https://wise.com/help/articles/2452305/how-can-i-check-the-status-of-my-transfer",
            "https://wise.com/help/articles/2941900/when-will-my-money-arrive",
            "https://wise.com/help/articles/2977950/why-does-it-say-my-transfers-complete-when-the-money-hasnt-arrived-yet",
            "https://wise.com/help/articles/2977951/why-do-some-transfers-take-longer",
            "https://wise.com/help/articles/2932689/what-is-a-proof-of-payment",
            "https://wise.com/help/articles/2977938/whats-a-banking-partner-reference-number"
        ]

        vector_store = Chroma(
            collection_name="wise_faq",
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-small", chunk_size=1000, dimensions=1536),
            persist_directory="./wise_faq_db"
        )

        for url in urls:
            print(f"Crawling: {url}")
            result = await crawler.arun(url=url, config=run_config)
            
            if not result.markdown:
                print(f"Failed to extract content from {url}")
                continue

            cleaned_text = clean_text(result.markdown)
            # cleaned_text = extract_info(cleaned_text)

            # Extract concern from URL
            concern = extract_concern_from_url(url)

            # Split text into chunks
            text_chunks = split_text(cleaned_text)

            print(f"Extracted {len(text_chunks)} chunks from {concern}")

            # Save chunks with metadata (concern) to vector store
            save_to_chroma(text_chunks, vector_store, concern)

if __name__ == "__main__":
    asyncio.run(main())
