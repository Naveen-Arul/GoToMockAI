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
def run_interview_style_quiz(resume_json):
   
    """
    Builds a prompt to ask 5 personalized questions based on resume JSON.

    Args:
        resume_json (dict): Parsed resume JSON data.

    Returns:
        str: Formatted prompt string for Groq LLM.
    """
    prompt= f"""
        You are an AI interview assistant.

         Your goal is to create 5 personalized, thoughtful, and job-relevant interview questions based on the candidate's resume data.

        Output Format (MUST be valid JSON):
        {{
        "1": {{
            "Question": "",
            "Categoty": ""
        }},
        "2": {{
            "Question": "",
            "Categoty": ""
        }},
        "3": {{
            "Question": "",
            "Categoty": ""
        }},
        "4": {{
            "Question": "",
            "Categoty": ""
        }},
        "5": {{
            "Question": "",
            "Categoty": ""
        }}
        }}

        Guidelines:
        - Focus on experience, projects, skills, and achievements from the resume.
        - Do **not** include general or vague questions. Be specific to the candidate’s profile.
        - Use professional language.
        - Leave the "Answer" field blank for the candidate to fill in.

         Resume JSON:
        ```json
        {json.dumps(resume_json, indent=2)}
    """
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return extract_json(response.choices[0].message.content.strip())

