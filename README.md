<div align="center">
  <h1>Archssistant</h1>
  <p><em>A conversational assistant for explainable, transparent, and traceable software architecture decisions.</em></p>
  <p>
    <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"></a>
    <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript"><img src="https://img.shields.io/badge/JavaScript-Frontend-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript"></a>
    <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
    <a href="https://www.docker.com"><img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"></a>
    <a href="https://platform.deepseek.com"><img src="https://img.shields.io/badge/DeepSeek-LLM-4D6BFE?style=for-the-badge" alt="DeepSeek"></a>
  </p>
  <p>
    <a href="#need-and-motivation">Need and Motivation</a> ·
    <a href="#capabilities">Capabilities</a> ·
    <a href="#architecture-components">Architecture Components</a> ·
    <a href="#setup">Setup</a> ·
    <a href="#prompts-and-traceability">Prompts and Traceability</a>
  </p>
</div>

---
## Need and Motivation

LLM-based conversational recommenders commonly improve interaction quality, but they often become difficult to audit when the LLM is responsible for multiple roles (dialogue management, interpretation, and sometimes recommendation). This prototype targets that gap by isolating the **decision mechanism** into a deterministic, inspectable component while keeping the LLM limited to **interpreting user inputs**, **asking clarifying questions**, and **producing explanations grounded on the deterministic output**.

> [!CAUTION]
> This is a **research prototype**.

---
## Capabilities

| Capability                                                                 | Status |
| -------------------------------------------------------------------------- | ------ |
| **Multi-turn interaction orchestration (state machine)**                   | ✅     |
| **Deterministic recommendation (decision table / scoring / ranking)**      | ✅     |
| **Explicit Decision Model (explicit architecture catalog)**               | ✅     |
| **LLM elicitation: interpret user answers into predefined criteria**       | ✅     |
| **LLM elicitation: ambiguity detection + clarification question generation** | ✅   |
| **LLM explanation: natural-language justification grounded on decision output** | ✅ |
| **Prompted workflow (prompt templates versioned in-repo)**                 | ✅     |
| **Token/context optimization (avoid re-sending long histories)**           | ❌     |
| **Evaluation metrics for explanation quality and auditability**            | ❌     |
| **Long-term conversation memory with traceable persistence (no re-sending context)** | ❌ |

> [!NOTE]
> The prototype produces explanations grounded on deterministic outputs, but it currently lacks a standardized evaluation layer to quantify explanation quality (e.g., faithfulness, completeness) and auditability (e.g., trace reconstruction accuracy).

---
## Architecture Components

- **UI (chat)**: user entry point (frontend).
- **Orchestrator**: central coordinator of the interaction flow and component exchanges.
- **Elicitation Machine (LLM)**: receives elicitation requests and returns inferred criteria.
- **Explicit Decision Model**: receives inferred criteria and returns a decision table.
- **Decision Maker (deterministic)**: receives a recommendation request plus decision table, and returns recommendation plus decision table.
- **Recommendation Explainer (LLM)**: receives recommendation plus decision table, and returns recommendation plus LLM explanation.

> [!CAUTION]
> The LLM must remain **non-decisional**. Any prompt or integration change that lets the LLM alter ranking undermines auditability.

![Component Architecture with Interaction Flow](docs/Components-Flow.png)

> [!NOTE]
> Components marked with ⊗ are LLM-based and are restricted to elicitation and explanation (not decision making).

---
## Setup

From the repository root, create `.env`, set `DEEPSEEK_API_KEY`, and optionally adjust `LOG_LEVEL`:

```bash
cp .env.example .env
# edit .env and replace DEEPSEEK_API_KEY
docker compose up --build
```

Relevant `.env` values:

```bash
LOG_LEVEL=DEBUG  # INFO / WARNING / ERROR / CRITICAL
HOST=0.0.0.0
PORT=5000
DEEPSEEK_API_KEY=sk-your-key-here
```

---
## Prompts and Traceability

Prompt templates are stored under:

* `archssistant-backend/app/services/elicitation_machine/prompt/`

These prompts are treated as **versioned behavioral artifacts** (Git history = traceability). The current prompt set enforces **strict JSON-only outputs** to keep the pipeline deterministic and auditable.

* `interpret_user_answer_prompt.txt`
  Classifies a user answer for a given parameter (e.g., `scalability`, `teamSize`) and returns:

  * `classification` (or `UNCERTAIN`)
  * `confidence` (`high|medium|low`)
  * a short `reasoning` string

* `generate_next_question_prompt.txt`
  Produces the next conversational turn. It supports:

  * **clarification mode** when `isClarificationNeeded=true`
  * **normal flow** when `isClarificationNeeded=false`
    Output is a JSON contract including `parameter_to_infer`, `question_for_user`, and `full_response_text`.

* `generate_final_descriptions_prompt.txt`
  Generates final architecture descriptions and justifications grounded on:

  * `{project_description}`
  * `{conversation_history}`
  * `{recommendations_names}`
    Output is a JSON object whose keys must match architecture names exactly.
