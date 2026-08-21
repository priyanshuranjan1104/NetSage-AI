# NetSage AI

> AI-assisted network fault diagnosis for Cisco Packet Tracer labs.

NetSage AI combines **AI-assisted diagnosis**, a **deterministic rule-based checker**, and **human review** to identify and validate common network configuration faults.

It covers:

* VLAN
* Gateway
* DHCP
* DNS
* Routing
* ACL
* NAT
* Wireless

---

## Features

* **30 network fault cases** with symptoms, topology information, CLI evidence, and ground-truth root causes.
* **Structured AI prompt** that produces consistent JSON diagnoses.
* **Deterministic Python checker** for independently detecting known configuration problems.
* **Human-in-the-loop review** with 24 accepted and 6 rejected AI diagnoses.
* **Responsible AI log** documenting rejected diagnoses and AI mistakes.
* **Excel dashboard** containing summaries, formulas, and charts.

---

## How It Works

```text
Cisco Packet Tracer
        │
        ▼
 Run show commands
        │
        ▼
 Collect network evidence
        │
        ├───────────────┐
        ▼               ▼
  AI Diagnosis    Rule-Based Checker
        │               │
        └───────┬───────┘
                ▼
          Human Review
                │
        ┌───────┴───────┐
        ▼               ▼
    Accepted         Rejected
```

---

## Project Structure

```text
NetSage-AI/
│
├── README.md
├── cases.csv
│
├── data/
│   └── build_cases.py
│
├── prompts/
│   └── diagnose_prompt.md
│
├── ai_diagnosis/
│   ├── ai_diagnoses.json
│   └── build_diagnoses.py
│
├── checker/
│   ├── rule_checker.py
│   └── checker_report.csv
│
├── review/
│   ├── human_review_log.csv
│   ├── build_review_log.py
│   └── responsible_ai_log.md
│
├── dashboard/
│   ├── dashboard.xlsx
│   └── build_dashboard.py
│
└── demo/
    └── demo_script.md
```

---

## Dataset

`cases.csv` contains **30 realistic Packet Tracer fault scenarios**.

Each case includes:

* Case ID
* Network symptom
* Topology note
* `show` command output
* Ground-truth root cause
* Issue type
* Severity

---

## AI Diagnosis

The structured prompt is available at:

```text
prompts/diagnose_prompt.md
```

The AI receives the case evidence and produces a diagnosis containing:

```json
{
  "root_cause": "...",
  "confidence": 0.92,
  "evidence": ["..."],
  "next_command": "...",
  "fix_steps": ["..."]
}
```

The current `ai_diagnosis/ai_diagnoses.json` contains **pre-authored AI outputs** following this schema. They were not generated through a live LLM API call.

---

## Deterministic Checker

The rule-based checker is located at:

```text
checker/rule_checker.py
```

It does not use AI.

Currently, it checks for:

* Duplicate IP addresses
* Incorrect subnet masks
* Gateway mismatch
* Interface down
* Missing VLAN
* Missing route

The checker intentionally detects only predefined patterns.

---

## Human Review

Human review results are stored in:

```text
review/human_review_log.csv
```

Each AI diagnosis is classified as:

* `Accepted`
* `Rejected`

Six cases are intentionally incorrect to demonstrate the importance of human validation.

Rejected cases are documented in:

```text
review/responsible_ai_log.md
```

---

## Results

| Metric                | Result |
| --------------------- | -----: |
| Total Cases           |     30 |
| Accepted              |     24 |
| Rejected              |      6 |
| AI-Human Agreement    |    80% |
| Rule Checker Triggers | 4 / 30 |

> The 80% agreement rate applies only to the pre-authored dataset and should not be considered a benchmark for real-world LLM performance.

---

## Installation

Clone the repository:

```bash
git clone <this-repo>
cd NetSage-AI
```

Install the dependency:

```bash
python3 -m pip install openpyxl
```

On Windows:

```bash
python -m pip install openpyxl
```

---

## Run the Project

Run the scripts in this order:

```bash
python3 data/build_cases.py
python3 ai_diagnosis/build_diagnoses.py
python3 review/build_review_log.py
python3 checker/rule_checker.py
python3 dashboard/build_dashboard.py
```

---

## Packet Tracer Workflow

NetSage AI does **not currently integrate directly with Cisco Packet Tracer**.

The intended workflow is:

1. Create or reproduce the fault in Packet Tracer.
2. Run the relevant `show` commands.
3. Copy the CLI output.
4. Provide the evidence to the AI diagnosis prompt.
5. Run the deterministic checker.
6. Compare the results.
7. Perform human review.
8. Record the final verdict.

Example commands:

```text
show running-config
show ip interface brief
show vlan brief
show ip route
show interfaces
```

---

## Real LLM Integration

The current project does not make a live LLM API request.

To use a real model:

1. Obtain an API key.
2. Read each case from `cases.csv`.
3. Provide the symptom, topology note, and CLI output to the prompt.
4. Store the model response in:

```text
ai_diagnosis/ai_diagnoses.json
```

5. Run:

```bash
python3 review/build_review_log.py
```

The resulting agreement rate may differ from the current 80%.

---

## Limitations

* No automatic Packet Tracer integration.
* CLI evidence must currently be copied manually.
* The deterministic checker only detects predefined patterns.
* The dataset contains only 30 cases.
* Current AI diagnoses are pre-authored rather than generated through a live API.
* AI recommendations should be reviewed before applying network changes.

---

## Future Improvements

* Live LLM API integration
* Larger fault dataset
* More rule-based checks
* Automatic evidence validation
* Network topology visualization
* Web-based dashboard
* Multi-model diagnosis comparison
* Automated test-case generation
* Expanded Cisco IOS support

---

## Author

**Priyanshu Ranjan**

---

## ⭐ Support the Project

If you find **NetSage AI** useful or interesting, please consider giving the repository a **⭐ star** on GitHub.


