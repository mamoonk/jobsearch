import json

import openai

from app.config import settings

client = openai.OpenAI(api_key=settings.openai_api_key)

INTERVIEW_PREP_SYSTEM_PROMPT = """You are a principal technical interviewer and director of talent evaluation at the target company, conducting a screening loop for the specified role. Analyze the candidate's profile metrics alongside the target role requirements to generate an interactive interview preparation guide.

OUTPUT SPECIFICATION RULES:
You must return a valid, unencapsulated JSON array containing exactly 5 structured data items. Each object in the array must include the following keys:
- "question_type": Must use either "Behavioral (STAR Method)" or "Technical Defense Vector".
- "targeted_skill": The explicit core capability, framework, or operational pattern under review.
- "interview_question": The literal question string the interviewer will present during the screening call.
- "strategic_intent": The underlying rationale explaining why this question targets a gap in the candidate's experience.
- "optimal_response_script": A complete response template utilizing the STAR method (Situation, Task, Action, Result) or a technical defense framework, demonstrating how the candidate can pivot using adjacent competencies.

If the alignment gap log indicates the candidate lacks a specific tool required for the role, design a "Technical Defense Vector" question. This question should require the candidate to explain their understanding of the underlying system architecture by drawing parallels to structural tools they have already mastered."""


async def generate_interview_prep(
    job_title: str,
    job_description: str,
    candidate_resume_summary: str,
    alignment_gaps_json: str,
) -> list:
    user_prompt = f"""INPUT VARIABLES:
- Job Description Parameters: {job_description}
- Candidate Profile Data: {candidate_resume_summary}
- Alignment Engine Gaps Log: {alignment_gaps_json}

OUTPUT:
Return only a valid JSON array with exactly 5 question objects."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": INTERVIEW_PREP_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
    )
    content = response.choices[0].message.content or "[]"
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return []
