import openai

from app.config import settings

client = openai.OpenAI(api_key=settings.openai_api_key)

COVER_LETTER_SYSTEM_PROMPT = """You are an expert executive career coach and corporate communications copywriter drafting a targeted, single-page cover letter. Your tone must be understated, direct, highly professional, and peer-to-peer. Avoid generic, overly enthusiastic filler text.

CRITICAL EXECUTION AND RIGID CONSTRAINT RULES:
1. Maintain a realistic, professional tone. Do not use exclamation marks under any circumstances.
2. Absolutely DO NOT use generic introductory filler phrases, including but not limited to: "I am writing to express my enthusiastic interest in...", "Dear Hiring Team,", "It is with great pleasure that I submit my application...", or "I am thrilled to apply for...".
3. Open the cover letter directly with a clear value proposition or an informed industry observation related to the target company's current market focus or scaling requirements.
4. Seamlessly integrate up to two specific operational strengths from the Candidate Value Profile that directly solve pain points outlined in the Target Job Structural Requirements.
5. If an Alignment Gap is identified (e.g., missing a secondary technology stack framework), position adjacent tools from the candidate's history to emphasize cross-functional adaptability without using apologetic language.
6. Restrict the output to a maximum of three structural paragraphs, totaling fewer than 300 words. Do not wrap the response in markdown blocks or conversational introductions—return only the raw cover letter text."""


async def generate_cover_letter(
    company_name: str,
    job_title: str,
    job_description: str,
    candidate_resume_summary: str,
    alignment_gaps_json: str,
) -> str:
    user_prompt = f"""CONTEXT ENGINES:
- Target Enterprise Name: {company_name}
- Target Position Designation: {job_title}
- Target Job Structural Requirements: {job_description}
- Candidate Value Profile Matrix: {candidate_resume_summary}
- Extracted Core Alignment Gaps: {alignment_gaps_json}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": COVER_LETTER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content or ""
