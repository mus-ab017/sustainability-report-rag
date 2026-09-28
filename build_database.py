import os
import time
from dotenv import load_dotenv
from google import genai
import chromadb

from extract_text import extract_text_from_pdf
from chunk_text import chunk_text

load_dotenv()
api_key = os.getenv("sustainability_rag")
client = genai.Client(api_key=api_key)

chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="sustainability_reports")

companies = {
    "microsoft": "data/microsoft_2026.pdf",
    "google": "data/google_2026.pdf",
    "apple": "data/apple_2026.pdf"
}

BATCH_SIZE = 20


def embed_with_retry(batch_chunks, max_retries=5):
    """Embed a batch. Retries short rate limits, but stops cleanly on the daily quota."""
    for attempt in range(max_retries):
        try:
            return client.models.embed_content(
                model="gemini-embedding-001",
                contents=batch_chunks
            )
        except Exception as e:
            message = str(e)
            if "PerDay" in message:
                print(f"\nDaily quota reached. Chunks saved so far: {collection.count()}")
                print("Run this script again after the quota resets. It will resume where it stopped.")
                raise SystemExit(0)
            if "429" in message and attempt < max_retries - 1:
                wait = 30 * (attempt + 1)
                print(f"  Rate limit hit, waiting {wait}s before retrying...")
                time.sleep(wait)
            else:
                raise


for company_name, file_path in companies.items():
    print(f"\nProcessing {company_name}...")

    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    print(f"  Created {len(chunks)} chunks")

    existing_ids = set(collection.get(ids=[f"{company_name}_{i}" for i in range(len(chunks))])["ids"])

    for batch_start in range(0, len(chunks), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(chunks))
        batch_ids = [f"{company_name}_{i}" for i in range(batch_start, batch_end)]

        if all(bid in existing_ids for bid in batch_ids):
            continue

        batch_chunks = chunks[batch_start:batch_end]

        result = embed_with_retry(batch_chunks)
        embeddings = [e.values for e in result.embeddings]

        collection.add(
            ids=batch_ids,
            embeddings=embeddings,
            documents=batch_chunks,
            metadatas=[{"company": company_name}] * len(batch_chunks)
        )
        print(f"  Saved chunks {batch_start}-{batch_end-1}")
        time.sleep(2)

    print(f"  Finished {company_name}")

print("\nAll done! Database built successfully.")
print("Total chunks saved:", collection.count())