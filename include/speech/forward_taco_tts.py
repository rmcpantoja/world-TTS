import os
import numpy as np
import onnxruntime
from .utils.cleaners import Cleaner
from .utils.tokenizer import Tokenizer
import json
import datetime
import soundfile as sf

class forward:
	def __init__(self, path: str):
		self.path = path
		self.cur_model = None
		self.checkpoint = None
		self.voc_checkpoint = None
		self.config = None
		self.voc_config = None
		self.cleaner = None
		self.tokenizer = Tokenizer()
		# Configure a session:
		self.sess_options = onnxruntime.SessionOptions()

	def available_voices(self):
		return os.listdir(self.path)

	async def do_tts(
		self, voice, rate, pitch, energy, text, path_cache, cuda
	):
		self.voice_path = f"{self.path}/{voice}/{voice}.onnx"
		self.voc_path = f"{self.path}/{voice}/vocoder-{voice}.onnx"
		if self.cur_model is None or self.cur_model != self.voice_path:
			self.load_e2e()
			self.cleaner = Cleaner('no_cleaners', True, self.config["espeak"]["voice"])
		current_datetime = datetime.datetime.now()
		formatted_datetime = current_datetime.strftime('%Y-%m-%d-%H-%M-%S')
		wav_filename = f"{path_cache}/ft-{formatted_datetime}.wav"
		pitch_function = lambda x: x * pitch
		energy_function = lambda x: x * energy
		x = self.tokenizer(self.cleaner(text))
		x = np.expand_dims(np.array(x, dtype=np.int64), 0)
		synth_options = np.array(
			[rate, pitch, energy],
			dtype=np.float32,
		)
		mel = self.checkpoint.run(
			None,
			{
				"input": x,
				"synth_options": synth_options
			},
		)[0]
		audio = self.voc_checkpoint.run(None, {"input": mel})[0].squeeze()
		sf.write(wav_filename, audio, self.config["audio"]["sample_rate"])
		return wav_filename

	def load_e2e(self):
		self.get_ft()
		self.get_hifigan()
		# Check config:
		if not self.config["audio"]["sample_rate"] == self.voc_config["sampling_rate"]:
			raise Exception("The sample rate of the model is not the same than the vocoder.")
		self.cur_model = self.voice_path
		return True

	def get_ft(self):
		conf = self.voice_path + ".json"
		with open(conf, encoding="utf-8") as f:
			self.config = json.loads(f.read())
		self.checkpoint = onnxruntime.InferenceSession(str(self.voice_path), sess_options=self.sess_options)

	def get_hifigan(self):
		hifigan_pretrained_model = self.voc_path
		if not os.path.exists(hifigan_pretrained_model):
			raise Exception(f"HiFI-GAN model {hifigan_pretrained_model} doesn't exists!")
		# Load HiFi-GAN
		conf = hifigan_pretrained_model + ".json"
		with open(conf) as f:
			self.voc_config = json.loads(f.read())
		self.voc_checkpoint = onnxruntime.InferenceSession(str(hifigan_pretrained_model), sess_options=self.sess_options)
