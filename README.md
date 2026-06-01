# knowledge-organism

> Turn any project's knowledge base into a **living organism** — a self-updating law↔evidence graph with an immune system, self-correction, and always-on hooks. So findings **compound** instead of rotting in scattered docs.

A Claude Code skill (works as a plain Python tool too). Born inside a hyperdimensional-computing chip-research program where dozens of experiments kept re-deriving the same lessons and hiding contradictions. The fix generalizes to any research/build effort.

## The idea
Give your project a **DNA** of numbered, falsifiable *laws*. Make every experiment **declare which laws it tests** and **digest its result** into a machine-readable graph. Then:
- **Metabolism** — `Kit.emit()` writes each result as an evidence node keyed by law.
- **Immune system** — a `CONFIRM` with no saved artifact is **VOID**ed; a `CONFIRM` lacking held-out split + baseline + ≥3 seeds is **downgraded to POC**. No ungrounded claim enters the bloodstream.
- **Self-correction** — `reflect()` flags laws with mixed CONFIRM+FALSIFY verdicts for review.
- **Senses** — `recall(law)` shows everything known about a law before you act.
- **Always-on** — two Claude Code hooks (SessionStart injects the laws + health into context; Stop self-checks and flags undigested results). It runs without you remembering to.

Pull one law → see every experiment that fed it. 牵一发而动全身.

## Quickstart
```bash
cp organism.py templates/LAWS-REGISTRY-template.md  your-project/
mv LAWS-REGISTRY-template.md LAWS-REGISTRY.md       # write your laws: **L1.** ...
```
```python
import organism
kit = organism.Kit("my_experiment", tests=["L1"])
kit.emit(verdict="CONFIRM", result={"metric": 0.93},
         note="what it means + honest boundary",
         csv_path="results/run.csv", held_out=True, baseline="random", seeds=3)
```
```bash
python3 organism.py            # health
python3 organism.py recall L1  # what's known about L1
```
Config via env: `KO_REGISTRY`, `KO_LEDGER`, `KO_ID_RE`. Hooks: see `templates/hooks-snippet.json`.

## Design principles it enforces
- **Set the ruler first** — a law states what would confirm *and* falsify it.
- **Evidence before assertion** — claims must trace to a saved artifact (the immune gate).
- **Negatives are kept** — a FALSIFY is recorded, not deleted; boundary laws *should* be mixed.
- **Laws are executable, not passive** — the gate runs at digestion time, so a violation is caught automatically rather than living in a doc nobody re-reads.

MIT-spirited; share freely.

## Active discovery — the organism proposes the next experiment
Beyond recording, it *plans*:
```bash
python3 organism.py agenda      # ranked next-experiments: info-gain × law centrality
python3 organism.py anomalies   # rigorous CONFIRM↔FALSIFY tension → candidate new/refined laws
```
`agenda()` spends your next experiment where it most reduces uncertainty on the most load-bearing law (resolve a contradiction → promote a flagship PoC to CONFIRM → gather where sparse). `anomalies()` is the augmentation arm — a rigorous result that bucks a law's confirmed direction becomes a candidate refinement or new law. The SessionStart hook injects the top-3 agenda + live anomalies, so every session opens with "what to run next." (PiEvo-inspired — arXiv 2602.06448 — adapted to a discrete law graph; honestly a heuristic, not a GP/BALD surrogate.)
