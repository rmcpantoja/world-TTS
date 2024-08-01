# TTSDialogs.py
# By Mateo Cedillo.
import re
import numpy as np

def parse_dialog(text):
	"""Parses a dialog from a plain text to a dict"""
	"""Example:
es_ES-gustabo: "Me ha llegado una carta"\nes_ES-carlitos: A mí también, ¿qué dirá? {openpapper.wav}\nes_ES-gustabo: estimado lector...
	"""
	lines = text.split('\n')
	dialog = {}
	for i, line in enumerate(lines):
		parts = line.split(':')
		if len(parts) == 0:
			raise Exception(f"This is not a valid dialog\nError at line: {line}")
		elif len(parts) >= 2:
			name = parts[0].strip()
			text = ':'.join(parts[1:]).strip()
			audio = re.search(r'\{(.+?)\}', text)
			if audio:
				audio = audio.group(1)
				text = re.sub(r'\{(.+?)\}', '', text).strip()
			else:
				audio = None
			dialog[i] = {
				"name": name, "text": text, "audio": audio
			}
	return dialog

def make_dialog(tts_engine, fx_path, text):
	"""Returns an audio with dialog using TTS"""
	try:
		dialog_dict = parse_dialog(text)
	except Exception:
		return -1
	# Lets creating:
	for index, voice in dialog_dict.items():
		# For now, we need only two things:
		tts_voice = voice["name"]
		text_to_speak = voice["text"]
		print(text_to_speak)
		# Now, lets generate TTS:




text = """
voz1: préstame el teléfono para una llamada, por favor.
voz2: está bien, ve.
voz1: gracias. {numeros.wav}
"""
make_dialog(None, None, text)