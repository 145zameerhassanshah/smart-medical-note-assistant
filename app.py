import streamlit as st

from config import (
    APP_NAME,
    DEFAULT_MODEL,
    DEFAULT_CONTEXT_LIMIT,
    RESERVED_OUTPUT_TOKENS,
    SAFETY_MARGIN,
    validate_config,
)
from services.prompt_service import build_dynamic_prompt
from services.llm_service import send_chat_request
from utils.context_utils import analyze_context, truncate_to_tokens


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🩺",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 1.2rem 1.4rem;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        margin-bottom: 1rem;
    }
    .hero h1 { margin: 0; color: #0F172A; }
    .hero p { color: #64748B; margin-bottom: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "draft_result" not in st.session_state:
    st.session_state.draft_result = None

st.markdown(
    """
    <div class="hero">
        <h1>🩺 Smart Medical Note Assistant</h1>
        <p>
            Convert practitioner bullet notes into a structured clinical draft
            with context safeguards, dynamic prompting, retries, and explicit review warnings.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

config_errors = validate_config()

with st.sidebar:
    st.markdown("### Configuration")
    st.write(f"**Model:** `{DEFAULT_MODEL}`")

    if config_errors:
        for error in config_errors:
            st.error(error)
    else:
        st.success("API configuration ready")

    st.divider()
    st.markdown("### Safety")
    st.caption(
        "Use synthetic or de-identified notes only. "
        "Generated summaries are drafts and require practitioner review."
    )

left, right = st.columns([1.05, 0.95], gap="large")

with left:
    st.markdown("## Practitioner Notes")

    note_type = st.selectbox(
        "Note Type",
        [
            "General Clinical Note",
            "Progress Note",
            "Consultation Note",
            "Emergency Note",
            "Discharge Note",
        ],
    )

    audience = st.selectbox(
        "Draft Style",
        ["Clinician", "Patient-Friendly"],
    )

    practitioner_notes = st.text_area(
        "Bulleted Notes",
        value=(
            "- SOB for 2 days\n"
            "- BP 150/95 mmHg\n"
            "- CXR: RLL infiltrate\n"
            "- Possible lower respiratory tract infection\n"
            "- Follow-up advised in 48 hours"
        ),
        height=260,
        help="Use synthetic or de-identified information only.",
    )

    preview_col, generate_col, clear_col = st.columns(3)

    with preview_col:
        preview_clicked = st.button("Build Prompt", width="stretch")

    with generate_col:
        generate_clicked = st.button("Generate Draft", type="primary", width="stretch")

    with clear_col:
        clear_clicked = st.button("Clear", width="stretch")

    if clear_clicked:
        st.session_state.draft_result = None
        st.rerun()

    prompts = build_dynamic_prompt(
        practitioner_notes=practitioner_notes,
        note_type=note_type,
        audience=audience,
    )

    analysis = analyze_context(
        text=practitioner_notes,
        system_prompt=prompts["system_prompt"],
        context_limit=DEFAULT_CONTEXT_LIMIT,
        reserved_output_tokens=RESERVED_OUTPUT_TOKENS,
        safety_margin=SAFETY_MARGIN,
    )

    if preview_clicked:
        st.success("Dynamic prompt built successfully.")
        with st.expander("Generated System Prompt", expanded=True):
            st.code(prompts["system_prompt"], language="text")

    if generate_clicked:
        if config_errors:
            st.error("Fix API configuration before generating a draft.")
        elif not practitioner_notes.strip():
            st.warning("Enter practitioner notes first.")
        else:
            if analysis["status"] == "OVERFLOW":
                safe_notes = truncate_to_tokens(
                    practitioner_notes,
                    analysis["available_input_budget"],
                )
                st.warning(
                    "Input exceeded the safe context budget. "
                    "For this milestone demo, the note was truncated before the API request."
                )
            else:
                safe_notes = practitioner_notes

            safe_prompts = build_dynamic_prompt(
                practitioner_notes=safe_notes,
                note_type=note_type,
                audience=audience,
            )

            with st.spinner("Generating structured draft..."):
                st.session_state.draft_result = send_chat_request(
                    system_prompt=safe_prompts["system_prompt"],
                    user_prompt=safe_prompts["user_prompt"],
                )

with right:
    st.markdown("## Context Safety")

    m1, m2, m3 = st.columns(3)
    m1.metric("Input Tokens", analysis["input_tokens"])
    m2.metric("Available Budget", analysis["available_input_budget"])
    m3.metric("Status", analysis["status"])

    if analysis["status"] == "SAFE":
        st.success("Input is inside the safe context budget.")
    elif analysis["status"] == "WARNING":
        st.warning("Input is approaching the context limit.")
    else:
        st.error(
            f"Input exceeds the safe budget by {analysis['overflow_tokens']} tokens."
        )

    with st.expander("View Dynamic Prompt"):
        st.code(prompts["system_prompt"], language="text")

    st.markdown("## Generated Draft")
    result = st.session_state.draft_result

    if not result:
        st.info("Generate a draft to see the structured summary here.")
    elif not result["success"]:
        st.error(f"Generation failed at stage: `{result['stage']}`")
        st.code(result["error"], language="text")
    else:
        st.success("Draft generated successfully.")
        st.markdown(result["content"])
        st.warning(
            "AI-generated draft: practitioner review is required before use."
        )

st.divider()
st.caption(
    "Educational prototype only. "
    "Do not use as a substitute for clinical judgment or a verified medical record."
)
