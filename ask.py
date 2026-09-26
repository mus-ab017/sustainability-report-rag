import os
from dotenv import load_dotenv
from google import genai
import chromadb
from sentence_transformers import SentenceTransformer

# --- Setup ---
load_dotenv()
api_key = os.getenv("sustainability_rag")
client = genai.Client(api_key=api_key)

embedder = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="sustainability_reports")


def ask_question(question, n_results_per_company=8):
    companies = ["microsoft", "google", "apple"]
    question_embedding = embedder.encode([question]).tolist()

    all_chunks = []
    all_sources = []

    # Retrieve separately from each company, so no one gets crowded out
    for company in companies:
        results = collection.query(
            query_embeddings=question_embedding,
            n_results=n_results_per_company,
            where={"company": company}
        )
        all_chunks.extend(results["documents"][0])
        all_sources.extend(results["metadatas"][0])

    # Build context from the combined, balanced results
    context = "\n\n---\n\n".join(
        f"[Source: {src['company']}]\n{chunk}"
        for chunk, src in zip(all_chunks, all_sources)
    )

    prompt = f"""You are a helpful assistant answering questions about corporate sustainability reports.
Use ONLY the information in the context below to answer the question.
If the context doesn't contain enough information to answer, say so clearly instead of guessing.
Always mention which company(s) your answer is based on.

Context:
{context}

Question: {question}

Answer:"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


# --- Test it ---
if __name__ == "__main__":
    test_questions = [
        "What is Microsoft's carbon reduction target?",
        "Compare the renewable energy commitments of Microsoft, Google, and Apple.",
        "How much water did Google replenish in 2025?",
        "What is Apple's stock price target for 2027?",  # intentionally irrelevant/out-of-scope
    ]

    for question in test_questions:
        answer = ask_question(question, n_results_per_company=8)
        print("=" * 80)
        print("Question:", question)
        print("\nAnswer:\n", answer)
        print()