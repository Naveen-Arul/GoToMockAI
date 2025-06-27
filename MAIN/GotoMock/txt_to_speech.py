import pyttsx3
def text_to_speech(txt):
    engine = pyttsx3.init()


    text = txt

    engine.say(text)


    engine.runAndWait()


    engine.stop()