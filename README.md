# NetSage AI — Project 2 Deliverable

AI-assisted troubleshooter for Cisco-style Packet Tracer labs. Reads
symptoms and show-command output, proposes a root cause, and requires a
human to review every diagnosis before it's trusted.

## Folder structure

```
NetSage-AI/
├── cases.csv                        # the 30-case dataset (main deliverable)
├── data/build_cases.py              # regenerates cases.csv
├── prompts/
│   └── diagnose_prompt.md           # structured prompt + 3 worked examples
├── ai_diagnosis/
│   ├── ai_diagnoses.json            # all 30 AI outputs, keyed by case_id
│   └── build_diagnoses.py           # regenerates ai_diagnoses.json
├── checker/
│   ├── rule_checker.py              # deterministic Python checker (run this)
│   └── checker_report.csv           # its output
├── review/
│   ├── human_review_log.csv         # Accepted/Edited/Rejected per case
│   ├── build_review_log.py          # regenerates the log
│   └── responsible_ai_log.md        # detailed writeup of the 6 corrected cases
├── dashboard/
│   ├── dashboard.xlsx               # summary + charts, formula-driven
│   └── build_dashboard.py           # regenerates dashboard.xlsx
└── demo/
    └── demo_script.md               # shot-by-shot script for your video
```

## How to run it yourself

```bash
cd NetSage-AI
python3 data/build_cases.py
python3 ai_diagnosis/build_diagnoses.py
python3 review/build_review_log.py
python3 checker/rule_checker.py
python3 dashboard/build_dashboard.py
```

## Key numbers (from this run)

- 30 cases, across 8 fault categories
- 24 AI diagnoses accepted, 6 rejected by human review (80% agreement)
- Deterministic checker independently flagged 4 of the 30 cases (it's
  intentionally narrow — it only catches the config mistakes the problem
  statement names explicitly: duplicate IPs, wrong masks, gateway
  mismatch, interface down, missing VLAN, missing route. The rest rely on
  AI + human judgement, which is by design, not a gap you need to fix)

