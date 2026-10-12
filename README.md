# Smart Medical Note Assistant

A local Streamlit milestone project that converts bulleted practitioner notes into a structured clinical draft while demonstrating secure LLM API integration, dynamic prompting, retry/error handling, and context-length safeguards.

## Milestone Requirements Covered

- Local Streamlit web app
- Bulleted practitioner-note input
- Structured clinical summary generation
- `.env`-based API-key management
- Retry and error handling
- Context-length safeguards
- Dynamic prompt construction
- Setup documentation
- Limitations documentation

## Real-World Problem

Practitioners often capture fast, fragmented bullet notes during or after an encounter. Turning those notes into a readable structured summary takes time and can introduce omissions.

This prototype demonstrates how an LLM can assist with drafting while preserving an important boundary: the model must not invent undocumented facts, diagnoses, medications, measurements, or plans.

The output is explicitly treated as a draft requiring practitioner review.

## Architecture

```text
Practitioner Bullet Notes
        ↓
Dynamic Prompt Builder
        ↓
Context Safety Analysis
        ↓
Safe Input / Truncation Safeguard
        ↓
LLM API Request
        ↓
Retry + Error Handling
        ↓
Structured Clinical Draft
        ↓
Practitioner Review Required
```

## Key Concepts

### Dynamic Prompting
The prompt changes according to runtime variables such as note type, audience/style, and practitioner notes.

### `.env` Key Management
Secrets are loaded from environment variables instead of being hardcoded in source code.

### Retry / Error Handling
Temporary failures such as HTTP 429, HTTP 500/502/503/504, timeouts, and connection failures are handled with controlled retries and exponential backoff with jitter.

### Context-Length Safeguards
The application estimates token usage before the request and reserves room for the system prompt, output, and safety margin.

If notes exceed the safe input budget, this milestone prototype truncates the input and displays a warning. In production, chunking or summarization is preferable when truncation could remove clinically important content.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

Then place your real key in `.env`:

```env
OPENROUTER_API_KEY=your_real_key
DEFAULT_MODEL=openrouter/free
```

## Suggested Demo Input

```text
- SOB for 2 days
- BP 150/95 mmHg
- CXR: RLL infiltrate
- Possible lower respiratory tract infection
- Follow-up advised in 48 hours
```

## Expected Output Sections

- Clinical Summary
- Key Findings
- Measurements
- Uncertainties
- Documented Plan / Next Steps
- Review Note

## Limitations

1. LLMs can produce incorrect, incomplete, or fabricated text.
2. Generated summaries require practitioner review.
3. The system must not be used as a diagnostic or treatment tool.
4. Use synthetic or properly de-identified data during development.
5. Simple truncation may remove important information from very long notes.
6. Model behavior can vary, particularly when using routed or free models.
7. This prototype does not provide EHR integration, audit trails, access control, or clinical compliance guarantees.
8. Real deployment would require stronger privacy, security, validation, observability, and governance controls.

## Learning Outcome

This milestone integrates secure configuration, prompt engineering, dynamic prompts, API requests, retry logic, network error handling, context-window management, Streamlit UI, safety-aware drafting, and technical documentation into one complete project.
