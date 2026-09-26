import chromadb
from sentence_transformers import SentenceTransformer

from extract_text import extract_text_from_pdf
from chunk_text import chunk_text

# --- Setup ---
print("Loading local embedding model (first time may take a minute)...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="sustainability_reports")

companies = {
    "microsoft": "data/microsoft_2026.pdf",
    "google": "data/google_2026.pdf",
    "apple": "data/apple_2026.pdf"
}

for company_name, file_path in companies.items():
    print(f"\nProcessing {company_name}...")

    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    print(f"  Created {len(chunks)} chunks")

    # Skip if already processed
    existing_ids = set(collection.get(ids=[f"{company_name}_{i}" for i in range(len(chunks))])["ids"])
    if len(existing_ids) == len(chunks):
        print(f"  Already fully processed, skipping.")
        continue

    # Generate embeddings for ALL chunks at once - fast, since it's local
    embeddings = embedder.encode(chunks, show_progress_bar=True)

    ids = [f"{company_name}_{i}" for i in range(len(chunks))]
    metadatas = [{"company": company_name}] * len(chunks)

    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=chunks,
        metadatas=metadatas
    )

    print(f"  Saved all {company_name} chunks to the database")

print("\nAll done! Database built successfully.")
