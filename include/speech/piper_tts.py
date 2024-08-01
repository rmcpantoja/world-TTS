from ..audio import pitch_changer
from Piper import speaker
import os
import datetime
import soundfile as sf

piper_speaker = None

async def piper_thread(
	voice,
	sid,
	rate,
	pitch,
	text,
	path,
	path_cache,
	cuda
):
	global piper_speaker
	voice_path = f"{path}/{voice}/{voice}.onnx"
	if piper_speaker is None or piper_speaker.model_path != voice:
		if os.path.exists(voice_path):
			piper_speaker = speaker.piperSpeak(voice_path, cuda)
			piper_speaker.load_model()
		else:
			return -1
	speaker_id = sid
	if piper_speaker.is_multispeaker():
		piper_speaker.set_speaker(speaker_id)
	if rate != 1.00:
		piper_speaker.set_rate(rate)

	audio_norm, sample_rate = piper_speaker.speak(text)
	current_datetime = datetime.datetime.now()
	formatted_datetime = current_datetime.strftime('%Y-%m-%d-%H-%M-%S')
	wav_filename = f"{path_cache}/piper{formatted_datetime}.wav"
	sf.write(wav_filename, audio_norm, sample_rate)
	if pitch != 1.00:
		print(pitch)
		audio = pitch_changer.change_pitch_with_praat(wav_filename, pitch)
		wav_filename = f"{wav_filename[:-4]}_changed.wav"
		audio.save(wav_filename, "WAV")
	return wav_filename
