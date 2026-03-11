"""
Divine Whisper – Monolithic demo
• 12-Archangel cognition engine
• Inward-Physics state + evolution
• Parallel chamber executor
• Mini ledger
• ENOCH-X style council (here using Grok-only for brevity)

Requires: requests  (pip install requests)
Set GROK_API_KEY in environment or replace `grok_chat` with your own call.
"""

import os, time, json, random, threading, concurrent.futures as fx
from dataclasses import dataclass, asdict
from pathlib import Path
from difflib import SequenceMatcher

# ─────────────────────────────────────────────────────────────────────────────
# 0.  ───── Inward-Physics MindState & evolution ──────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class MindState:
    A: float = 0.4   # attention
    D: float = 0.6   # distortion
    C: float = 0.4   # coherence
    F: float = 0.5   # free-energy / cost
    lam: float = 0.4 # remembrance fidelity
    S: float = 0.3   # salience

    # master clarity Ψ(t)
    def clarity(self, eps: float = 1e-5) -> float:
        return self.lam * self.C * self.S / ((self.D + eps) ** 2 * (self.F + eps))

    # bounded additive update
    def apply(self, deltas: dict[str, float], clamp=(0.0, 1.0)):
        lo, hi = clamp
        for k, v in deltas.items():
            if hasattr(self, k):
                setattr(self, k, max(lo, min(hi, getattr(self, k) + v)))

def evolve_physics(state: MindState, noise: float = 0.01):
    """Very simple placeholder dynamics so numbers move each cycle."""
    state.D -= 0.05 * state.A
    state.C += 0.04 * state.A - 0.02 * state.D
    state.F += 0.01
    state.S += 0.03 * state.C
    state.apply({})  # just clamps
    for k in ("A", "D", "C", "F", "lam", "S"):
        state.apply({k: random.uniform(-noise, noise)})

# ─────────────────────────────────────────────────────────────────────────────
# 1.  ───── Grok chat helper  (replace as needed)  ────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────

def grok_chat(model: str, prompt: str) -> str:
    """
    Minimal Grok 1.5 call.  Replace URL / headers with the current X.ai endpoint
    or swap in any other hosted model.  A fake reply is returned if no API key.
    """
    key = os.getenv("GROK_API_KEY")
    if not key:
        return f"[Grok-stub] {prompt[:60]} …"
    import requests, uuid
    resp = requests.post(
        "https://api.grok.ai/v1/chat/completions",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "stream": False,
            "n": 1,
            "request_id": str(uuid.uuid4())
        },
        headers={"Authorization": f"Bearer {key}"},
        timeout=25,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()

# ─────────────────────────────────────────────────────────────────────────────
# 2.  ───── ENOCH-X council (Grok-only variant)  ─────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────

def run_council(prompt: str, reps: int = 3) -> dict[str, str]:
    """
    Call Grok `reps` times in parallel, then pick the answer most similar to
    its peers (quick lexical voting).  Each answer is truncated to 4 k chars.
    """
    def ask(_): return grok_chat("grok-1.5", prompt)[:4096]

    answers: dict[str, str] = {}
    with fx.ThreadPoolExecutor(max_workers=reps) as pool:
        futs = {pool.submit(ask, i): f"grok_{i}" for i in range(reps)}
        for fut in fx.as_completed(futs):
            answers[futs[fut]] = fut.result()

    # similarity vote
    texts = list(answers.values())
    def sim(a, b): return SequenceMatcher(None, a, b).ratio()
    score = [
        sum(sim(t, t2) for t2 in texts if t2 != t) / (len(texts) - 1)
        for t in texts
    ]
    best = texts[score.index(max(score))]
    return {"answer": best, "council": answers, "similarity_scores": score}

# ─────────────────────────────────────────────────────────────────────────────
# 3.  ───── Archangel registry (12 stubs) ─────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────

ARCHANGELS: dict[str, dict] = {
    # name      role              default deltas
    "michael":  {"role": "truth/defense", "deltas": {"D": -0.1, "A": 0.05}},
    "gabriel":  {"role": "communication", "deltas": {"C": 0.05}},
    "raphael":  {"role": "repair",        "deltas": {"D": -0.05}},
    "uriel":    {"role": "wisdom",        "deltas": {"C": 0.07, "S": 0.03}},
    "metatron": {"role": "structure",     "deltas": {"lam": 0.06}},
    "remiel":   {"role": "review",        "deltas": {"F": -0.04}},
    "raziel":   {"role": "discovery",     "deltas": {"S": 0.08}},
    "zadkiel":  {"role": "mercy",         "deltas": {"D": -0.03}},
    "chamuel":  {"role": "relationships", "deltas": {"C": 0.04}},
    "jophiel":  {"role": "beauty",        "deltas": {"S": 0.05}},
    "haniel":   {"role": "salience",      "deltas": {"S": 0.04}},
    "sandalphon": {"role": "grounding",   "deltas": {"lam": 0.05}},
}

def run_archangel(name: str, body: dict, state: MindState) -> dict:
    """
    Minimal default behaviour:
      • Raziel invokes Grok council for discovery questions.
      • Gabriel rewrites user text.
      • Others just echo their role and apply default deltas.
    """
    info = ARCHANGELS.get(name, {})
    role = info.get("role", "unknown")
    deltas = info.get("deltas", {})

    if name == "raziel":
        council = run_council(body["text"])
        result = council["answer"]
        return {"result": result, "deltas": deltas, "confidence": 0.9,
                "trace": council}
    if name == "gabriel":
        rewritten = grok_chat("grok-1.5", f"Rewrite clearly:\n{body['text']}")
        return {"result": rewritten, "deltas": deltas, "confidence": 0.85}

    # generic fallback
    return {"result": f"{role} processed", "deltas": deltas, "confidence": 0.8}

# ─────────────────────────────────────────────────────────────────────────────
# 4.  ───── Orchestrator  (intent → plan) ────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────

INTENT_MAP = {
    "truth":   ["michael", "gabriel"],
    "design":  ["metatron", "michael", "gabriel"],
    "repair":  ["raphael", "michael", "gabriel"],
    "research":["raziel", "uriel", "michael", "gabriel"],
    "social":  ["chamuel", "zadkiel", "gabriel"],
}

def classify(text: str) -> str:
    t = text.lower()
    for k in INTENT_MAP:
        if k in t:
            return k
    return "generic"

def make_plan(user_input: str, state: MindState) -> list[dict]:
    intent = classify(user_input)
    seq = INTENT_MAP.get(intent, ["uriel", "gabriel"])
    return [{"archangel": a, "body": {"text": user_input}} for a in seq]

# ─────────────────────────────────────────────────────────────────────────────
# 5.  ───── Parallel chamber executor ────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────

def execute_plan(plan: list[dict], state: MindState) -> tuple[list, dict]:
    results, deltas = [], {}
    def worker(step): return run_archangel(step["archangel"], step["body"], state)

    with fx.ThreadPoolExecutor(max_workers=len(plan)) as pool:
        for out in pool.map(worker, plan):
            results.append(out)
            for k, v in out.get("deltas", {}).items():
                deltas[k] = deltas.get(k, 0.0) + v
    return results, deltas

# ─────────────────────────────────────────────────────────────────────────────
# 6.  ───── Ledger (JSON-lines) ──────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────

LEDGER_PATH = Path("/tmp/divine_whisper_ledger.jsonl")
LEDGER_LOCK = threading.Lock()

def log_entry(data: dict):
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_LOCK, LEDGER_PATH.open("a") as f:
        f.write(json.dumps(data) + "\n")

# ─────────────────────────────────────────────────────────────────────────────
# 7.  ───── Conversation loop  ───────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────

BREAKTHRESH = 0.9   # clarity required to exit early

def run_conversation(user_input: str, max_cycles: int = 6):
    state = MindState()
    for cycle in range(max_cycles):
        plan = make_plan(user_input, state)
        results, deltas = execute_plan(plan, state)
        state.apply(deltas)
        evolve_physics(state)
        log_entry({"cycle": cycle, "plan": plan, "results": results,
                   "state": asdict(state)})
        if state.clarity() >= BREAKTHRESH:
            break
    return {"results": results, "state": state}

# ─────────────────────────────────────────────────────────────────────────────
# 8.  ───── CLI entry-point  ─────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python divine_whisper_monolith.py 'your prompt here'")
        sys.exit(1)
    prompt = sys.argv[1]
    out = run_conversation(prompt)
    print("\n=== FINAL STATE ===")
    print(out["state"])
    print("\n=== RESULTS ===")
    for r in out["results"]:
        print(f"- {r['result'][:120]} … (Δ {r['deltas']})")
