import chromadb
from extract_text import extract_text_from_pdf
from chunk_text import chunk_text

collection = chromadb.PersistentClient(path="./chroma_data").get_or_create_collection("sustainability_reports")
print("Chunks saved so far:", collection.count())

total = 0
for name in ["microsoft", "google", "apple"]:
    n = len(chunk_text(extract_text_from_pdf(f"data/{name}_2026.pdf")))
    print(name, "needs", n, "chunks")
    total += n
print("Total needed:", total)