# Sustainability Report Intelligence

A Retrieval-Augmented Generation (RAG) system for analyzing corporate sustainability reports — with a custom-built feature that measures how specific vs. vague each company's sustainability claims actually are.

## The problem

Corporate sustainability reports are long, dense, and often mix genuinely quantified commitments ("reduce emissions by 30% by 2030") with vague marketing language ("we are committed to leading the way in sustainability"). This project makes these reports queryable via natural language, and automatically flags which claims are backed by real numbers versus general commitment language.

## What it does

- **Ask questions** across multiple companies' sustainability reports and get grounded, cited answers (not hallucinated ones)
- **Compare companies** on specific metrics (renewable energy, water usage, carbon targets)
- **Claim Specificity Dashboard** — a custom-built analytical feature that scores each company's sustainability claims on how specific/quantified they are, with supporting example sentences

Built and tested on Microsoft, Google, and Apple's 2026 Environmental/Sustainability reports.

## Key finding

Using a rule-based claim-specificity scorer built for this project, Microsoft (80%) and Apple (75%) show notably higher rates of quantified sustainability claims compared to Google (56%) — driven largely by AI-growth-related sustainability messaging that leans on general commitment language rather than measurable targets.

## Tech stack

- **Backend:** Python, FastAPI
- **LLM:** Google Gemini (gemini-3.5-flash-lite for generation, gemini-embedding-001 for embeddings)
- **Vector database:** ChromaDB
- **PDF processing:** pypdf
- **Frontend:** Vanilla HTML/CSS/JavaScript (no framework)

## How it works

1. **Extraction & chunking:** Each PDF report is parsed and split into overlapping ~500-character chunks
2. **Embedding & storage:** Each chunk is converted into a vector embedding and stored in a local ChromaDB vector database
3. **Retrieval:** When a question is asked, it's embedded and matched against the closest chunks — retrieved **separately per company** to prevent one company's content from crowding out another's in comparison questions
4. **Generation:** Retrieved chunks + the question are sent to Gemini, which is explicitly instructed to answer only from the provided context and to say so if the context is insufficient
5. **Specificity scoring:** A separate, rule-based pipeline scans each report for claim-like sentences and classifies them as specific (contains a number/date/unit) or vague (aspirational language with no backing figure)

## Setup

```bash
git clone https://github.com/mus-ab017/sustainability-report-rag.git
cd sustainability-report-rag
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with your own Gemini API key (this is a template for other users — it does not affect your own existing `.env` file):
sustainability_rag=your_api_key_here


Build the vector database (one-time step):
```bash
python build_database.py
```

Run the app:
```bash
uvicorn api:app --reload
```

Visit `http://127.0.0.1:8000/app`

## Known limitations

- Text extraction does not capture data presented only in charts/images — only prose-based figures are captured
- Retrieval quality depends on chunk boundaries and exact query phrasing; not every specific figure is guaranteed to surface for every question
- The specificity scorer identifies *whether a claim contains a number*, not whether that number represents a genuine, ambitious commitment — a reported statistic and an actual pledge are treated the same way
- Free-tier API rate limits constrain how quickly the database can be (re)built from scratch

## Future improvements

- Vision-model-based extraction of data from charts and infographics
- Fine-tuned classifier to distinguish genuine commitments from reported statistics
- Extending the pipeline to other industries (already designed to be industry-agnostic — only the source PDFs and a few keyword lists would need to change)