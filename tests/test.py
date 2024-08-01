from Piper import speaker
import soundfile as sf
speaker = speaker.piperSpeak("	")
speaker.load_model()
#speaker.set_noise_scale_w(1.7)
print(speaker.is_multispeaker())
audio_norm, sample_rate = speaker.speak("Cargando.")
sf.write("audio.wav", audio_norm, sample_rate)