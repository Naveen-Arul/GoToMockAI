import uuid
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Dict

from GotoMock import resume, question, answer, evaluate

app = FastAPI(
    title="GotoMock API",
    description="An API to conduct an AI-powered mock interview based on a resume.",
    version="1.0.0"
)

# In-memory storage for interview sessions.

interview_sessions = {}

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

class UserAnswers(BaseModel):
    answers: Dict[str, str]

@app.post("/interview/start", summary="Start a new interview session")
async def start_interview(resume_file: UploadFile = File(..., description="The candidate's resume in PDF format.")):
    """
    Upload a resume to start a new mock interview.

    This endpoint will:
    1. Process the uploaded PDF resume.
    2. Generate personalized interview questions.
    3. Generate ideal answers based on the resume.
    4. Create a unique session ID for the interview.

    Returns the session ID and the generated questions.
    """
    if resume_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    # Save the uploaded file temporarily to be processed by the existing logic
    temp_file_path = f"_temp_{resume_file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await resume_file.read())

    try:
        # Core logic from the existing scripts
        resume_data = resume.Resume(temp_file_path)
        if not resume_data:
            raise HTTPException(status_code=422, detail="Failed to parse resume. The PDF might be empty or corrupted.")

        questions = question.run_interview_style_quiz(resume_data)
        ideal_answers = answer.Answer(questions, resume_data)

        # Create a new session
        session_id = str(uuid.uuid4())
        interview_sessions[session_id] = {
            "questions": questions,
            "ideal_answers": ideal_answers
        }

        return {
            "interview_id": session_id,
            "questions": questions
        }
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.post("/interview/{interview_id}/submit", summary="Submit answers and get evaluation")
async def submit_answers(interview_id: str, user_answers: UserAnswers):
    """
    Submit your answers for the interview questions and receive a detailed evaluation.

    This endpoint will:
    1. Retrieve the session data using the `interview_id`.
    2. Compare your answers against the ideal answers.
    3. Return a detailed, question-by-question evaluation.
    """
    if interview_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    session_data = interview_sessions[interview_id]
    ideal_answers = session_data["ideal_answers"]

    # The user_answers model is {"answers": {"1": "...", "2": "..."}}
    # The evaluation function expects {"1": {"Question": "...", "Answer": "..."}, ...}
    # We need to format it correctly.
    formatted_user_answers = {}
    for q_num, ans_text in user_answers.answers.items():
        if q_num in session_data["questions"]:
            formatted_user_answers[q_num] = {
                "Question": session_data["questions"][q_num]["Question"],
                "Answer": ans_text
            }

    evaluation = evaluate.evaluate_ans(formatted_user_answers, ideal_answers)

    # Clean up the session after it's completed
    del interview_sessions[interview_id]

    return evaluation

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)