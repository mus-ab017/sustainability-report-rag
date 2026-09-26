import re

CLAIM_INDICATORS = [
    "goal", "target", "commit", "committed", "commitment", "pledge",
    "aim to", "aims to", "will", "by 2025", "by 2026", "by 2027",
    "by 2028", "by 2029", "by 2030", "by 2040", "by 2050", "plan to",
    "working to", "strive", "striving"
]

VAGUE_PHRASES = [
    "committed to", "deeply committed", "remain committed",
    "our commitment to", "leading", "innovative", "striving",
    "dedicated to", "passionate about", "we believe", "our vision",
    "world-class", "cutting-edge", "best-in-class", "pioneering",
    "championing", "playing our part", "doing our part", "champion"
]


def clean_text(text):
    """Remove common PDF extraction artifacts before splitting into sentences."""
    text = re.sub(r'-\n', '', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.replace('ʼ', "'").replace('’', "'")

    # Remove footnote numbers stuck right after a period (e.g. "energy.2 Microsoft" -> "energy. Microsoft")
    text = re.sub(r'\.(\d{1,2})(\s)', r'.\2', text)

    return text


def strip_leading_footnote_number(sentence):
    """Remove a small leading number (likely a footnote marker), but never touch a real 4-digit year."""
    return re.sub(r'^\d{1,2}\s+(?=[A-Z])', '', sentence)


def has_long_capitalized_run(sentence, min_run=4):
    """Detect an unbroken run of consecutive Capitalized Words - a strong sign of header/nav/TOC text."""
    words = sentence.split()
    run = 0
    for w in words:
        if w[:1].isupper() and w.lower() not in {"i"}:
            run += 1
            if run >= min_run:
                return True
        else:
            run = 0
    return False


def looks_like_header_or_toc(sentence):
    """Detect table-of-contents / header noise."""
    words = sentence.split()
    if len(words) < 5:
        return False

    capitalized = sum(1 for w in words if w[:1].isupper())
    ratio = capitalized / len(words)
    standalone_numbers = sum(1 for w in words if re.fullmatch(r'\d{1,3}', w))

    return ratio > 0.4 or standalone_numbers >= 3 or has_long_capitalized_run(sentence)


def is_claim_sentence(sentence):
    """A sentence only counts as a 'claim' if it uses goal/commitment-type language."""
    lower = sentence.lower()
    return any(indicator in lower for indicator in CLAIM_INDICATORS)


def has_specific_signal(sentence):
    if re.search(r'\d+%', sentence):
        return True
    if re.search(r'\b(19|20)\d{2}\b', sentence):
        return True
    if re.search(r'\d+\s?(gigawatt|megawatt|gallon|ton|tonne|liter|billion|million)', sentence, re.IGNORECASE):
        return True
    return False


def has_vague_language(sentence):
    lower = sentence.lower()
    return any(phrase in lower for phrase in VAGUE_PHRASES)


def score_text_specificity(text):
    text = clean_text(text)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    results = {"specific": [], "vague": []}

    for sentence in sentences:
        sentence = strip_leading_footnote_number(sentence.strip())

        if len(sentence) < 20:
            continue
        if looks_like_header_or_toc(sentence):
            continue
        if not is_claim_sentence(sentence):
            continue

        if has_specific_signal(sentence):
            results["specific"].append(sentence)
        elif has_vague_language(sentence):
            results["vague"].append(sentence)
        # A claim sentence with neither signal is rare but possible - we just don't count it

    total = len(results["specific"]) + len(results["vague"])
    specificity_score = len(results["specific"]) / total if total > 0 else 0

    return {
        "specificity_score": round(specificity_score, 2),
        "specific_count": len(results["specific"]),
        "vague_count": len(results["vague"]),
        "total_claims_analyzed": total,
        "vague_examples": results["vague"][:5],
        "specific_examples": results["specific"][:5]
    }


if __name__ == "__main__":
    from extract_text import extract_text_from_pdf

    for company, path in [
        ("microsoft", "data/microsoft_2026.pdf"),
        ("google", "data/google_2026.pdf"),
        ("apple", "data/apple_2026.pdf")
    ]:
        text = extract_text_from_pdf(path)
        result = score_text_specificity(text)
        print(f"\n{'='*80}\n{company.upper()}\n{'='*80}")
        print(f"Specificity score: {result['specificity_score']} "
              f"({result['specific_count']} specific / {result['vague_count']} vague "
              f"out of {result['total_claims_analyzed']} claim-like sentences)")
        print("\nExample vague claims:")
        for v in result['vague_examples']:
            print(" -", v[:150])
        print("\nExample specific claims:")
        for s in result['specific_examples']:
            print(" -", s[:150])