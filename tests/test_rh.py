from include.speech import RHVoice_tts
import os

rhpath = "rhvoice"
rhvoice = RHVoice_tts.rhvoice(rhpath)

voice = "mateo-beta"
rate = 1.0
pitch = 1.0
text = "This is a test."
path_cache = os.getcwd()

result = rhvoice.do_tts(voice, rate, pitch, text, path_cache)
print(f"Generated file: {result}")