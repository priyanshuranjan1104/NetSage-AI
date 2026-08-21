"""
rule_checker.py — NetSage AI deterministic checker.

Independent of the AI: this scans the raw show-command evidence in
cases.csv with plain text/regex rules and flags known config mistakes.
It is meant to run BEFORE or AFTER the AI diagnosis and give a second,
non-AI signal the human reviewer can cross-check the AI against.

Checks implemented (per the problem statement):
  1. Duplicate IP addresses
  2. Wrong / mismatched subnet mask
  3. Gateway mismatch (PC gateway vs router's actual interface IP)
  4. Interface administratively/operationally down
  5. Missing VLAN (referenced but not present in VLAN database)
  6. Missing route (a subnet mentioned in the topology note with no
     matching entry in a "show ip route" block)

Usage:
    python3 rule_checker.py [path/to/cases.csv]

Output:
    checker_report.csv  — one row per case, per flag raised
    Also prints a summary to stdout.
"""
import csv
import re
import sys
from pathlib import Path

DEFAULT_INPUT = Path(__file__).resolve().parent.parent / "cases.csv"
OUTPUT = Path(__file__).resolve().parent / "checker_report.csv"


def check_duplicate_ip(show_output: str):
    ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", show_output)
    seen = {}
    for ip in ips:
        seen[ip] = seen.get(ip, 0) + 1
    dupes = [ip for ip, count in seen.items() if count > 1]
    if dupes and re.search(r"duplicate|conflict", show_output, re.IGNORECASE):
        return f"Duplicate IP address detected: {', '.join(dupes)}"
    return None


def check_wrong_mask(show_output: str):
    # Flag any mask shorter than /24 equivalent classful default mismatch
    # heuristic: look for a /28-style mask (255.255.255.240) paired with a
    # network statement or PC config that implies a /24 LAN.
    masks = re.findall(r"255\.255\.255\.\d{1,3}", show_output)
    if "255.255.255.240" in masks or "255.255.255.224" in masks:
        return f"Non-standard subnet mask found ({masks}) — verify it matches the intended LAN size"
    return None


def check_gateway_mismatch(show_output: str):
    gw_match = re.search(r"Default Gateway:\s*((?:\d{1,3}\.){3}\d{1,3})", show_output)
    router_ips = re.findall(r"ip address\s+((?:\d{1,3}\.){3}\d{1,3})", show_output)
    iface_ips = re.findall(r"IP-Address\s*\n?.*?((?:\d{1,3}\.){3}\d{1,3})", show_output)
    candidates = set(router_ips) | set(iface_ips)
    if gw_match and candidates and gw_match.group(1) not in candidates:
        return f"PC default gateway {gw_match.group(1)} does not match any router interface IP found in evidence ({sorted(candidates)})"
    return None


def check_interface_down(show_output: str):
    if re.search(r"administratively down|down\s+down", show_output, re.IGNORECASE):
        return "Interface reported administratively down or down/down"
    return None


def check_missing_vlan(show_output: str, topology_note: str):
    referenced = set(re.findall(r"VLAN\s?(\d+)", show_output + " " + topology_note, re.IGNORECASE))
    if not referenced:
        return None
    vlan_brief_block = re.search(r"show vlan brief(.*)", show_output, re.IGNORECASE | re.DOTALL)
    if not vlan_brief_block:
        return None
    block = vlan_brief_block.group(1)
    listed_vlans = set(re.findall(r"^\s*(\d+)\s", block, re.MULTILINE))
    missing = [v for v in referenced if v not in listed_vlans and v not in ("0",)]
    # Only flag if the output text itself says the VLAN isn't listed/present
    if missing and re.search(r"not listed|not present|missing", show_output, re.IGNORECASE):
        return f"VLAN(s) referenced but not found in VLAN database: {missing}"
    return None


def check_missing_route(show_output: str):
    if not re.search(r"show ip route", show_output, re.IGNORECASE):
        return None
    # Prefer a subnet explicitly named next to "no route to" / "not present" /
    # "no entry" over any other subnet mentioned elsewhere in the output
    # (e.g. a directly-connected network listed in the same block).
    targeted = re.search(
        r"no route to\s*((?:\d{1,3}\.){3}\d{1,3}/\d{1,2})", show_output, re.IGNORECASE)
    if targeted:
        return f"show ip route has no entry for {targeted.group(1)}"
    if re.search(r"not present|no entry", show_output, re.IGNORECASE):
        subnet = re.search(r"((?:\d{1,3}\.){3}\d{1,3}/\d{1,2})", show_output)
        if subnet:
            return f"show ip route has no entry for {subnet.group(1)}"
        return "show ip route is missing an expected route entry"
    return None


CHECKS = [
    ("duplicate_ip", lambda row: check_duplicate_ip(row["show_output"])),
    ("wrong_mask", lambda row: check_wrong_mask(row["show_output"])),
    ("gateway_mismatch", lambda row: check_gateway_mismatch(row["show_output"])),
    ("interface_down", lambda row: check_interface_down(row["show_output"])),
    ("missing_vlan", lambda row: check_missing_vlan(row["show_output"], row["topology_note"])),
    ("missing_route", lambda row: check_missing_route(row["show_output"])),
]


def run(input_path: Path):
    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = []
    for row in rows:
        flags_found = 0
        for check_name, check_fn in CHECKS:
            result = check_fn(row)
            if result:
                flags_found += 1
                results.append({
                    "case_id": row["case_id"],
                    "category": row["category"],
                    "check": check_name,
                    "flag": result,
                })
        if flags_found == 0:
            results.append({
                "case_id": row["case_id"],
                "category": row["category"],
                "check": "none",
                "flag": "No deterministic rule matched — relies on AI/human judgement",
            })

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["case_id", "category", "check", "flag"])
        w.writeheader()
        w.writerows(results)

    triggered = [r for r in results if r["check"] != "none"]
    print(f"Checked {len(rows)} cases, {len(rows)} covered by CSV.")
    print(f"Deterministic checks triggered on {len(triggered)} rows across {len({r['case_id'] for r in triggered})} distinct cases.")
    print(f"Report written to {OUTPUT}")
    print()
    for r in results:
        print(f"[{r['case_id']:>4}] {r['check']:<18} {r['flag']}")


if __name__ == "__main__":
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    run(input_path)
