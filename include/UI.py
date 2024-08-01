import re
import discord
import gdown
from . import config, extract_package, helpers
from .translator import *
import os
import traceback

# globals:

bot_config = config.read_bot_config()
lang = bot_config["language"]
lan = Translator(base_language="es")
rhvoice_pattern = re.compile(r"^RHVoice-.*(voice|language).*-v[\d.]+")
#rhvoice_pattern = re.compile(r"^RHVoice-(voice|language)-([^-]+)-([^-]+)-.*-v([\d.]+)")

class Upload_TTS_model(discord.ui.Modal):
	def __init__(self, synthesizer: str):
		super().__init__(title=lan.translate(lang, 'Subir modelo TTS'))
		self.name = discord.ui.TextInput(
			label=lan.translate(lang, 'Nombre'),
			placeholder=lan.translate(lang, '¿Cómo titulas la voz?'),
			required=True,
		)
		self.voiceurl = discord.ui.TextInput(
			label=lan.translate(lang, 'Enlace'),
			style=discord.TextStyle.long,
			placeholder=lan.translate(lang, 'URL de Drive o HuggingFace del paquete de voz (tar.gz)'),
			required=True,
			max_length=400,
		)
		self.synthesizer = synthesizer
		self.add_item(self.name)
		self.add_item(self.voiceurl)

	async def on_submit(self, interaction: discord.Interaction):
		if not "http" in self.voiceurl.value:
			await interaction.response.send_message(f'{lan.translate(lang, "Hola")}, {interaction.user}. {lan.translate(lang, "Parece que el paquete de voz que estás intentando subir no es un enlace válido.")}', ephemeral=True)
			return
		else:
			await interaction.response.send_message(f'{lan.translate(lang, "Hola")}, {interaction.user} {lan.translate(lang, "Gracias por el paquete, estamos procesándolo.")}', ephemeral=True)
		downame = gdown.download(self.voiceurl.value, fuzzy=True)
		if downame is None or not isinstance(downame, str):
			await interaction.channel.send(lan.translate(lang, 'No se ha podido descargar el paquete de voz. Por favor, asegúrate de que el enlace al que estás llenando en el formulario sea un enlace compartible.'))
			return
		if self.synthesizer == "piper":
			_, _, voice_path, _ = helpers.colab_or_local_running(True, "piper")
			if not downame.endswith(".tar.gz"):
				await interaction.channel.send(lan.translate(lang, 'Hmm... por lo que veo, este no es un paquete de voz. Él debe estar en un formato tar.gz.\nPor favor, consulta la guía de Piper para obtener información de cómo hacer esto.'))
				return
			realname = downame[:-7]
			if realname.startswith("voice-"):
				realname = realname[6:]
				print(realname)
			extract_package.extract_tar(downame, voice_path)
			# comprobando si hay un archivo onnx ahí:
			if not helpers.detect_onnx_models(f"{voice_path}/{realname}"):
				await interaction.channel.send(lan.translate(lang, "HMM... este archivo tar.gz no ha tenido un modelo de voz. Por favor, no subas otra cosa que no sea un modelo TTS exportado."))
				return
			else:
				print(lan.translate(lang, "Todo está bien. EL proceso ha terminado."))
			#print(f'{lan.translate(lang, "Ya le avisé al")} {myself} {lan.translate(lang, "en MD para que lo ponga, o puedes hacerlo tú y avisarle. Ahora voy a informar en el canal que configuraste.")}')
		elif self.synthesizer == "RHVoice":
			voice_path, _ = helpers.colab_or_local_running(True, "RHVoice")
			if not downame.endswith(".zip"):
				await interaction.channel.send(lan.translate(lang, 'Este no es un paquete de voz válido para RHVoice. Él debe estar en un formato zip.\nEjecuta scons dentro del proyecto RHVoice para obtener el zip de tu paquete y súbelo.'))
				return
			realname = downame[:-4]
			rhvoice_format = rhvoice_pattern.match(realname)
			if not rhvoice_format:
				await interaction.channel.send(lan.translate(lang, 'El paquete subido no tiene el formato esperado.'))
				return
			extract_package.extract_zip(downame, f"{voice_path}/{self.name.value}")
			# We need to check voice.data.
			if not helpers.detect_hts_models(f"{voice_path}/{self.name.value}/*"):
				await interaction.channel.send(lan.translate(lang, "El paquete que subiste no tiene el archivo de voz para funcionar."))
				return
			else:
				print(lan.translate(lang, "Todo está bien. EL proceso ha terminado."))
		await interaction.channel.send(f'🎤{lan.translate(lang, "¡Presentamos un nuevo modelo TTS! gracias a")} {interaction.user.mention} {lan.translate(lang, "por proporcionarlo, y se llama")}: {self.name.value}.\n📝{lan.translate(lang, "¡Pronto estará disponible en /list!")}')
		os.remove(downame)

	async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
		await interaction.channel.send(lan.translate(lang, '¡Ups! Creo que algo ha salido mal. Por favor, ponte en contacto con los mantenedores del bot.'))
		traceback.print_exception(type(error), error, error.__traceback__)
