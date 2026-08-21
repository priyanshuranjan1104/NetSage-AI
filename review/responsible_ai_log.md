# Responsible AI Log — NetSage AI

This log documents every case where the AI's diagnosis was reviewed and
**rejected or corrected** by a human. Per the project's safety rule, no AI
diagnosis is ever applied to a lab without this review step.

**Result summary:** 30 cases run, 24 Accepted, 0 Edited, 6 Rejected.
AI-human agreement rate: **80%** (see `dashboard/` for the chart).

---

## Case V03 — Native VLAN mismatch (Rejected)

- **AI said:** Trunk between SW1 and SW2 is not fully configured.
- **Actually wrong because:** The trunk *was* up and passing traffic. The AI
  pattern-matched "CDP warning near a trunk" to "trunk not configured" instead
  of reading the specific warning text, which named a **native VLAN
  mismatch** (1 vs 99).
- **Correct root cause:** Native VLAN mismatch across the trunk.
- **Why it matters:** The AI's fix (re-enabling trunking) would have done
  nothing — the trunk was never down. A junior engineer trusting this
  blindly would waste time re-running a command that already succeeded.

## Case G03 — HSRP preempt disabled (Rejected)

- **AI said:** R1 is completely down and no backup gateway exists.
- **Actually wrong because:** HSRP *was* configured on R2 and correctly
  entered Standby state. The AI ignored that detail and assumed the
  simplest, most alarming explanation.
- **Correct root cause:** `standby preempt` is not enabled on R2, so it
  never takes over Active even when R1 fails.
- **Why it matters:** The AI's suggested fix ("wait for R1 to come back")
  leaves the network with no working failover. This is the kind of error
  that turns a planned maintenance window into an outage.

## Case D03 — DHCP excluded-address missing (Rejected)

- **AI said:** DHCP pool is low on addresses.
- **Actually wrong because:** The pool wasn't full. The real signal — a
  duplicate address conflict involving the *gateway's own IP* — points to a
  specific, well-known misconfiguration (gateway never excluded from the
  pool), not generic exhaustion.
- **Correct root cause:** Missing `ip dhcp excluded-address` for the gateway.
- **Why it matters:** The AI's fix (expanding the pool) does not solve the
  conflict and could make it worse by leasing out more addresses that clash
  with statically assigned devices.

## Case R02 — OSPF MTU mismatch (Rejected)

- **AI said:** OSPF isn't fully enabled on one interface.
- **Actually wrong because:** OSPF clearly *was* enabled on both sides — a
  neighbor relationship formed and reached EXSTART. Getting stuck exactly at
  EXSTART/EXCHANGE is a textbook MTU-mismatch signature, which the show
  output confirmed directly (1500 vs 1400).
- **Correct root cause:** MTU mismatch between R1 and R2 on the shared link.
- **Why it matters:** The AI missed evidence that was sitting right there
  in the output. This is the clearest case of the AI not fully using the
  evidence it was given — exactly what the human review step exists to catch.

## Case A03 — Standard vs. extended ACL misuse (Rejected)

- **AI said:** ACL applied in the wrong direction.
- **Actually wrong because:** Direction was never the issue. ACL 10 is a
  **standard** ACL, which can only filter by source address — it has no way
  to also match the specific destination (the HR server) the requirement
  called for. That's why it blocked the whole subnet everywhere, not just
  toward one server.
- **Correct root cause:** Standard ACL used where an extended ACL was required.
- **Why it matters:** Changing "direction" would not have fixed anything.
  This is a case where the AI's fix looks plausible but is categorically
  the wrong type of change.

## Case T03 — NAT ACL too narrow (Rejected)

- **AI said:** NAT overload pool exhausted.
- **Actually wrong because:** PAT overload on a single outside IP supports
  thousands of simultaneous port translations — it essentially never "runs
  out" the way the AI implied. The real gatekeeper is the ACL that decides
  *which* internal hosts qualify for translation at all, and it only
  covered part of the subnet.
- **Correct root cause:** NAT-referenced ACL too narrow, excluding
  192.168.1.192/27 from translation.
- **Why it matters:** The AI's fix (adding a second public IP) costs real
  money and doesn't fix the actual gap.

---

## Pattern across all 6 rejected cases

In every rejected case, the AI reached for the *most common* or *most
dramatic* explanation for a symptom instead of the explanation the specific
evidence actually supported. This is the main failure mode this project's
human-review requirement is designed to catch — the AI is a useful first
pass, not a verdict.
