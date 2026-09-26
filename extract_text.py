from pypdf import PdfReader

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    all_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            all_text += text + "\n"
    return all_text

if __name__ == "__main__":
    # Test it on one file first
    text = extract_text_from_pdf("data/microsoft_2026.pdf")
    print("Total characters extracted:", len(text))
    print("\n--- First 500 characters ---\n")
    print(text[:500])