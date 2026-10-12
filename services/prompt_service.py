from typing import Dict

NOTE_TYPE_INSTRUCTIONS = {
    "General Clinical Note": "Organize the note into a concise clinical summary using only documented facts.",
    "Progress Note": "Emphasize interval changes, symptoms, observations, measurements, and documented assessment.",
    "Consultation Note": "Emphasize reason for consultation, key findings, documented impression, and documented recommendations.",
    "Emergency Note": "Emphasize presenting concern, urgent findings, measurements, and documented uncertainty.",
    "Discharge Note": "Emphasize reason for care, important findings, course, and documented discharge-related information.",
}

AUDIENCE_INSTRUCTIONS = {
    "Clinician": "Use concise professional clinical language.",
    "Patient-Friendly": "Use plain language and explain unavoidable medical terms briefly.",
}


def build_dynamic_prompt(practitioner_notes: str, note_type: str, audience: str) -> Dict[str, str]:
    note_instruction = NOTE_TYPE_INSTRUCTIONS[note_type]
    audience_instruction = AUDIENCE_INSTRUCTIONS[audience]

    system_prompt = f"""
You are a medical note drafting assistant.

Your job is to convert practitioner bullet notes into a structured draft summary.

NOTE TYPE
{note_type}

NOTE-SPECIFIC INSTRUCTION
{note_instruction}

AUDIENCE
{audience}

AUDIENCE INSTRUCTION
{audience_instruction}

SAFETY AND FIDELITY RULES
- Use only information explicitly present in the practitioner notes.
- Do not invent diagnoses, medications, findings, plans, or measurements.
- Preserve uncertainty words such as "possible", "suspected", and "rule out".
- Preserve important measurements and time durations.
- If information is missing, do not guess.
- This is a draft for review, not a final medical record.
- Do not provide treatment recommendations beyond what is documented.

OUTPUT FORMAT
Return the following sections using Markdown headings:

## Clinical Summary
A concise paragraph summarizing the documented note.

## Key Findings
Bullet points of important documented findings.

## Measurements
Bullet points for vitals, lab values, or other documented measurements. If none, write "Not documented."

## Uncertainties
Bullet points for possible/suspected/rule-out items. If none, write "None documented."

## Documented Plan / Next Steps
Only include actions explicitly present in the practitioner notes. If none, write "Not documented."

## Review Note
State that this is an AI-generated draft requiring practitioner review.
""".strip()

    user_prompt = f"""
Convert the following practitioner bullet notes into the required structured draft.

PRACTITIONER NOTES
{practitioner_notes}
""".strip()

    return {"system_prompt": system_prompt, "user_prompt": user_prompt}
