import os
from rhvoice_wrapper import TTS

data_path=os.path.join(os.getcwd(), "rhvoice")
lib_path=os.path.join(data_path, "RHVoice.dll")
config_path = os.path.join(data_path, "RHVoice.ini")
tts = TTS(
	lib_path=lib_path, data_path =data_path, config_path = config_path, quiet=True, stream=False
)
voices = list(tts.voices)
tts.join()
print(voices)
if "mateo-beta" in voices:
	print("My voice is in the list.")
#tts.to_file(
#	filename='test.wav', text='This is a test', voice='Kathleen', format_='wav'
#)
#print("Done")