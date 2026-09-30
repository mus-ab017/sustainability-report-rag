import time
from ask import ask_question

TESTS = [
    {"q": "What is Microsoft's goal for carbon by 2030?", "type": "factual", "keywords": [["carbon negative"], ["2030"]]},
    {"q": "How much water did Google replenish in 2025?", "type": "factual", "keywords": [["7.7 billion"]]},
    {"q": "What has Apple achieved for renewable electricity in its corporate operations?", "type": "factual", "keywords": [["100 percent", "100%"]]},
    {"q": "How much net-new clean energy did Google sign agreements for in 2025?", "type": "factual", "keywords": [["12 gw", "12 gigawatt"]]},
    {"q": "What is Apple's 2030 goal?", "type": "factual", "keywords": [["carbon neutral"], ["2030"]]},
    {"q": "What is Microsoft's water goal for 2030?", "type": "factual", "keywords": [["water positive"], ["2030"]]},
    {"q": "What is Google's carbon-free energy goal?", "type": "factual", "keywords": [["24/7", "carbon-free"], ["2030"]]},
    {"q": "What does Google say about restarting the Duane Arnold Energy Center?", "type": "factual", "keywords": [["600 mw", "600 megawatt"], ["2029"]]},
    {"q": "How many megawatts of renewable energy has Apple helped create for its own facilities?", "type": "factual", "keywords": [["1,780", "1780"]]},
    {"q": "Compare the renewable energy commitments of Microsoft, Google, and Apple.", "type": "comparison", "keywords": [["microsoft"], ["google"], ["apple"]]},
    {"q": "Compare the 2030 goals of Microsoft and Apple.", "type": "comparison", "keywords": [["microsoft"], ["apple"], ["2030"]]},
    {"q": "What is Apple's stock price target for 2027?", "type": "refusal", "keywords": []},
    {"q": "What is the salary of Microsoft's CEO?", "type": "refusal", "keywords": []},
    {"q": "What single percentage emissions-reduction target does Microsoft state?", "type": "manual", "keywords": []},
    {"q": "Which company has the most ambitious sustainability goals?", "type": "manual", "keywords": []},
]

REFUSAL_PHRASES = ["not enough information", "does not contain", "no information",
                   "not mentioned", "cannot answer", "not provide"]


def grade(test, answer):
    lower = answer.lower()
    if test["type"] == "manual":
        return "REVIEW"
    if test["type"] == "refusal":
        return "PASS" if any(p in lower for p in REFUSAL_PHRASES) else "FAIL"
    ok = all(any(k in lower for k in group) for group in test["keywords"])
    return "PASS" if ok else "FAIL"


results = []
for i, test in enumerate(TESTS, 1):
    print(f"[{i}/{len(TESTS)}] {test['q']}")
    answer = ask_question(test["q"], n_results_per_company=8)
    results.append((test, answer, grade(test, answer)))
    time.sleep(5)

passed = sum(1 for _, _, g in results if g == "PASS")
failed = sum(1 for _, _, g in results if g == "FAIL")
review = sum(1 for _, _, g in results if g == "REVIEW")

with open("eval_results.md", "w", encoding="utf-8") as f:
    f.write(f"# Evaluation results\n\nPASS: {passed} | FAIL: {failed} | REVIEW: {review} | Total: {len(results)}\n\n")
    for test, answer, g in results:
        f.write(f"## [{g}] ({test['type']}) {test['q']}\n\n{answer}\n\n---\n\n")

print(f"\nPASS: {passed} | FAIL: {failed} | REVIEW: {review}")
print("Full answers saved to eval_results.md")