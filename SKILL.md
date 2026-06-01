---
name: knowledge-organism
description: Turn any project's knowledge base into a LIVING ORGANISM — a self-updating law↔evidence graph with an immune system, self-correction, and always-on hooks. Invoke when you want findings to COMPOUND instead of rot: "raise this as an organism", "digest this result", "what do we know about law L#", "set up the knowledge organism", "stop re-deriving lessons", "evidence ledger", "牵一发而动全身". Project-agnostic (configurable via KO_REGISTRY/KO_LEDGER env). Born 2026-06-01 in the HDC research program; generalized for sharing.
---

# knowledge-organism — raise your knowledge base as a living thing

**Problem it solves:** in a long research/build program, findings scatter across docs, get re-derived, and contradictions hide. Memory stales; nothing compounds. This makes the knowledge base **deterministic + accelerating**: every result is digested into a graph keyed by the *laws* (or principles) it tests — nothing lost, contradictions auto-surface, pull one law and see all its evidence.

## Anatomy (biological metaphor, real mechanics)
| Organ | What it is | File / call |
|---|---|---|
| **DNA** | numbered laws/principles | `LAWS-REGISTRY.md` (append-only) |
| **Metabolism** | digests a result into evidence | `Kit(exp, tests=[...]).emit(...)` |
| **Nervous system** | law←evidence edges | `LAWS-EVIDENCE.jsonl` |
| **Immune system** | refuses ungrounded claims | `_gate` (auto-VOID / downgrade) |
| **Self-correction** | flags contradictions | `reflect()` |
| **Senses** | perceive before acting | `recall(law)` |

## Setup (once per project)
1. Copy `organism.py` into the project (or point to it).
2. Create `LAWS-REGISTRY.md` from `templates/LAWS-REGISTRY-template.md` — number your laws `**L1.** ...`, `**L2.** ...` (or `P1` for principles).
3. (Optional but the point) wire always-on hooks in `.claude/settings.local.json` — see `templates/hooks-snippet.json`. SessionStart injects the laws + health into context; Stop self-checks + flags undigested results.
4. Set `KO_REGISTRY` / `KO_LEDGER` if your files aren't in cwd.

## Core discipline (the one rule)
**Every experiment declares which laws it tests, and emits its result — or that result is an orphan.**
```python
import organism
kit = organism.Kit("my_experiment", tests=["L1"], could_update=["L1"])
kit.emit(verdict="CONFIRM", result={"metric": 0.93},
         note="what it means + honest boundary",
         csv_path="results/run.csv",      # immune system VOIDs CONFIRM/FALSIFY without an artifact
         held_out=True, baseline="random 1/N", seeds=3)  # CONFIRM needs all three or it's downgraded to POC
```
Verdicts: `CONFIRM` (held-out + baseline + ≥3 seeds), `POC` (works but not yet Golden-Standard), `FALSIFY` (config/hypothesis failed — still valuable, still recorded), `VOID` (immune-rejected, no artifact).

## Reading the organism
```bash
python3 organism.py                 # status + health (reflect)
python3 organism.py recall L1        # everything known about L1
python3 organism.py --hook-session   # what the SessionStart hook injects
python3 organism.py --hook-stop .    # self-check + orphan scan
```

## Why MIXED verdicts are healthy
A boundary/meta-law accrues both CONFIRM and FALSIFY by design (it marks *where* something holds). `reflect()` flags these for review — that's the immune system working, not an error. Don't "resolve" a boundary law by deleting losses.

## Lineage
First grown in a hyperdimensional-computing chip program (the HDC laws L0–L17). The same machinery runs on any domain — give it your laws and feed it your results.
