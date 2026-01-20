# Māyājāl  
**Synthetic Deception Infrastructure for Red-Team & Adversarial Simulation**

> *Māyājāl* (मायाजाल) — “the web of illusion” — is a research-driven platform for generating **believable, self-consistent synthetic digital environments** designed to withstand human and automated scrutiny.  
It sits at the intersection of **LLMs, cyber deception, honeypots, and red-team simulation**.

This repository currently hosts **two tightly coupled engines** that together form the foundation of a scalable deception ecosystem.

---

## 🧩 What Māyājāl Is 

Māyājāl is **not** a chatbot, assistant, or agent framework.

It is a **data-generation and behavioral-simulation system** whose sole purpose is to produce **realistic digital artifacts and terminal behavior** that look, feel, and fail like real systems — long enough to fool skilled humans.

Think:
- Fake corporate laptops
- Synthetic engineers with habits and mistakes
- Believable shell sessions
- Convincing internal clutter (logs, configs, commits, notes)
- Artifacts that *hold up under inspection*

---

## 🏗️ Core Components

### 1️⃣ Synthetic Artifact Generator (SAG)
*A persona-driven artifact factory*

From a **short natural-language persona description**, SAG generates **hundreds to thousands of coherent digital artifacts** that plausibly belong to a single human operating in a modern (≈2026) technical environment.

#### Examples of Generated Artifacts
- `.env` files with realistic but fake secrets
- Bash / Zsh histories (typos, retries, habits)
- Git commit logs & diffs
- JIRA-style tickets and comments
- SQL procedures
- React / TypeScript components
- Notes, TODOs, markdown docs
- Chrome extension configs
- Synthetic PII (emails, usernames, paths — all fake)

All artifacts:
- Share consistent usernames, emails, timestamps
- Reflect the same tech stack and seniority
- Contain human-like quirks and imperfections
- Avoid real credentials or real-world harm

---

### 2️⃣ Deception Engine (Shell Simulation)
*A behavioral realism layer*

The Deception Engine focuses on **interactive terminal behavior** — not command syntax, but **command output realism**.

Given a shell command, the model responds with output that resembles:
- A real Linux system
- Non-root permissions
- Partial pipelines
- Silent commands
- Realistic errors and failures

This enables:
- High-interaction honeypots
- Fake servers that “feel alive”
- Red-team training environments
- Malware / attacker behavior studies

---

## 🧠 Design Philosophy

### What We Optimize For
- **Believability over correctness**
- **Behavior over explanation**
- **Consistency over cleverness**
- **Evaluation over vibes**

### What We Explicitly Avoid
- Reasoning chains
- Chat-style responses
- Over-explaining
- Instruction-following
- Hard-coded procedural scripts

---

## ⚙️ Current Architecture (v0)

### Language & Runtime
- Python (prototype)
- Async-first design
- Minimal dependencies

### Models
- **Gemini family** (Flash for speed, Pro for quality ceiling)
- **Code-specialized LLMs** for shell realism (e.g. DeepSeek Coder)

---

### 🧱 Pipeline Overview

#### 1. Persona → Dense Context
A short persona description expands into:
- Role, seniority, company fiction
- Personality traits & flaws
- Tech stack choices
- Behavioral tells (habits, mistakes, preferences)

#### 2. Category-Specific Prompt Factories
Each artifact type has:
- Its own prompt template
- Few-shot realism anchors
- Anti-hallucination constraints
- Strict JSON schema instructions

#### 3. Structured Batch Generation
- Parallel async calls
- Batch sizes: 30–120 artifacts
- Temperature tuned for controlled variety
- Native JSON/schema enforcement

#### 4. Stateful SQLite Backbone
A single SQLite DB stores everything:
- Persona slug
- Artifact category
- Structured JSON blobs
- Metadata & timestamps

Before each generation batch:
- Relevant prior artifacts are queried
- Summaries are injected back into prompts
- Ensures cross-artifact coherence

#### 5. Validation & Persistence
- Schema validation
- Syntax checks (JS, SQL, YAML, Markdown)
- UUID + timestamp randomization
- Atomic writes only

---

### Human-Centric Evaluation

Blind reviews by domain experts:
- Believability score (0–5)
- “Would this fool me for 30–60 seconds?”
- Internal consistency judgments

Target:
> **≥ 4.0 / 5.0 realism under medium–high scrutiny**

---

## 🎯 Intended Use Cases

- High-interaction honeypots
- Red-team & blue-team training
- Insider-threat simulation
- Malware research sandboxes
- Deception research datasets
- Synthetic corpora for detection systems

---

## 🧪 Research Value

Māyājāl is intentionally scoped as a **pre-agentic foundation**.

Before building autonomous agents, we answer:
- What *looks real*?
- What breaks immersion?
- How do humans detect synthetic artifacts?
- Which prompt constraints matter?

This creates:
- A reusable benchmark for deception realism
- A testbed for prompt ablation studies
- Baselines for future agentic systems
- A bridge between frontier LLMs and practical deception tooling

---

## 🧬 Why “Māyājāl”?

Because deception isn’t about lying loudly —  
it’s about weaving a world just convincing enough that no one thinks to question it.

---

If you’re interested in:
- collaborating,
- stress-testing realism,
- or extending Māyājāl into agentic territory,

open an issue or start a discussion.

This project is intentionally opinionated — and that’s the point.
