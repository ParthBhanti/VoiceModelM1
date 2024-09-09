import speech_recognition as sr
import openai
import pyttsx3
import face_recognition
import cv2
import numpy as np
import subprocess
import os

openai.api_key = '*******************************'

recognizer = sr.Recognizer()
microphone = sr.Microphone()
tts_engine = pyttsx3.init()

tts_engine.setProperty('rate', 150)
tts_engine.setProperty('volume', 0.9)

def listen_for_keyword(keyword="Jarvis"):
    while True:
        print("Listening for keyword...")
        result = recognize_speech_from_mic(recognizer, microphone)
        if result["success"] and keyword.lower() in result["transcription"].lower():
            print("Keyword detected!")
            return True
        
def recognize_speech_from_mic(recognizer, microphone):
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)

    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable/unresponsive"
    except sr.UnknownValueError:
        response["success"] = False
        response["error"] = "Unable to recognize speech"
    
    return response


def get_gpt_response(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"


def speak_text(text):
    tts_engine.say(text)
    tts_engine.runAndWait()


def perform_action(command):
    if 'open chrome' in command:
        if os.name == 'nt':
            subprocess.Popen('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')
        elif os.name == 'posix':
            subprocess.Popen(['open', '-a', 'Google Chrome'])
    elif 'open notepad' in command:
        if os.name == 'nt':
            subprocess.Popen('notepad.exe')
        elif os.name == 'posix':
            subprocess.Popen(['open', '-a', 'TextEdit'])
    elif 'open Dev c++' in command:
        if os.name == 'nt':
            subprocess.Popen('D:\Dev-Cpp\devcpp.exe')
        elif os.name == 'posix':
            subprocess.Popen(['open', '-a', 'TextEdit'])
    
    elif 'open this model' in command:
        if os.name == 'nt':
            subprocess.Popen('VoiceModelM1')
        elif os.name == 'posix':
            subprocess.Popen(['open', '-a', 'TextEdit'])
    
    else:
        speak_text("Sorry, I can't perform that action.")


def authenticate_by_voice():
    speak_text("Please say your authentication phrase.")
    result = recognize_speech_from_mic(recognizer, microphone)
    if result["success"]:
        if result["transcription"].lower() == "Earth is round".lower():
            speak_text("Voice authentication successful.")
            return True
    speak_text("Voice authentication failed.")
    return False


def authenticate_by_face():
    known_image = face_recognition.load_image_file("recogphoto.jpg")
    known_encoding = face_recognition.face_encodings(known_image)[0]

    video_capture = cv2.VideoCapture(0)
    speak_text("Looking for your face. Please look at the camera.")
    
    while True:
        ret, frame = video_capture.read()
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces([known_encoding], face_encoding)
            if True in matches:
                speak_text("Face authentication successful.")
                video_capture.release()
                cv2.destroyAllWindows()
                return True
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    speak_text("Face authentication failed.")
    return False


def main():
    while True:
        if listen_for_keyword():
            speak_text("Do you want voice recognition or face recognition?")
            result = recognize_speech_from_mic(recognizer, microphone)

            if result["success"]:
                if "voice" in result["transcription"].lower():
                    if authenticate_by_voice():
                        break
                #elif "face" in result["transcription"].lower():
                    #if authenticate_by_face():
                        break
            speak_text("Authentication failed. Please try again.")

    speak_text("Authentication successful. How can I assist you?")
    
    while True:
        result = recognize_speech_from_mic(recognizer, microphone)
        
        if result["success"]:
            command = result["transcription"].lower()
            if 'exit' in command:
                speak_text("Goodbye!")
                break
            if 'open' in command:
                perform_action(command)
            else:
                gpt_response = get_gpt_response(result["transcription"])
                speak_text(gpt_response)
        else:
            speak_text("I didn't catch that. Please try again.")

if __name__ == "__main__":
    main()


