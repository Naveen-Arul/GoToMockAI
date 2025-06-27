from groq import Groq
import re
import os
from dotenv import load_dotenv
import json

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise EnvironmentError("GROQ_API_KEY not set.")


client = Groq(api_key=API_KEY)
def extract_json(text):
    """
    You are a strict technical evaluator.

The question is:
"{question}"

Ideal Answer:
\"\"\"{ideal_answer}\"\"\"

User Answer:
\"\"\"{user_answer}\"\"\"

Evaluate:
- If the user answered the question and their response aligns with the ideal answer in a correct and relevant way, award **2 marks**.
- If the user did not answer the question or the answer is incorrect, award **0 marks**.

Output strictly in the following JSON format:
{{
  "Score": int,  // 0 or 2 only
  "Feedback": "Your short feedback here"
}}
"""
    
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return json.loads(match.group(0))
    else:
        raise ValueError("No valid JSON found in the response.")
def evaluate_ans(user_answers, llm_answers):
    """
    Evaluates user's answers against LLM-generated ideal answers on a per-question basis.

    Args:
        user_answers (dict): A dictionary of the user's answers.
        llm_answers (dict): A dictionary of the ideal answers.

    Returns:
        dict: A dictionary containing detailed evaluation feedback.
    """
    question_evaluations = []
    total_score = 0

    for q_num in user_answers:
        if q_num not in llm_answers:
            continue

        question = user_answers[q_num]['Question']
        user_ans = user_answers[q_num]['Answer']
        llm_ans = llm_answers[q_num]['Answer']

        prompt = f"""
You are a strict but fair AI interviewer providing detailed feedback.
Evaluate the user's answer based on the provided ideal answer and the original question.

---
**Question:**
"{question}"

**Ideal Answer:**
"{llm_ans}"

**User's Answer:**
"{user_ans}"
---

**Evaluation Criteria:**
1.  **Relevance & Correctness:** Is the answer on-topic and factually correct?
2.  **Completeness:** Does the answer address all parts of the question?
3.  **Clarity:** Is the answer clear and well-explained?

**Task:**
Provide a `Status`, `Feedback` and a `Score`.
-   **Status:** Choose one: "Correct", "Incomplete", or "Incorrect".
-   **Feedback:** Provide a concise, one-sentence explanation for the assigned status.
-   **Score:** Assign a score of 2 for "Correct", 1 for "Incomplete", and 0 for "Incorrect".

**Output MUST be in the following JSON format:**
{{
    "Status": "...",
    "Feedback": "...",
    "Score": 0
}}
"""
        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"},
            )
            eval_result = json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, IndexError, TypeError):
            eval_result = {"Status": "Error", "Feedback": "Failed to evaluate this answer.", "Score": 0}

        question_evaluations.append({
            "QuestionNumber": q_num,
            "Question": question,
            "YourAnswer": user_ans,
            "Status": eval_result.get("Status", "Error"),
            "Feedback": eval_result.get("Feedback", "Evaluation failed.")
        })
        total_score += eval_result.get("Score", 0)

    num_questions = len(user_answers)
    overall_score_percent = (total_score / (num_questions * 2)) * 10 if num_questions > 0 else 0
    summary_for_feedback = "\\n".join([f"Q{item['QuestionNumber']}: {item['Status']} - {item['Feedback']}" for item in question_evaluations])

    overall_feedback_prompt = f"""
You are an AI career coach summarizing an interview performance.
Based on the following question-by-question evaluation, provide a concise, encouraging, and constructive overall feedback summary.

**Evaluation Summary:**
{summary_for_feedback}

**Task:**
Write a 1-2 sentence overall feedback summary.

**Output MUST be in the following JSON format:**
{{ "OverallFeedback": "..." }}
"""
    try:
        feedback_response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": overall_feedback_prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        overall_feedback_json = json.loads(feedback_response.choices[0].message.content)
        overall_feedback = overall_feedback_json.get("OverallFeedback", "No overall feedback.")
    except (json.JSONDecodeError, IndexError, TypeError):
        overall_feedback = "Could not generate an overall feedback summary."

    return {
        "OverallScore": round(overall_score_percent, 1),
        "OverallFeedback": overall_feedback,
        "QuestionEvaluations": question_evaluations
    }
