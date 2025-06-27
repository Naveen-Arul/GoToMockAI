import json
from GotoMock import resume,question,answer,check,evaluate,txt_to_speech

res = resume.Resume("23ADR052 Gurruprasaath M K.pdf")
que=question.run_interview_style_quiz(res)
ans = answer.Answer(que, res)
response = check.answer_check(que)
result=evaluate.evaluate_ans(response,ans)

print(json.dumps(result, indent=4))

txt_to_speech.text_to_speech(f"Your final overall score is {result.get('OverallScore', 0)} out of 10.")
txt_to_speech.text_to_speech(f"Here is your overall feedback: {result.get('OverallFeedback', 'No feedback available.')}")