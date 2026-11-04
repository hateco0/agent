import sys
sys.path=['src','.']+sys.path
import speech_recognition as sr
from voice_os_agent.voice import microphone as m
from core import logging_setup
r=sr.Recognizer()
mic=m.SoundDeviceMicrophone()
try:
    with mic as source:
        r.adjust_for_ambient_noise(source,duration=0.6)
        logging_setup.log.info('LISTEN')
        audio=r.listen(source,timeout=4,phrase_time_limit=6)
    t=r.recognize_google(audio,language='ru-RU')
    logging_setup.log.info('TXT:'+t)
except Exception as e:
    logging_setup.log.exception('ERR')
