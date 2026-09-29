# Freight Rate Copilot — Project Plan

## Problem statement

Freight/logistics teams field constant questions about rates, tariffs, and surcharges — "what's the fuel surcharge for this lane," "is this carrier's rate still valid," "why did this shipment cost more than quoted." Answers live scattered across rate sheets, carrier policy documents, and surcharge tables. A wrong answer isn't just unhelpful — quoting an expired rate or misreading a surcharge rule has a real dollar cost.

**This project is an assistant that answers those questions from real policy/rate documents — but never presents an answer as fact until deterministic code has checked it against the actual business rules.** The LLM proposes; code decides.

## Why this project (the resume narrative)

- Ties directly to real professional domain (Carrier Integration Service, freight/logistics) — not a generic tutorial clone.
- Demonstrates production-aware AI engineering, not just "I called an LLM API": retrieval, tool use via a real protocol (MCP), deterministic validation gates, an adversarial eval set with published numbers, observability, and a proven security defense.
- Gives concrete, defensible interview stories — every claim below is meant to be backed by a real number or a real test, not a vibe.

## Architecture

```
User question
     │
     ▼
┌─────────────────┐   Hybrid search (BM25-style keyword + embedding similarity)
│  RAG Retrieval   │   over mock rate sheets / carrier policies / surcharge rules,
│                  │   stored in Postgres + pgvector
└────────┬─────────┘
         │ retrieved evidence (chunks + similarity scores)
         ▼
┌─────────────────┐   LangGraph agent. May call a rate-lookup tool exposed
│  Proposer Agent  │   over MCP (Node.js server) for exact structured figures.
└────────┬─────────┘   Produces a DRAFT answer — never shown to the user yet.
         │
         ▼
┌─────────────────┐   Plain deterministic Python — NOT an LLM call:
│ Validation Gate  │     • is the cited rate within its validity date range?
│                  │     • is the carrier name a real, known carrier?
│                  │     • does the surcharge math actually reconcile?
│                  │     • is the cited fact literally present in the
│                  │       retrieved evidence (grounding check)?
└────────┬─────────┘   Anything failing here blocks the answer — no exceptions.
         │ only if ALL checks pass
         ▼
┌─────────────────┐   Second LLM call. Turns a validated, gate-approved
│  Responder Agent │   result into a polished, customer-facing answer.
└────────┬─────────┘   If the gate failed, this agent writes an honest
         │              refusal instead — never a guess.
         ▼
   Final answer (via API) → shown to the user
```

## Tech stack, and why

| Layer | Tech | Reason |
|---|---|---|
| RAG, agents, validation gate, evals | Python | Continues/extends the 12-topic roadmap build directly |
| Rate-lookup tool | Node.js, MCP server | Matches real day-job stack; extends Topic 8 directly |
| Vector storage | Postgres + pgvector (Docker) | Extends Topic 10 directly |
| API layer | TBD — likely FastAPI | New: needed for a live, deployable product; to be decided when we reach that phase |
| Deployment host | TBD | New territory, not covered by any roadmap topic — needs its own research pass before Phase 8 |

## What's reused vs. genuinely new

| Component | Status |
|---|---|
| Chunking, embeddings, hybrid search, pgvector | Reused directly from Topics 4, 5, 10 |
| Tool calling, MCP server | Reused/extended from Topics 6, 8 |
| LangGraph agent orchestration | Reused/extended from Topic 9 |
| Context/token management | Reused from Topic 7 |
| Eval harness (LLM-as-judge), observability logging, prompt-injection defense | Reused/extended from Topic 11 |
| Two-agent handoff pattern (proposer → responder) | Reused/extended from Topic 12 |
| **Deterministic validation gate** (business-rule checks, zero LLM calls) | **New** — the actual differentiator of this project |
| **Adversarial/unanswerable-heavy eval set with published metrics** | **New** — Topic 11 built the mechanism; this project needs a much larger, harder golden set |
| **Mock freight data generation** (rate sheets, policies, carrier list) | **New** |
| **API layer + live deployment** | **New** — nothing in the roadmap has run anywhere but localhost |
| **Product-spec README** (architecture diagram, quantified eval results, cost/latency, "what didn't work") | **New** |

## Build phases

- [ ] **Phase 0 — Mock data.** Realistic freight rate sheets, carrier policies, surcharge rules, a carrier list with validity dates. Enough internal structure (dates, numbers, carrier names) for the validation gate to actually have something to check.
- [ ] **Phase 1 — RAG retrieval.** Chunk the mock corpus, embed, store in pgvector, hybrid search working and verified against known-answer queries.
- [ ] **Phase 2 — Rate-lookup MCP tool.** Node.js MCP server exposing a structured rate/carrier lookup, connected to a real client.
- [ ] **Phase 3 — Proposer agent.** LangGraph agent combining RAG retrieval + the MCP tool, producing a draft answer.
- [ ] **Phase 4 — Validation gate.** The deterministic checks — expiry, carrier validity, surcharge math, literal grounding. This is the core differentiator; needs real unit tests of its own.
- [ ] **Phase 5 — Responder agent.** Turns a gate-passed result into a polished answer, or a gate-failed result into an honest refusal.
- [ ] **Phase 6 — Eval harness v2.** A real golden set: answerable questions, deliberately unanswerable ones, and adversarial/injection attempts — each category scored separately, numbers published.
- [ ] **Phase 7 — Observability + security.** Structured logging per request (question, evidence, gate result, cost, latency), prompt-injection defense carried over and re-verified in this new context.
- [ ] **Phase 8 — API + deployment.** Wrap everything behind an HTTP API, deploy somewhere with a real, live URL. Needs its own research pass first — not yet decided.
- [ ] **Phase 9 — README as product spec.** Problem statement, architecture diagram, real eval numbers, cost/latency figures, and an honest "what didn't work" section — not written until there's real data to report.

## Success criteria (to fill in with real numbers as we build — no invented numbers before Phase 6)

- Retrieval accuracy on the golden set: **TBD**
- Answer correctness (gate-passed answers judged correct): **TBD**
- Unanswerable-question refusal rate: **TBD**
- Adversarial/injection resistance rate: **TBD**
- Cost per request, p50/p95 latency: **TBD**

## Open questions / decisions still needed

- Exact deployment host (Phase 8 — needs its own research pass)
- Whether to build a minimal frontend or ship API-only for v1
- Exact size/composition of the golden eval set (Phase 6)
