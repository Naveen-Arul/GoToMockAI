import json
from .txt_to_speech import text_to_speech

def answer_check(que):
    
    data={}
    for i in que:
        print("\n")
        print("Question NO: ",i)
        print("\n")
        print(que[i]["Question"])
        text_to_speech(que[i]["Question"])
        print("\n")
        ans = input("Enter Answer For This:\n")    
        data.update({i:{"Question":que[i]["Question"],"Answer":ans}})
    
    return data