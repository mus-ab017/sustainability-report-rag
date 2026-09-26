from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ask import ask_question
from specificity_scorer import score_text_specificity
from extract_text import extract_text_from_pdf

app = FastAPI(title="Sustainability Report RAG API")

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


@app.get("/specificity")
def specificity():
    companies = {
        "microsoft": "data/microsoft_2026.pdf",
        "google": "data/google_2026.pdf",
        "apple": "data/apple_2026.pdf"
    }

    results = {}
    for company, path in companies.items():
        text = extract_text_from_pdf(path)
        results[company] = score_text_specificity(text)

    return results


@app.get("/")
def health_check():
    return {"status": "API is running"}