import os
from rhvoice_wrapper import TTS
import datetime

class rhvoice:
	def __init__(self, path: str):
		self.path = path
		self.lib_path=os.path.join(self.path, "RHVoice.dll")
		self.config_path = os.path.join(self.path, "RHVoice.ini")
		self.tts = TTS(
			threads=1, force_process=False,
			lib_path=self.lib_path, data_path =self.path, config_path = self.config_path, quiet=True, stream=False
		)
		self._sets = None

	def available_voices(self):
		return list(self.tts.voices)

	def _prepare_set(self, val):
		try:
			return max(0, min(100, int(val)))
		except (TypeError, ValueError):
			return None

	def _normalize_set(self, val):
		return val/50.0-1

	def _set_set(self, param, value):
		if self._sets[param] == value:
			return 'unchanged'
		n_value = _prepare_set(value)
		if n_value is None:
			return 'bad value: {}'.format(value)
		self._sets[param] = str(n_value)
		self.tts.set_params(**{param: self._normalize_set(n_value)})
		return 'success'

	async def do_tts(self, voice, rate, pitch, text, path_cache):
		if voice not in self.available_voices():
			return -1
		if rate != 1 or pitch != 1:
			self._sets={
				'absolute_rate': rate/2, 'absolute_pitch': pitch/2, 'absolute_volume': 1
			}
		current_datetime = datetime.datetime.now()
		formatted_datetime = current_datetime.strftime('%Y-%m-%d-%H-%M-%S')
		wav_filename = f"{path_cache}/rh-{formatted_datetime}.wav"
		self.tts.to_file(
			filename=wav_filename, text=text, voice=voice, format_='wav', sets=self._sets
		)
		return wav_filename