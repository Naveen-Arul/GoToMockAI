from groq import Groq
import re
import os
from dotenv import load_dotenv
from dotenv import load_dotenv
import json

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise EnvironmentError("GROQ_API_KEY not set.")


client = Groq(api_key=API_KEY)
def extract_json(text):
    """
    Extracts JSON string from LLM response using regex.

    Args:
        text (str): Raw text from LLM response.

    Returns:
        dict: Parsed JSON object.
    """
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return json.loads(match.group(0))
    else:
        raise ValueError("No valid JSON found in the response.")
def Answer(question, resume_json):
    """
    Builds a prompt for Groq to answer interview questions using the resume JSON.

    Args:
        question (dict): JSON with questions.
        resume_json (dict): Parsed resume data.

    Returns:
        str: Prompt for Groq LLM to return filled answers in JSON format.
    """
    prompt = f"""
    You are an AI job applicant. Your task is to answer the following interview questions.

    **Constraint: You MUST base your answers *only* on the information provided in the Resume JSON below. Do not invent new skills, projects, or experiences.**

    The goal is to generate realistic answers that this specific candidate could give.

    ---
    **Resume JSON:**
    ```json
    {json.dumps(resume_json, indent=2)}
    ```
    ---
    **Interview Questions:**
    ```json
    {json.dumps(question, indent=2)}
    ```
    ---

    **Output Format (MUST be valid JSON):**
    Provide answers for the questions in the same JSON structure. Each answer should be 2-4 sentences.
    """
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return extract_json(response.choices[0].message.content.strip())