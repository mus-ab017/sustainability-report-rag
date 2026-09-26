from extract_text import extract_text_from_pdf

text = extract_text_from_pdf("data/microsoft_2026.pdf")

for phrase in ["carbon negative", "carbon neutral", "reduction target", "net zero", "net-zero"]:
    if phrase in text.lower():
        idx = text.lower().find(phrase)
        print(f"\n--- Found '{phrase}' ---")
        print(text[max(0, idx-200):idx+200])
    else:
        print(f"\n--- '{phrase}' not found ---")