# Model Classes Reference

| Class | Role | Implementation Status | Notes |
|---|---|---|---|
| **LLM** | Reasoning, conversation, planning, coding | Implemented | Cloud (OpenAI) preferred, local (Qwen, Llama, Gemma) fallback via `transformers` |
| **LAM** | Desktop action execution | Implemented | Routes through MCP `browser` and `input_injection` servers; never raw OS access |
| **MoE Router** | Model/tool router | Implemented | Keyword-based local triage + cloud routing; extensible |
| **VLM** | Screen understanding, OCR, GUI automation | Implemented | Uses OpenAI GPT-4o vision API for OCR and screen analysis |
| **SLM** | Small local model for fast commands | Implemented | Always-warm keyword fallback + local LLM with 2s timeout |
| **SAM** | Segment Anything — advanced CV | Implemented with fallback | Falls back to full-image bbox when `segment_anything` package is unavailable |
| **MLM** | Masked LM — embeddings, classification | Placeholder | Declared in registry; dense vector store deferred to Phase 3 RAG extension |
| **LCM** | Latent Consistency Model — fast image gen | Placeholder | Declared in registry; creative-tier generation deferred |
