#!/usr/bin/env python3
"""knowledge-organism — turn any knowledge base into a LIVING ORGANISM (project-agnostic core).

The idea: stop letting findings rot in scattered docs. Give your project a DNA of numbered LAWS
(or principles), and make every experiment DIGEST its result into a machine-readable law<-evidence
graph — with an IMMUNE SYSTEM that refuses ungrounded claims, SELF-CORRECTION that flags
contradictions, and SENSES that let you recall what's known before acting. Pull one law -> see every
experiment that fed it ("牵一发而动全身"). Wire the two hooks (see SKILL.md) and it runs always-on.

Anatomy:  DNA=registry of laws · metabolism=Kit.emit (digests results) · nervous=ledger edges
          immune=_gate (auto-VOID/DOWNGRADE) · self-correction=reflect · senses=recall

Config (env, with sane cwd defaults so it works anywhere):
  KO_REGISTRY  path to your laws/principles markdown   (default ./LAWS-REGISTRY.md)
  KO_LEDGER    path to the evidence jsonl              (default ./LAWS-EVIDENCE.jsonl)
  KO_ID_RE     regex for law ids in the registry       (default '\\*\\*([LP]\\d+)[.\\s]')
"""
import os, json, re, datetime, pathlib

REGISTRY = pathlib.Path(os.environ.get("KO_REGISTRY", "LAWS-REGISTRY.md"))
LEDGER   = pathlib.Path(os.environ.get("KO_LEDGER",   "LAWS-EVIDENCE.jsonl"))
ID_RE    = os.environ.get("KO_ID_RE", r"\*\*([LP]\d+)[.\s]")

def known_laws():
    """Parse law/principle ids from the registry so we can validate declared laws exist (DNA check)."""
    if not REGISTRY.exists(): return set()
    return set(re.findall(ID_RE, REGISTRY.read_text()))

class Kit:
    """Metabolism + immune system. Declare which laws an experiment tests, then emit() its result."""
    def __init__(self, experiment, tests, could_update=None, results_dir="."):
        self.exp=experiment; self.tests=list(tests); self.could_update=list(could_update or [])
        self.results_dir=pathlib.Path(results_dir)
        known=known_laws()
        unknown=[l for l in self.tests+self.could_update if known and l not in known]
        if unknown: print(f"[organism][WARN] declared laws not in registry (typo or new?): {unknown}")
        print(f"[organism] experiment={experiment} tests={self.tests} could_update={self.could_update}")

    def _gate(self, verdict, csv_path, held_out, baseline, seeds):
        """IMMUNE SYSTEM — cheap rigor gates at digestion time. Won't let an ungrounded CONFIRM in:
        no artifact -> VOID; CONFIRM without held-out+baseline+seeds>=3 -> downgraded to POC."""
        reasons=[]
        if verdict in ("CONFIRM","FALSIFY") and not csv_path:
            return "VOID","VOID",["claim must trace to a saved artifact (csv/json)"]
        if verdict=="CONFIRM":
            if not held_out: reasons.append("no held-out split declared")
            if not baseline: reasons.append("no baseline (beats-random) declared")
            if not seeds or seeds<3: reasons.append(f"seeds={seeds} <3 -> PoC not Golden-Standard")
            if reasons: return "POC","DOWNGRADED",reasons
        return verdict,"PASS",reasons

    def emit(self, verdict, result, note="", csv_path=None, held_out=None, baseline=None, seeds=None):
        eff,gate,reasons=self._gate(verdict,csv_path,held_out,baseline,seeds)
        if gate!="PASS": print(f"[organism][IMMUNE] {gate}: {verdict}->{eff} reasons={reasons}")
        ts=datetime.datetime.now().isoformat(timespec="seconds")
        rec={"ts":ts,"experiment":self.exp,"verdict":eff,"declared_verdict":verdict,"gate":gate,
             "gate_reasons":reasons,"laws_applied":self.tests,"could_update":self.could_update,
             "result":result,"note":note,"csv":csv_path,"held_out":held_out,"baseline":baseline,"seeds":seeds}
        out=self.results_dir/f"_organism_{self.exp}.json"; out.write_text(json.dumps(rec,indent=2,ensure_ascii=False))
        if gate=="VOID":
            print(f"[organism] VOID — not absorbed (immune rejected). reasons={reasons}"); return rec
        LEDGER.parent.mkdir(parents=True,exist_ok=True)
        with open(LEDGER,"a") as f:
            for law in self.tests: f.write(json.dumps({"law":law,**rec},ensure_ascii=False)+"\n")
        print(f"[organism] EMITTED verdict={eff} laws={self.tests} -> {out.name} + {LEDGER.name}")
        return rec

def _all(): return [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()] if LEDGER.exists() else []
def law_evidence(law): return [e for e in _all() if e["law"]==law]

def recall(law):
    """SENSES — perceive what's already known about a law before acting."""
    ev=law_evidence(law); vs={}
    for e in ev: vs.setdefault(e["verdict"],[]).append(e["experiment"])
    print(f"[recall {law}] {len(ev)} nodes; verdicts={{{', '.join(f'{k}:{len(v)}' for k,v in vs.items())}}}")
    for e in ev: print(f"    - {e['verdict']:8s} {e['experiment']}: {e.get('note','')[:80]}")
    return {"law":law,"n":len(ev),"verdicts":vs,"evidence":ev}

def reflect():
    """SELF-CORRECTION — flag laws with MIXED verdicts (CONFIRM+FALSIFY) for review."""
    ev=_all(); laws={}
    for e in ev: laws.setdefault(e["law"],[]).append(e)
    print(f"\n=== organism reflect (health) — {len(ev)} evidence nodes / {len(laws)} laws ===")
    flags=[]
    for law in sorted(laws):
        vs={}
        for e in laws[law]: vs[e["verdict"]]=vs.get(e["verdict"],0)+1
        mixed=("CONFIRM" in vs and "FALSIFY" in vs)
        if mixed: flags.append(law)
        print(f"  {law}: {len(laws[law])} nodes {vs}  {'MIXED — review' if mixed else 'ok'}")
    if flags: print(f"  -> review queue (mixed verdicts): {flags}")
    return {"laws":{l:len(laws[l]) for l in laws},"review_queue":flags}

def organism_status():
    print("=== KNOWLEDGE ORGANISM — status ===")
    print(f" DNA: {len(known_laws())} laws in {REGISTRY}"); reflect()

def hook_session():
    laws=sorted(known_laws()); P={}
    for e in _all(): P.setdefault(e["law"],[]).append(e)
    print("[KNOWLEDGE ORGANISM — always-on]")
    print(f"DNA: {len(laws)} laws ({', '.join(laws[:6])}…). Before substantial work: declare tests=[law] + use the Kit.")
    for l in sorted(P):
        vs={}
        for e in P[l]: vs[e["verdict"]]=vs.get(e["verdict"],0)+1
        print(f"  {l}: {vs}")
    print("Rule: every experiment `import organism; organism.Kit(name,tests=[law]).emit(...)` or its result is an orphan.")
    print(""); agenda(top=3)            # ACTIVE: open every session with what to run next
    an=anomalies()
    if an: print(f"[organism] {len(an)} live anomaly(ies) → candidate law refinement; see `organism.py anomalies`")

def hook_stop(results_dir="."):
    import glob
    rep=reflect()
    csvs=set(os.path.basename(p) for p in glob.glob(os.path.join(results_dir,"results_*.csv")))
    fed=set(os.path.basename(e["csv"]) for e in _all() if e.get("csv"))
    orphans=sorted(c for c in csvs if c not in fed)
    if orphans: print(f"[organism][ORPHAN] {len(orphans)} result CSVs not digested: {orphans[:8]}")
    if rep["review_queue"]: print(f"[organism][REVIEW] mixed-verdict laws: {rep['review_queue']}")
    return {"orphans":orphans,**rep}

# ---- ACTIVE DISCOVERY (PiEvo-inspired) — the organism PROPOSES the next experiment ----
def _asint(x):
    try: return int(x)
    except: return 0

def agenda(top=8):
    """ACTIVE LOOP — turn the passive evidence graph into a RANKED next-experiment agenda.
    Heuristic information-gain × law centrality (NOT a GP/BALD surrogate — same spirit adapted to a
    discrete law graph): spend the next experiment where it most reduces uncertainty on the most
    load-bearing law. Moves: RESOLVE (mixed), PROMOTE (PoC→CONFIRM), GATHER (sparse), SETTLED (monitor)."""
    import math
    ev=_all(); bylaw={}
    for e in ev: bylaw.setdefault(e["law"],[]).append(e)
    items=[]
    for law,g in bylaw.items():
        v={}
        for e in g: v[e["verdict"]]=v.get(e["verdict"],0)+1
        c=v.get("CONFIRM",0); p=v.get("POC",0); f=v.get("FALSIFY",0); n=len(g)
        rigor_c=sum(1 for e in g if e["verdict"]=="CONFIRM" and e.get("held_out") and _asint(e.get("seeds"))>=3)
        central=math.log(1+n)
        if c>0 and f>0:   move="RESOLVE — run a disambiguator isolating where it HOLDS vs BREAKS"; base=1.0
        elif p>0 and rigor_c==0: move=f"PROMOTE — upgrade flagship PoC to CONFIRM (≥3 seeds+held-out+baseline); {p} PoC, 0 rigorous CONFIRM"; base=0.8
        elif n<3: move="GATHER — too few nodes; add independent evidence"; base=0.6
        else: move="SETTLED — monitor; only an edge/stress case adds info"; base=0.2
        items.append({"law":law,"n":n,"verdicts":v,"move":move,"score":round(base*central,3)})
    items.sort(key=lambda x:-x["score"])
    print("=== ORGANISM AGENDA — what to run next (info-gain × centrality) ===")
    for it in items[:top]:
        print(f"  [{it['score']:.2f}] {it['law']} (n={it['n']} {it['verdicts']})\n         → {it['move']}")
    return items

def anomalies():
    """A RIGOROUS minority verdict (held-out+≥3-seed CONFIRM vs FALSIFY tension) = a real surprise
    → candidate law REFINEMENT or NEW law. Ignores the PoC mass (only rigorous tension counts)."""
    ev=_all(); bylaw={}
    for e in ev: bylaw.setdefault(e["law"],[]).append(e)
    out=[]
    print("=== ANOMALIES — rigorous CONFIRM↔FALSIFY tension (candidate new/refined laws) ===")
    for law,g in bylaw.items():
        rig=[e for e in g if e.get("held_out") and _asint(e.get("seeds"))>=3 and e["verdict"] in ("CONFIRM","FALSIFY")]
        pol=set(e["verdict"] for e in rig)
        if {"CONFIRM","FALSIFY"} <= pol:
            nc=sum(1 for e in rig if e["verdict"]=="CONFIRM"); nf=len(rig)-nc
            minor="FALSIFY" if nf<=nc else "CONFIRM"
            for e in rig:
                if e["verdict"]==minor:
                    out.append((law,e)); print(f"  {law}: '{e['experiment']}' is {e['verdict']} vs {nc}C/{nf}F rigorous → {e.get('note','')[:100]}")
    if not out: print("  (none — organism coherent)")
    return out

if __name__=="__main__":
    import sys
    a=sys.argv[1:]
    if not a: organism_status()
    elif a[0]=="--hook-session": hook_session()
    elif a[0]=="--hook-stop": hook_stop(a[1] if len(a)>1 else ".")
    elif a[0]=="recall" and len(a)>1: recall(a[1])
    elif a[0]=="agenda": agenda()
    elif a[0]=="anomalies": anomalies()
    else: organism_status()
