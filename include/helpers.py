import glob
import os
import subprocess
from . import config
from .translator import *

def colab_or_local_running(drive_required=False, tts = "piper", quiet=True):
	bot_config = config.read_bot_config()
	lang = bot_config["language"]
	lan = Translator(base_language="es")
	colab = False
	cuda = False
	# aquí comprobamos si existe /content, pero no existe un montado de Drive:
	if drive_required:
		if os.path.exists("/content") and not os.path.exists("/content/drive"):
			raise Exception(lan.translate(lang, "Por favor, dé montando Drive para que el bot funcione y se sincronice con los cambios. Tenga la bondad."))
	if os.path.exists("/content/drive/Othercomputers/"):
		colab = True
	if not colab:
		if tts == "forward":
			ruta = bot_config["local_paths"]["ftvoices_path"]
		elif tts == "piper":
			ruta = bot_config["local_paths"]["voices_path"]
		elif tts == "RHVoice":
			ruta = bot_config["local_paths"]["rhvoices_path"]
		ruta_cache = bot_config["local_paths"]["audio_cache_path"]
		if not quiet: print(lan.translate(lang, "Ejecutando en modo local."))
	else:
		cuda = True
		if tts == "forward":
			ruta = bot_config["colab_paths"]["ftvoices_path"]
		elif tts == "piper":
			ruta = bot_config["colab_paths"]["voices_path"]
		elif tts == "RHVoice":
			ruta = bot_config["colab_paths"]["rhvoices_path"]
		ruta_cache = bot_config["colab_paths"]["audio_cache_path"]
		if not quiet: print(lan.translate(lang, "Ejecutando en modo colab."))
		# comprueba GPU:
		try:
			gpu_info = subprocess.check_output("nvidia-smi -L", shell=True)
		except subprocess.CalledProcessError as e:
			cuda = False
		if cuda:
			if not quiet: print(lan.translate(lang, "Usando GPU para inferencia."))
		else:
			if not quiet: print(lan.translate(lang, "Usando CPU para inferencia."))
	if not os.path.exists(ruta_cache):
		os.makedirs(ruta_cache)
	if tts == "forward" or tts == "piper":
		return colab, cuda, ruta, ruta_cache
	elif tts == "RHVoice":
		return ruta, ruta_cache

def detect_onnx_models(path):
	onnx_models = glob.glob(path + '/*.onnx')
	if len(onnx_models) > 1:
		return onnx_models
	elif len(onnx_models) == 1:
		return onnx_models[0]
	else:
		return None

def detect_hts_models(path):
	files = glob.glob(path + '/*.data')
	if len(files) > 1:
		return files
	elif len(files) == 1:
		return files[0]
	else:
		return None

def remove_audio_cache(path_cache):
	if os.path.isdir(path_cache):
		file_counter = 0
		for file in os.listdir(path_cache):
			full_path = os.path.join(path_cache, file)
			if os.path.isfile(full_path):
				os.remove(full_path)
				file_counter += 1
		return file_counter
	else:
		return -1