# 🧠 Idea Pressure Tester — System Brain & Architecture Notes

> **Purpose:** Internal architecture specification, decision logs, prompting strategies, and engineering insights for the **Idea Pressure Tester** project.

---

## 🎯 1. Mission & Vision

Startups and product concepts frequently fail due to unexamined assumptions or echo-chamber validation. Traditional LLM brainstorming tends to be overly agreeable ("sycophantic").

**Idea Pressure Tester** solves this by decomposing evaluation into **adversarial and analytical personas** alongside real-time market discovery, simulating a diverse advisory board before writing a single line of code.

---

## 🏛️ 2. Core Architecture & Component Map

```
idea-pressure-tester/
├── src/
│   ├── app.py             # Presentation Layer: Streamlit UI, State Management, Teach Mode
│   └── main.py            # Logic Layer: AI Clients, Multi-threaded Execution, Fallback Strategies
├── .env.example           # Environment template (Gemini / OpenAI)
├── .gitignore             # Credential & cache exclusions
├── brain.md               # Engineering & architectural memory (This Document)
├── LICENSE                # MIT License
├── README.md              # Public documentation
└── requirements.txt       # Production dependencies
```

### Component Breakdown
1. **[`src/main.py`](file:///d:/Projects/idea-pressure-tester/src/main.py)**:
   - Contains persona system instructions and prompt formatting.
   - Encapsulates network communication with LLM providers (**Google Gemini** and **OpenAI**).
   - Exposes `get_persona_reactions(idea)` and `get_web_search_summary(idea)`.
   - Offers `analyze_idea_concurrently(idea)` leveraging Python's `concurrent.futures.ThreadPoolExecutor` for parallel execution.
   - Preserves `if __name__ == "__main__":` for standalone terminal CLI execution.

2. **[`src/app.py`](file:///d:/Projects/idea-pressure-tester/src/app.py)**:
   - Reactive Streamlit application.
   - Session state management for pre-filled idea templates.
   - Color-coded 2x2 presentation grid (`Customer`, `Investor`, `Competitor`, `Skeptic`).
   - Educational **Teach Mode** exposing system prompt, raw JSON schema, and search parameters.
   - Response caching via `@st.cache_data`.

---

## 👥 3. Persona Design & Prompt Engineering

The system prompt enforces a zero-shot, multi-persona panel returning **strictly valid JSON** with no markdown fences or preambles:

```json
{
  "investor": "string (2-3 sentences)",
  "skeptic": "string (2-3 sentences)",
  "customer": "string (2-3 sentences)",
  "competitor": "string (2-3 sentences)"
}
```

### Behavioral Directives:
- **Investor (Green / Success):** Focuses on TAM (Total Addressable Market), scalability, recurring revenue, and exit potential.
- **Skeptic (Red / Error):** Targets fatal failure modes, CAC (Customer Acquisition Cost) traps, regulatory/legal risks, and user churn.
- **Customer (Blue / Info):** Assesses real-world daily utility, switching costs, and willingness to pay.
- **Competitor (Yellow / Warning):** Assesses moats, barriers to entry, and incumbent retaliation tactics.

---

## ⚡ 4. Engineering Learnings & Performance Optimizations

### A. The Windows TLS Handshake Bottleneck
- **Symptom:** The default `google-genai` Python SDK (which relies on `httpx` + `httpcore`) suffered from connection handshake timeouts (`_ssl.c:993: The handshake operation timed out`) on certain Windows network configurations.
- **Root Cause:** HTTP/2 ALPN negotiation stalls on Windows with specific ISP/proxy routing.
- **Resolution:** Replaced the SDK's internal client with a direct, lightweight HTTP/1.1 REST implementation using `requests`. Latency dropped from **>30s timeout** to **~1.8s**.

### B. Parallel Execution
- **Symptom:** Sequentially chaining persona generation ($t_1$) and competitor analysis ($t_2$) created perceived lag ($t_1 + t_2 \approx 15-20s$).
- **Resolution:** Implemented `ThreadPoolExecutor(max_workers=2)` in `analyze_idea_concurrently()`. Both calls run concurrently, reducing wait time to $\max(t_1, t_2) \approx 3-5s$.

### C. 429 Quota Exhaustion & Graceful Degradation
- **Symptom:** Google Search Grounding tools trigger strict rate limits (`429 RESOURCE_EXHAUSTED`) on free-tier API keys.
- **Resolution:** Implemented automatic error-catching. When 429 or tool limits are encountered, the engine seamlessly queries Gemini's vast internal market knowledge base to identify competitors without throwing a fatal exception to the user.

### D. Streamlit Session State Lifecycle
- **Symptom:** `StreamlitWidgetAlreadyInstantiatedError` occurs if `st.session_state["idea_input"]` is modified after `st.text_area(key="idea_input")` is created.
- **Resolution:** Controlled reset flags (`reset_requested`) handled at the very top of `app.py` before any widget instantiation, ensuring 100% crash-free state resets.

---

## 🎓 5. Teach Mode Specification

Teach Mode demystifies generative AI design patterns for developers and students:
1. **Role Prompting**: Shows how persona instructions shape specialized tone and perspective.
2. **Structured Output**: Shows how `response_mime_type="application/json"` guarantees parseable outputs.
3. **Tool & Model Telemetry**: Inspects the exact query payload sent to market analysis models.

---

## 🔮 6. Future Roadmap

- [ ] **Export to PDF / Notion**: Download a 1-page executive summary of the pressure test.
- [ ] **Founder Rebuttal**: Allow the user to challenge the Skeptic or Investor in an interactive chat session.
- [ ] **Pitch Deck Score**: Generate a quantitative 1–100 viability score across TAM, Defensibility, and Feasibility.
