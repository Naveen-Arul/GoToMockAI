import json
import re
import os
from groq import Groq
from pdfminer.high_level import extract_text
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise EnvironmentError("GROQ_API_KEY not set.")


client = Groq(api_key=API_KEY)
def extract_resume_text(pdf_path):
    """
    Extracts text content from a PDF resume.

    Args:
        pdf_path (str): Path to the resume PDF.

    Returns:
        str: Extracted raw text from the PDF.
    """
    return extract_text(pdf_path)

def build_prompt(text):
    """
    Builds a detailed and structured prompt for the LLM to extract resume data.

    Args:
        text (str): Raw text extracted from the PDF.

    Returns:
        str: Formatted prompt string.
    """
    return f"""
You are an expert resume parser AI.

Your task is to extract *structured JSON* from the resume below.

---

 Guidelines:
1. Extract all core sections:
   - name, email, phone
   - education (college and school)
   - projects
   - experience
   - skills
   - certifications
   - objective
   - links (linkedin, github, leetcode)
   - achievements (awards, recognitions, notable accomplishments)

2. In the "education" section:
   - Group entries by "institution"
   - Even if multiple levels (SSLC, HSC, B.Tech) exist for the same institution, merge them into one entry.
   - Put "level", "degree", "duration", and "grades_or_cgpa" inside a "details" array under each institution.
   - Do *not* repeat the same institution in separate objects.

3. Return *only valid JSON* with no extra text, headers, markdown, or explanations.
4. Only include fields that are present and non-empty in the resume.
5. Maintain case (uppercase/lowercase) as seen in the resume where it makes sense.
6. If there is more than one experience create an array to store all
7. If no experience is labeled, infer internships or freelance work based on description.

---

📄 Resume:
\"\"\"
{text}
\"\"\"

---

🎯 Required Output Format:
{{
  "name": "",
  "email": "",
  "phone": "",
  "education": [
    {{
      "institution": "",
      "details": [
        {{
          "level": "",
          "degree": "",
          "duration": "",
          "grades_or_cgpa": ""
        }}
      ]
    }}
  ],
  "projects": [
    {{
      "name": "",
      "description": ""
    }}
  ],
   "experience": [
    {{
      "title": "",
      "company": "",
      "duration": "",
      "description": ""
    }}],
  "skills": [],
  "certifications": [],
  "objective": "",
  "achievements": [],
  "links": {{
    "linkedin": "",
    "github": "",
    "leetcode": ""
  }}
}}
"""

def call_groq(prompt):
    """
    Sends prompt to Groq API and returns the model response.

    Args:
        prompt (str): The prompt to send to Groq's LLM.

    Returns:
        str: Raw model output containing JSON.
    """
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content
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
def remove_empty_fields(data):
    """
    Recursively removes keys with empty values.

    Args:
        data (dict or list): Parsed JSON.

    Returns:
        dict or list: Cleaned JSON with non-empty values.
    """
    if isinstance(data, dict):
        return {
            k: remove_empty_fields(v)
            for k, v in data.items()
            if v not in ("", [], {}, None)
        }
    elif isinstance(data, list):
        return [remove_empty_fields(item) for item in data if item not in ("", [], {}, None)]
    else:
        return data
def save_to_json(data, pdf_path):
    """
    Saves the JSON output next to the original PDF.

    Args:
        data (dict): Cleaned JSON data.
        pdf_path (str): Original resume path.
    """
    base = os.path.splitext(pdf_path)[0]
    json_path = base + "_parsed.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"✅ JSON saved to: {json_path}")


def Resume(pdf_path):
    raw_text = extract_resume_text(pdf_path)
    prompt = build_prompt(raw_text)
    raw_output = call_groq(prompt)
    parsed_json = extract_json(raw_output)
    cleaned_json = remove_empty_fields(parsed_json)
    return cleaned_json
