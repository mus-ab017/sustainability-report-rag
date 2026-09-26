from extract_text import extract_text_from_pdf

def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # move forward, but overlap a bit
    return chunks

# Test it
text = extract_text_from_pdf("data/microsoft_2026.pdf")
chunks = chunk_text(text)

print("Original text length:", len(text))

print("Total chunks created:", len(chunks))
print("\n--- First chunk ---\n")
print(chunks[0])
print("\n--- Second chunk (notice the overlap with the end of the first) ---\n")
print(chunks[1])