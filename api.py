from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os

from ask import ask_question
from specificity_scorer import score_text_specificity
from extract_text import extract_text_from_pdf

app = FastAPI(title="Sustainability Report RAG API")
if not os.path.exists("./chroma_data"):
    print("No existing database found — building it now (this may take a minute)...")
    import build_database

# Allow our frontend (running separately) to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask(payload: Question):
    answer = ask_question(payload.question, n_results_per_company=8)
    return {"answer": answer}


_specificity_cache = None

@app.get("/specificity")
def specificity():
    global _specificity_cache
    if _specificity_cache is not None:
        return _specificity_cache

    companies = {
        "microsoft": "data/microsoft_2026.pdf",
        "google": "data/google_2026.pdf",
        "apple": "data/apple_2026.pdf"
    }

    results = {}
    for company, path in companies.items():
        text = extract_text_from_pdf(path)
        results[company] = score_text_specificity(text)

    _specificity_cache = results
    return results


@app.get("/")
def health_check():
    return {"status": "API is running"}

@app.get("/app")
def serve_frontend():
    return FileResponse("frontend.html")