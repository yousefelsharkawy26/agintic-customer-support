# Generic AI Customer Support Platform — Implementation Plan (v2.0)

> **Vision:** A plug-and-play, multi-tenant AI customer support SaaS that any company can deploy on their site. Combines RAG, MCP-driven tool integration, and LangGraph-based agent orchestration — no per-customer integration code required.
>
> The architecture is designed to extend beyond customer support to any agent vertical (Sales, HR, IT, etc.) without rewriting the core — by building abstractions now and deferring implementations until needed.

---

## Table of Contents

1. [Architecture Review](#1-architecture-review)
2. [Refined Architecture](#2-refined-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Core Components Deep Dive](#5-core-components-deep-dive)
6. [Phased Plan (8 Phases)](#6-phased-plan-8-phases)
7. [Decisions Needed Before Kickoff](#7-decisions-needed-before-kickoff)
8. [Risks & Mitigations](#8-risks--mitigations)
9. [Success Metrics](#9-success-metrics)
10. [Open Questions](#10-open-questions)
11. [Architectural Principle](#11-architectural-principle)

---

## 1. Architecture Review

### 1.1 What's Strong

- **MCP as the integration layer** — eliminates months of per-vendor integration code.
- **Multi-tenant from day 1** — retrofitting later requires rewriting half the system.
- **Pluggable providers via interfaces** — keeps the core stable as vendors change.
- **Qdrant** — good choice for multi-tenant via collection namespacing + payload filtering.
- **LangGraph** — production-grade agent orchestration (more mature than CrewAI).
- **Redis + Postgres split for memory** — each in its right role.

### 1.2 Critical Gaps From First Review

| Gap                                               | Why it matters                                         |
| ------------------------------------------------- | ------------------------------------------------------ |
| **Streaming responses (SSE/WebSocket)**           | Without it the widget feels dead. Required from day 1. |
| **Semantic cache**                                | ~40% of questions repeat. Saves cost + latency.        |
| **RAG evaluation (RAGAS or custom)**              | Without it you can't tell if retrieval is working.     |
| **Guardrails (PII, prompt injection, jailbreak)** | Customer-facing = attack surface.                      |
| **Conversation summarization**                    | Context window blows up after ~20 turns.               |
| **Per-tenant cost quotas**                        | One runaway tenant can burn your API bill in an hour.  |
| **Doc versioning & invalidation**                 | Policy changed on site — RAG must know.                |
| **Cold-start handling**                           | New tenant with zero docs — what does the agent say?   |
| **Long-running MCP tool execution**               | Cancellation, timeouts, progress events.               |
| **Eval-driven dev loop**                          | Without an eval set you're flying blind.               |

### 1.3 Verdict on the 11 Proposed Enhancements

| #     | Enhancement                            | Verdict                    | Phase                          |
| ----- | -------------------------------------- | -------------------------- | ------------------------------ |
| 10.1  | Event-Driven Architecture              | ✅ Must-have               | Phase 0                        |
| 10.2  | Modular Agent Pipeline                 | ✅ Must-have               | Phase 3                        |
| 10.3  | Prompt Versioning & Management         | ✅ Must-have               | Phase 1                        |
| 10.4  | Model Router                           | ✅ Must-have               | Phase 1                        |
| 10.5  | Plugin SDK                             | ⏸️ Deferred                | Phase 8+                       |
| 10.6  | Tool Registry Versioning               | ✅ Must-have               | Phase 3                        |
| 10.7  | Advanced Memory Architecture (layered) | ✅ Must-have (partial)     | Phase 3, expand later          |
| 10.8  | Workflow Builder                       | 🚫 Future                  | Phase 8+                       |
| 10.9  | Knowledge Graph Layer                  | 🚫 Future                  | Phase 8+ (optional per tenant) |
| 10.10 | Widget as Independent Product          | ✅ Concept, scoped rollout | Phase 1, 3, 5, 7               |
| 10.11 | DDD Service Boundaries                 | 🚫 Future                  | When scaling demands           |

### 1.4 Pushbacks

**10.5 Plugin SDK** — MCP covers ~80% of integrations with zero code from us. A native plugin SDK doubles our surface area (maintenance, security review, versioning, lifecycle). Ship MCP first; add SDK only when customers demand capabilities MCP can't express.

**10.8 Workflow Builder** — Visual editor with conditional branches, approval nodes, and templates is a product on its own — months of work. It also fights against the agent-as-reasoner model. Defer until the agent model proves insufficient for a real customer.

**10.9 Knowledge Graph Layer** — Powerful for relationship-heavy domains, but most customer support is document-heavy. Build as an opt-in module per tenant, not core infrastructure.

**10.11 DDD Service Boundaries** — Classic distributed-monolith trap. Each service = its own DB + network hop + deployment cycle. Build a well-modularized monolith first, extract services when scaling demands it. The monorepo layout already enables this when the time comes.

---

## 2. Refined Architecture

```text
                          Website
                             │
                   Chat Widget Product
                   (configurable, themeable, extensible)
                             │
                       SSE/WebSocket
                             │
                      API Gateway + Auth
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
 Conversation Service    Rate Limiter       Event Bus ──┐
        │                                        │      │
        ▼                                        │      │
   ┌─────────────────────────────────────────┐   │      │
   │     Modular Agent Pipeline              │   │      │
   │     (each step = independent module)    │   │      │
   │                                         │   │      │
   │  ┌────────────┐  ┌─────────────┐         │   │      │
   │  │Preprocessor│→│Intent Class.│         │   │      │
   │  └────────────┘  └─────────────┘         │   │      │
   │         │                                │   │      │
   │         ▼                                │   │      │
   │  ┌────────────┐  ┌─────────────┐         │   │      │
   │  │  Planner   │→│  Reasoner   │         │   │      │
   │  └────────────┘  └─────────────┘         │   │      │
   │         │            │                   │   │      │
   │         ▼            ▼                   │   │      │
   │  ┌──────────┐  ┌──────────────┐          │   │      │
   │  │  Memory  │  │ Tool Executor│          │   │      │
   │  │  Layer   │  │ (MCP-first,  │          │   │      │
   │  │ Working  │  │  versioned)  │          │   │      │
   │  │ Convo    │  └──────────────┘          │   │      │
   │  │ Knowl.   │          │                 │   │      │
   │  └──────────┘          ▼                 │   │      │
   │                ┌──────────────┐          │   │      │
   │                │Postprocessor │          │   │      │
   │                └──────────────┘          │   │      │
   │                       │                 │   │      │
   │                       ▼                 │   │      │
   │              Streaming Response         │   │      │
   └─────────────────────────────────────────┘   │      │
        │           │            │              │      │
        ▼           ▼            ▼              ▼      ▼
   Redis       Qdrant       Postgres       Indexer  Analytics
  (cache,     (vectors,    (tenants,        │       │
   memory,    tenant-      convos,         │       ▼
   streams)   scoped)      prompts,        │   Audit, Billing
                              tools)        │
                                              │
                            ┌─────────────────┘
                            ▼
                   Model Router (OpenAI, Claude,
                   Gemini, Local, with failover)
                            │
                  Prompt Registry (versioned,
                  A/B testable, tenant-scoped)
```

---

## 3. Tech Stack

| Layer             | Choice                          | Notes                                                      |
| ----------------- | ------------------------------- | ---------------------------------------------------------- |
| Backend           | FastAPI                         | Native async, great SSE support                            |
| Agent             | LangGraph                       | Production-grade orchestration                             |
| Vector DB         | Qdrant                          | Multi-tenant via namespaced collections                    |
| Cache & Event Bus | Redis (Streams)                 | Cache + event bus + semantic cache + memory                |
| DB                | Postgres                        | With Row-Level Security                                    |
| Queue             | Celery + Redis Streams          | Async indexing + heavy work                                |
| Auth              | JWT + per-widget API keys       |                                                            |
| LLM providers     | OpenAI, Claude, Gemini, Local   | All behind `LLMProvider` interface, routed by Model Router |
| Embeddings        | text-embedding-3-large, BGE, E5 | Behind `EmbeddingProvider`                                 |
| Re-ranker         | Cohere Rerank / bge-reranker    | Quality boost on retrieval                                 |
| Guardrails        | Guardrails AI / NeMo            | PII + safety + injection                                   |
| RAG Eval          | RAGAS + custom golden set       | CI-evaluated on every PR                                   |
| Observability     | Langfuse                        | Tracing + cost + eval                                      |
| Widget            | Vanilla TS                      | Drop-in script for any site, <50KB gzipped                 |
| Dashboard         | Next.js + shadcn/ui             |                                                            |
| Deployment        | Docker → K8s                    | Docker Compose for dev                                     |
| Monorepo          | pnpm workspaces + uv            | Shared types between TS/Python                             |

---

## 4. Project Structure

```text
customer-support-platform/
├── apps/
│   ├── widget/              # JS chat widget (vanilla TS)
│   ├── dashboard/           # Next.js admin
│   └── api/                 # FastAPI backend (modular monolith)
│       ├── core/            # interfaces, DI, config
│       ├── conversation/    # session + history
│       ├── rag/             # loaders, chunkers, retriever, reranker
│       ├── agent/           # modular pipeline: preprocessor → intent → planner → retriever → reasoner → tool → composer → postprocessor
│       ├── tools/           # MCP client + tool registry (versioned)
│       ├── memory/          # layered memory (working/conversation/knowledge + later user/org/tool)
│       ├── prompts/         # prompt registry with versioning + A/B + rollback
│       ├── models/          # model router (LLM selection + failover)
│       ├── events/          # event bus + subscribers (analytics/billing/audit/indexer)
│       ├── tenants/         # multi-tenancy
│       ├── auth/            # JWT + API keys
│       ├── guardrails/      # PII + safety
│       ├── observability/   # tracing + metrics
│       └── billing/         # quotas + usage metering
├── packages/
│   ├── shared-types/        # TS types + Pydantic models (single source of truth)
│   ├── llm-providers/       # OpenAI, Claude, Gemini, Local adapters
│   ├── embedding-providers/ # OpenAI, BGE, E5
│   ├── vector-stores/       # Qdrant, Pinecone, Chroma
│   ├── document-loaders/    # PDF, web, Notion, GDrive
│   ├── tool-providers/      # MCP, REST, GraphQL (future: Plugin SDK)
│   └── memory-layers/       # WorkingMemory, ConversationMemory, KnowledgeMemory, ...
├── infra/
│   ├── docker-compose.yml   # Postgres, Redis, Qdrant, MinIO, Langfuse
│   ├── k8s/
│   └── terraform/
└── eval/
    ├── datasets/            # golden Q&A (multi-language, multi-vertical)
    ├── metrics/             # RAGAS + custom metrics
    └── runners/             # CI eval pipeline
```

---

## 5. Core Components Deep Dive

### 5.1 Event Bus (10.1)

**Why:** Decouple async work from the request path. Indexing, analytics, billing, audit, notifications — none of them should block user-facing latency.

**Tech evolution:** Redis Streams (Phase 0-2) → RabbitMQ (Phase 3+) → Kafka (only at large scale, if ever).

```text
Events Emitted:
- conversation.started
- conversation.ended
- message.received
- tool.called
- tool.failed
- doc.indexed
- doc.failed
- escalation.triggered
- quota.exceeded
- llm.failed

Subscribers:
- Indexer Service        ← doc.* events
- Analytics Service      ← conversation.* + message.*
- Billing Service        ← tool.called + token usage
- Audit Service          ← security-sensitive events
- Notifications Service  ← escalation.triggered, quota.exceeded
- Cache Invalidation     ← doc.indexed (per-tenant)
```

### 5.2 Modular Agent Pipeline (10.2)

Replace the linear `Planner → Retriever → Memory → Tool → Respond` with explicit stages. Each is independently testable, optimizable, and replaceable.

```text
User Input
    ↓
Preprocessor          (normalize, redact PII, detect language)
    ↓
Intent Classifier     (FAQ vs. complex vs. tool-needed vs. escalation)
    ↓
Planner               (decide which steps to run; can short-circuit FAQs)
    ↓
Retriever             (semantic-cache → RAG → rerank)
    ↓
Reasoner              (synthesize retrieved context with selected LLM via Model Router)
    ↓
Tool Executor         (MCP or hardcoded tools, versioned)
    ↓
Response Composer     (format final answer, citations, follow-ups)
    ↓
Postprocessor         (safety check, PII scrub, tone adjust)
    ↓
Streaming Response
```

**Benefits:**

- Preprocessor can be swapped per language or compliance regime.
- Intent Classifier enables fast paths (FAQ → small model, complex → large model).
- Reasoner can use different models per request type via Model Router.
- Postprocessor is a single point for safety guarantees.

### 5.3 Model Router (10.4)

A single `ModelRouter` interface that selects the LLM per request based on:

```text
Request          │  Model Selected
─────────────────┼──────────────────────────────
FAQ / classify   │  Small/fast (gpt-4o-mini, Haiku, Gemini Flash)
Customer support │  Mid-tier (gpt-4o, Sonnet)
Long reasoning   │  Top-tier (gpt-5, Opus)
Code generation  │  gpt-5 (or whatever's best)
Embedding        │  Dedicated embedding model
```

**Also handles:**

- Failover (primary down → secondary)
- Cost caps per tenant
- Per-tenant model preferences
- A/B testing different models

### 5.4 Prompt Registry (10.3)

Treat prompts as versioned, queryable assets:

```text
Prompt Metadata:
- id
- name (e.g., "customer_support.system")
- version
- status (draft / active / archived)
- tenant_id (null = global default)
- environment (dev / staging / prod)
- variables (list)
- content (template)
- created_by
- created_at
- metrics (latency, token usage, eval scores)
```

**Features:**

- Version every change
- Rollback to any prior version
- A/B test two versions in production
- Tenant-specific overrides
- Track eval metrics per version
- Auto-rollback if eval scores drop

**Storage:** Postgres table `prompt_versions`. Active version per (tenant, name, env) cached in Redis.

### 5.5 Tool Registry Versioning (10.6)

Extended from the original tool spec:

```text
Tool:
- name
- version
- description
- input_schema (JSON Schema)
- output_schema
- permissions (list of scopes)
- owner (tenant or global)
- health_status
- timeout_ms
- retry_policy
- rate_limit (per tenant, global)
- visibility (public / private / beta)
- deprecation_date (if any)
- changelog
```

**Why versioning matters:**

- Safe upgrades (run v2 alongside v1, migrate gradually).
- Compatibility tracking (which prompts/tools use which version).
- Auditability (who called what when).
- Deprecation flow (warn callers, then remove).

### 5.6 Layered Memory (10.7) — Rolled Out in Layers

Don't build all 6 memory layers on day 1. Roll them out as needed:

**Phase 3 — Core 3 layers:**

1. **Working Memory** — current turn's reasoning context (in-memory + Redis).
2. **Conversation Memory** — history + rolling summaries (Postgres + Redis).
3. **Knowledge Memory** — RAG-retrieved context (Qdrant).

**Phase 5+ — Add as needed:** 4. **User Memory** — preferences, language, timezone (Postgres per user). 5. **Organization Memory** — tenant policies, business rules (Postgres per tenant). 6. **Tool Memory** — execution history, cached results (Redis with TTL).

Each layer has a clear interface so adding the next one is non-breaking.

### 5.7 Widget as Independent Product (10.10)

Treat the widget as a standalone product with its own roadmap:

| Feature                                | Phase              |
| -------------------------------------- | ------------------ |
| Drop-in script, theme, position, color | Phase 1            |
| SSE streaming + typing indicators      | Phase 1            |
| File uploads                           | Phase 3            |
| Rich cards (buttons, carousels)        | Phase 3            |
| Localization (i18n strings)            | Phase 5            |
| Voice in/out                           | Phase 5 (optional) |
| White-label (custom domain, logo)      | Phase 6            |
| Session persistence + offline mode     | Phase 7            |
| Custom UI extensions (plugin slots)    | Phase 7+           |

**Non-negotiable from day 1:**

- Tiny bundle (<50KB gzipped).
- Zero external deps.
- WCAG AA accessibility.
- Works on any site (no React, no jQuery, no framework lock-in).

---

## 6. Phased Plan (8 Phases)

### Phase 0 — Foundation (Week 1-2)

**Exit criteria:** No production code, but the foundation is solid and the event bus is wired in.

- [ ] Monorepo setup (pnpm workspaces + uv for Python).
- [ ] Tooling: ruff, mypy, eslint, prettier, pre-commit.
- [ ] Docker Compose: Postgres, Redis, Qdrant, MinIO, Langfuse.
- [ ] Define all core interfaces:
  - `LLMProvider`
  - `EmbeddingProvider`
  - `VectorStore`
  - `DocumentLoader`
  - `ToolProvider`
  - `MemoryProvider`
  - `CacheProvider`
  - `EventBus`
- [ ] One working adapter per interface (OpenAI, Qdrant, Redis, PDF, MCP).
- [ ] Tenant schema in Postgres + RLS policies.
- [ ] **Redis Streams event bus** running with event catalog drafted.
- [ ] CI pipeline: lint + type-check + test.
- [ ] `.env.example` + secrets management.

---

### Phase 1 — Core Chat Engine + Model Router + Prompt Registry (Week 3-5)

**Exit criteria:** End-to-end chat works with streaming, model routing, versioned prompts, and event subscribers.

- [ ] FastAPI app with health/readiness probes.
- [ ] `POST /chat` + `GET /conversations/{id}`.
- [ ] **SSE streaming** for token-by-token responses.
- [ ] Conversation Manager (Postgres + Redis cache).
- [ ] **Chat Widget v1** (vanilla TS, drop-in script, theming).
- [ ] JWT auth + per-widget API keys.
- [ ] Rate limiting per tenant.
- [ ] Structured logging + request IDs.
- [ ] Error handling + graceful degradation.
- [ ] **Prompt Registry** (Postgres-backed, with versioning + tenant overrides + rollback).
- [ ] **Model Router** (interface + OpenAI/Claude/Gemini adapters + failover).
- [ ] **Event Bus subscribers** for Analytics, Billing, Audit.
- [ ] Eval harness skeleton + first 20 golden questions.

**Demo milestone:** Widget on a test page, LLM responds via streaming with model selection visible in traces.

---

### Phase 2 — RAG Engine (Week 6-9)

**Exit criteria:** Upload PDF → ask a question → answer cites the PDF. Eval pipeline green.

- [ ] Document Loaders: PDF, Markdown, HTML, Notion, Google Drive.
- [ ] Chunkers: Recursive, Semantic, Markdown.
- [ ] Embedding Pipeline (batched + async via Celery).
- [ ] Qdrant integration with **tenant-namespaced collections**.
- [ ] Retriever (hybrid: dense + BM25).
- [ ] **Re-ranker** (Cohere / bge-reranker).
- [ ] Background indexer (Celery workers + Redis Streams).
- [ ] **Eval pipeline using RAGAS** on a 50-question golden set, runs in CI.
- [ ] Doc versioning + invalidation hook (event-driven cache bust).
- [ ] Citations in response (which doc, which chunk).

**Demo milestone:** Upload a PDF, ask about it, answer includes citations and eval scores are green.

---

### Phase 3 — Agent Orchestration (Week 10-13)

**Exit criteria:** Agent decides when it needs docs/tools and acts correctly across all pipeline stages.

- [ ] **Modular Agent Pipeline**: Preprocessor → Intent → Planner → Retriever → Reasoner → Tool → Composer → Postprocessor.
- [ ] **Semantic Cache** between Question and Retriever.
- [ ] **Conversation Summarization** when history grows long (rolling summaries).
- [ ] **Guardrails**: PII detection, prompt injection, content safety.
- [ ] Function calling layer (tool spec → OpenAI tools format).
- [ ] **Tool Registry** with versioning, health, rate limits, visibility.
- [ ] **Layered Memory v1**: Working + Conversation + Knowledge.
- [ ] Hardcoded tools v1:
  - `create_ticket`
  - `escalate_human`
  - `get_faq`
  - `search_docs`
- [ ] Widget features: file uploads, rich cards.

**Demo milestone:** Agent uses `create_ticket` when user requests escalation; full trace visible in Langfuse.

---

### Phase 4 — MCP Integration (Week 14-16)

**Exit criteria:** Tenant provides an MCP server URL → tools appear automatically and execute correctly.

- [ ] MCP Client (stdio + HTTP transports).
- [ ] Tool Discovery (`list_tools`).
- [ ] Schema adapter (MCP JSON Schema → OpenAI tools format).
- [ ] Per-tenant MCP server registry.
- [ ] Auth tokens per MCP server (OAuth / API key).
- [ ] **Long-running tool execution** with progress events.
- [ ] Tool timeouts + retries + circuit breaker.
- [ ] Webhook receiver (for async tool results).
- [ ] Tool call audit log.

**Demo milestone:** Connect a Stripe MCP server → agent processes a refund without custom code.

---

### Phase 5 — Multi-Tenancy Hardening (Week 17-18)

**Exit criteria:** 3 separate tenants — fully isolated. Cost under control.

- [ ] Per-tenant config: LLM key, vector collection, MCP servers, prompts, branding.
- [ ] Postgres RLS enforcement on every query.
- [ ] Qdrant collection namespacing + API key scoping.
- [ ] Redis key prefixing per tenant.
- [ ] Per-tenant **cost quotas** (tokens/month, requests/day) enforced by Model Router + API gateway.
- [ ] Usage metering + billing events.
- [ ] Cold-start flow (new tenant with zero docs — sensible defaults).
- [ ] Tenant onboarding wizard.
- [ ] **User Memory + Organization Memory layers** added.
- [ ] Widget localization (i18n strings).
- [ ] RabbitMQ considered if Redis Streams shows limits.

**Demo milestone:** Tenant A cannot see Tenant B data even if they try; quotas enforced.

---

### Phase 6 — Admin Dashboard (Week 19-21)

**Exit criteria:** Customers manage their own account without contacting us.

- [ ] Next.js dashboard.
- [ ] Auth + tenant context.
- [ ] Pages:
  - Overview
  - Knowledge Base (upload + crawl)
  - Tools (MCP servers)
  - Conversations (viewer + tracing)
  - Analytics
  - Settings (LLM, prompts, branding)
  - API Keys
  - Billing & Usage
- [ ] Upload docs UI + website crawl wizard.
- [ ] Conversation viewer with full trace.
- [ ] Analytics: questions, latency, tool calls, escalation rate.
- [ ] **Prompt Registry UI** (create version, set active, A/B test, rollback).
- [ ] White-label widget config (theme, position, color, logo, custom domain).

**Demo milestone:** A company uploads docs, connects an MCP, manages prompts, watches live conversations.

---

### Phase 7 — Observability, Eval, Hardening (Week 22-24)

**Exit criteria:** Production-ready for pilot customers.

- [ ] Langfuse traces for every conversation + tool call + retrieval.
- [ ] Expanded eval set (200+ questions, multi-language).
- [ ] CI runs eval on every PR (regression guard).
- [ ] Cost dashboard (per tenant, per day).
- [ ] Alerts: token spike, error rate, retrieval null rate, latency p99.
- [ ] Security hardening:
  - Secrets vault
  - Encryption at rest
  - Audit log
  - Penetration test
- [ ] Load test: 100 concurrent conversations.
- [ ] Disaster recovery: DB backups, RPO/RTO documented.
- [ ] Widget session persistence + offline mode.
- [ ] Documentation:
  - API reference
  - Self-host guide
  - Integration guide
  - Admin guide

**Demo milestone:** One pilot customer live in production.

---

### Phase 8 — Pilot & Iterate (Week 25+)

- [ ] 2-3 design partners.
- [ ] Weekly feedback loop.
- [ ] Eval set grows based on real failures.
- [ ] Pricing tiers + Stripe billing.
- [ ] Marketing site.
- [ ] Status page.
- [ ] **Evaluate** whether to add any of the deferred items:
  - 10.5 Plugin SDK (if 5+ customers ask)
  - 10.8 Workflow Builder (if enterprise demands approval gates)
  - 10.9 Knowledge Graph (if a customer pays for KG-backed tier)
  - 10.11 Service extraction (if monolith becomes a bottleneck)

---

## 7. Decisions Needed Before Kickoff

| Question                | Recommended default                          | Why                                                      |
| ----------------------- | -------------------------------------------- | -------------------------------------------------------- |
| Backend language        | Python (FastAPI)                             | Best AI ecosystem, mature LangGraph support              |
| Widget framework        | Vanilla TS                                   | Drop-in script for any site, no React dep                |
| Streaming               | SSE                                          | Simpler than WebSocket, sufficient for chat              |
| Deployment model        | Self-hosted first, SaaS later                | Faster iteration early on                                |
| Multi-region from day 1 | No                                           | Single region + scale later                              |
| First pilot customer    | Someone with rich docs + existing MCP server | Proves the plug-and-play thesis                          |
| Event bus (initial)     | Redis Streams                                | Already in stack; swap to RabbitMQ if needed in Phase 5+ |
| Re-ranker               | Cohere Rerank                                | Faster to integrate; bge-reranker if cost-sensitive      |
| Eval (RAG)              | RAGAS                                        | De facto standard; supplement with custom metrics        |

---

## 8. Risks & Mitigations

| Risk                                       | Mitigation                                                                                    |
| ------------------------------------------ | --------------------------------------------------------------------------------------------- |
| LLM cost blowup                            | Per-tenant quotas + semantic cache + smaller models for simple queries (via Model Router)     |
| RAG quality complaints                     | Eval-driven dev + reranker + chunk quality metrics                                            |
| Vendor lock-in (OpenAI)                    | All providers behind interfaces; test with multiple from day 1; Model Router handles failover |
| MCP server instability                     | Circuit breaker + graceful degradation + hardcoded fallback tools                             |
| Tenant data leak                           | Postgres RLS + Qdrant namespacing + integration tests for isolation                           |
| Slow retrieval                             | Hybrid search + reranker + semantic cache + pre-warming popular queries                       |
| Long-running MCP calls blocking UI         | Async tool execution + webhook callbacks + UI progress                                        |
| Prompt regression on update                | Prompt Registry versioning + auto-rollback on eval score drop                                 |
| Model provider outage                      | Model Router failover (primary → secondary)                                                   |
| Over-engineering before product-market fit | Strict adherence to "build abstractions, defer implementations"                               |

---

## 9. Success Metrics

**At 3 months:**

- [ ] MVP live with 1 pilot customer.
- [ ] < 3s p95 first-token latency.
- [ ] > 60% deflection rate.
- [ ] RAGAS faithfulness > 0.75.

**At 6 months:**

- [ ] 10 paying tenants.
- [ ] < 2s p95 first-token latency.
- [ ] > 80% deflection rate (questions answered without human).
- [ ] < 5% escalation rate to human.
- [ ] RAGAS faithfulness > 0.85.
- [ ] Zero tenant data leaks.
- [ ] $X MRR (set your own target).

**At 12 months:**

- [ ] 50 paying tenants.
- [ ] Multi-vertical expansion (Sales or HR agent) validated.
- [ ] SOC 2 Type 1 (if enterprise target).
- [ ] Self-serve onboarding working end-to-end.

---

## 10. Open Questions

1. Multi-language support scope — UI + responses in N languages?
2. White-label pricing tiers — free, pro, enterprise?
3. On-prem deployment for enterprise?
4. SOC 2 timeline?
5. Data residency (EU vs US)?
6. First pilot customer — who?
7. Will the first vertical be pure customer support, or do you already have a Sales/HR pilot in mind?

---

## 11. Architectural Principle

> **Build abstractions, defer implementations.**

Every "future" item (Plugin SDK, Workflow Builder, Knowledge Graph, Service Boundaries) is preceded by an interface or module boundary in the MVP. That means when the time comes to add them, we don't rewrite the core — we plug them in.

The test of a good architecture is not how many features it has on day 1. It's how few features you'd need to remove if you had to rebuild from scratch.

The path to becoming a **Generic Enterprise AI Agent Platform** (not just Customer Support SaaS) is:

1. Build the core abstractions (LLM, Memory, Tools, Prompts, Events) for one vertical.
2. Prove product-market fit on that vertical.
3. Add verticals (Sales, HR, IT) by composing the same abstractions with vertical-specific prompts, tools, and eval sets.

We do **not** build for "any vertical" upfront — we build the foundations that make the next vertical a 2-week exercise instead of a 6-month rebuild.

---

_Document version: 2.0 — created 2026-07-01 (consolidated V1 + V2 Architectural Enhancements)_
