import re
from extract_text import extract_text_from_pdf

text = extract_text_from_pdf("data/microsoft_2026.pdf")

matches = list(re.finditer(r'(carbon|emissions?)[^.]{0,100}\d+%', text, re.IGNORECASE))

if matches:
    print(f"Found {len(matches)} potential matches:\n")
    for m in matches:
        print(m.group())
        print("---")
else:
    print("No sentences found combining 'carbon'/'emissions' with a specific percentage.")