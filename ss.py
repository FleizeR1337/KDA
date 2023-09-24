import speech_recognition as sr
from gtts import gTTS
import os

def recognize_speech():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Говорите что-то...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language="ru-RU")
        print(f"Вы сказали: {text}")
        return text
    except sr.UnknownValueError:
        print("Извините, не удалось распознать речь")
        return ""
    except sr.RequestError as e:
        print(f"Произошла ошибка при отправке запроса к сервису распознавания речи: {e}")
        return ""

def speak(text):
    tts = gTTS(text, lang="ru")
    tts.save("output.mp3")
    os.system("mpg123 output.mp3")  # Воспроизведение аудиофайла
    os.remove("output.mp3")  # Удаление временного файла

# Основной код для взаимодействия с пользователем
while True:
    command = recognize_speech()

    if "включи музыку" in command:
        speak("Включаю музыку")
        # Ваш код для включения музыки

    elif "выключи музыку" in command:
        speak("Выключаю музыку")
        # Ваш код для выключения музыки

    elif "привет" in command:
        speak("Привет! Как я могу вам помочь?")

    elif "пока" in command:
        speak("До свидания!")
        break