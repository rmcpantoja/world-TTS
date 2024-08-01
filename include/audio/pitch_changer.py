import parselmouth
from parselmouth.praat import call

def change_pitch_with_praat(audio_file, factor):
	snd = parselmouth.Sound(audio_file)
	manipulation = call(snd, "To Manipulation", 0.01, 75, 600)
	pitch_tier = call(manipulation, "Extract pitch tier")
	call(pitch_tier, "Multiply frequencies", snd.xmin, snd.xmax, factor)
	call([pitch_tier, manipulation], "Replace pitch tier")
	return call(manipulation, "Get resynthesis (overlap-add)")
