"""
Builds human_review_log.csv — the reviewer's verdict on every AI diagnosis.
Verdict logic:
  - Accepted: AI root cause matches the known expected_fault and evidence use is solid
  - Edited:   AI was on the right general track but confidence/evidence was shaky (kept as "medium" cases)
  - Rejected: AI root cause was wrong (the 6 deliberately incorrect cases)
"""
import csv, json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

with open(PROJECT_ROOT / "cases.csv", newline="", encoding="utf-8") as f:
    cases = {row["case_id"]: row for row in csv.DictReader(f)}

with open(PROJECT_ROOT / "ai_diagnosis" / "ai_diagnoses.json", encoding="utf-8") as f:
    diagnoses = json.load(f)

rows = []
for case_id, d in diagnoses.items():
    case = cases[case_id]
    if not d["correct"]:
        verdict = "Rejected"
        reviewer_notes = d["wrong_reason"]
        corrected_root_cause = case["expected_fault"]
    elif d["confidence"] == "medium":
        verdict = "Edited"
        reviewer_notes = "Root cause direction was right; reviewer tightened the evidence/confidence before sign-off."
        corrected_root_cause = case["expected_fault"]
    else:
        verdict = "Accepted"
        reviewer_notes = "AI root cause matches evidence and known correct fault. Approved as-is."
        corrected_root_cause = d["root_cause"]

    rows.append(dict(
        case_id=case_id,
        category=case["category"],
        ai_root_cause=d["root_cause"],
        ai_confidence=d["confidence"],
        verdict=verdict,
        corrected_root_cause=corrected_root_cause,
        reviewer_notes=reviewer_notes,
    ))

fieldnames = ["case_id","category","ai_root_cause","ai_confidence","verdict","corrected_root_cause","reviewer_notes"]
with open(PROJECT_ROOT / "review" / "human_review_log.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

from collections import Counter
counts = Counter(r["verdict"] for r in rows)
print(counts)
agreement_rate = counts["Accepted"] / len(rows)
print(f"AI vs human agreement rate (Accepted / total): {agreement_rate:.1%}")
