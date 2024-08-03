# WorldTTS discord bot
# Unlock the potential of Text-To-Speech with Discord, extending it to multiple TTS architectures.
# by Mateo Cedillo - rmcpantoja
import os
import datetime
from datetime import timezone
current_date = datetime.datetime.now()
christmas_time = False
if 1 <= current_date.day <= 25 and current_date.month == 12:
	import time
	from include import Christmas
	christmas_time = True
from include.constants import worldttsbot_version
from include.extract_package import VOICE_INFO_REGEX
import discord
from discord import app_commands
from discord.ext import tasks
from typing import Optional, Literal
from include.admin import Admin
import json
from include import config, helpers, searcher, UI, utils, words
from include.translator import *
from include.speech import forward_taco_tts, piper_tts, RHVoice_tts
import asyncio
import atexit

# initialization:
bot_config = config.read_bot_config()
autoTTS = False
# Language:
lang = bot_config["language"]
lan = Translator(base_language="es")
TEST_GUILD = discord.Object(bot_config["bot_server_id"])
myself = None
# Start blacklisted words:
blacklisted_words = words.load_blacklisted_words()
# Setup admin support:
admin_control = Admin()

class MyClient(discord.Client):
	def __init__(self) -> None:
		intents = discord.Intents.all()
		intents.message_content = True
		intents.members = True
		intents.moderation = True
		super().__init__(intents=intents)
		self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
		self.tree.copy_global_to(guild=TEST_GUILD)
		await self.tree.sync()
		if christmas_time:
			hilo_mensajes.start()

client = MyClient()
# establecemos el canal:
channel = None

# Comprobamos si es ejecución colab o local, también cargar rutas:
colab, cuda, ftpath, path_cache = helpers.colab_or_local_running(True, "forward")
_, _, path, _ = helpers.colab_or_local_running(True, "piper")
# También queremos las rutas para RHVoice:
rhpath, _ = helpers.colab_or_local_running(True, "RHVoice")
# Initialize it:
forwardtaco = forward_taco_tts.forward(ftpath)
rhvoice = RHVoice_tts.rhvoice(rhpath)
rhvoices = rhvoice.available_voices()
with open("list.md", "r", encoding="utf-8") as tmpv:
	tmpvoices = tmpv.read()
piper_voices = searcher.get_all_voices(tmpvoices)
_all_voices = rhvoices + piper_voices
all_voices = Literal[tuple(_all_voices)]

@client.event
async def on_ready():
	global myself, channel, bot_config, lan, lang
	print(f'{lan.translate(lang, "Iniciado sesión como")} {client.user} (ID: {client.user.id})')
	print('--------------------')
	# Prepare bot's profile picture:
	with open('logo.png', 'rb') as hnd_logo:
		logo = hnd_logo.read()
	await client.user.edit(username="WorldTTS", avatar=logo)
	myself = client.get_user(bot_config["user_id"])
	channel = client.get_channel(bot_config["bot_general_channel"])
	if bot_config["welcome"]:
		await send_alert_to_everyone(client, f'{lan.translate(lang, "Bot en ejecución. Disfrútalo mientras esté disponible.")}\nGPU: {cuda}\nColab: {colab}')
	if christmas_time:
		await channel.send(lan.translate(lang, "¡Christmas time activado!"))
	if bot_config["moderation"]:
		await client.change_presence(
			activity=discord.Activity(type=discord.ActivityType.watching, name=lan.translate(lang, "contenido general y TTS"))
		)

async def send_alert_to_everyone(client: discord.Client, message: str):
	for server in client.guilds:
		for channel in server.text_channels:
			try:
				await channel.send(message)
			except Exception:
				continue
			else:
				break
	return True

@client.event
async def on_message(message):
	global blacklisted_words, admin_control, path_cache, bot_config, autoTTS
	if message.author == client.user:
		return
	if isinstance(message.channel, discord.TextChannel):
		# Blacklisted words:
		blacklisted, _ = words.contains_blacklisted_words(message.content, blacklisted_words)
		if blacklisted:
			if bot_config["moderation"]:
				await message.channel.send(f'{message.author.mention}, {lan.translate(lang, "¡El respeto principalmente! No está permitido decir eso aquí.")}')
				await message.delete()
				await myself.send(
					f"Enviando reporte:\n{message.author} ha usado una palabra no permitida en nuestra lista de palabras prohibidas: {_}\nContenido del texto: {utils.no_longe_text(lan, message.content, lang, 2)}."
				)
				moderating_file = "moderating.json"
				if os.path.exists(moderating_file):
					with open(moderating_file, "r") as file:
						moderating_data = json.load(file)
					user_data = moderating_data.get(str(message.author), {"general count": 0, "tts count": 0})
					user_data["general count"] += 1
					moderating_data[str(message.author)] = user_data
				else:
					moderating_data = {str(message.author): {"general count": 1, "tts count": 0}}
				with open(moderating_file, "w") as file:
					json.dump(moderating_data, file, indent=4)
				if user_data["general count"] >= 3:
					# a la tercera es la vencida...
					await message.author.ban(reason=lan.translate(lang, "Uso de palabras malsonantes no permitidas.\nLa próxima vez compórtate mejor."))
					await myself.send(f'{message.author} {lan.translate(lang, "ha sido baneado en el ámbito general.")}')
	# AutoTTS:
	if isinstance(message.channel, discord.TextChannel):
		autotts_channel = message.channel.name
	else:
		autotts_channel = None
	autotts_user = message.author.name
	try:
		autoTTS_servers = bot_config["autoTTS"]
	except KeyError:
		autoTTS = False
	if autotts_channel in autoTTS_servers and isinstance(message.channel, discord.TextChannel):
		if not bot_config["autoTTS"][autotts_channel]:
			autoTTS = False
		else:
			autoTTS = True
	elif autotts_user in autoTTS_servers and isinstance(message.channel, discord.TextChannel):
		if not bot_config["autoTTS"][autotts_user]:
			autoTTs = False
		else:
			autoTTS = True
	if autoTTS:
		try:
			voice, text = message.content.split("|", 1)
		except ValueError:
			try:
				voice = (
					bot_config["autoTTS_voices"].get(autotts_channel)
					or bot_config["autoTTS_voices"].get(autotts_user)
					or "en_US-hfc_female-medium"
				)
				text = message.content
			except KeyError:
				voice = "en_US-hfc_female-medium"
				text = message.content
		# text replacements:
		text = text.replace("*", "")
		speaker = 0
		rate = 1
		pitch = 1
		loop = asyncio.get_event_loop()
		if VOICE_INFO_REGEX.match(voice):
			# It is a piper model:
			task = loop.create_task(
				piper_tts.piper_thread(
					voice,
					speaker,
					rate,
					pitch,
					text,
					path,
					path_cache,
					cuda
				)
			)
			wav_filename = await task
			if wav_filename == -1:
				await message.channel.send(f'{lan.translate(lang, "¡Esta voz no existe! Por favor, usa /list para obtener una lista. La voz fue")}: {voice}.')
				return
		else:
			# It is RHVoice or other.
			task = loop.create_task(
				rhvoice.do_tts(
					voice,
					rate,
					pitch,
					text,
					path_cache
				)
			)
			wav_filename = await task
			if wav_filename == -1:
				await message.channel.send(f'{lan.translate(lang, "¡Esta voz no existe! Por favor, usa /list para obtener una lista. La voz fue")}: {voice}.')
				return
		await message.reply(
			file=discord.File(wav_filename),
			mention_author=True
		)
	# Admin commands:
	# Give an alert or message to all users:
	if "!alert" in message.content:
		is_admin = admin_control.is_admin(message.author.name)
		if is_admin:
			await send_alert_to_everyone(client, message.content.split("|")[1])
		else:
			await message.channel.send(lan.translate(lang, "Este comando solo está disponible para los administradores."))
	if message.content == "!delstats":
		is_admin = admin_control.is_admin(message.author.name)
		if is_admin:
			if os.path.exists("moderating.json"):
				os.remove("moderating.json")
				await message.channel.send(lan.translate(lang, "Lista de usuarios advertidos o baneados está borrada."))
			else:
				await message.channel.send(lan.translate(lang, "Con suerte, no hay ningún usuario advertido de contenido prohivido. Todos se han portado bien."))
		else:
			await message.channel.send(lan.translate(lang, "Este comando solo está disponible para los administradores."))
	if message.content == "!stats":
		is_admin = admin_control.is_admin(message.author.name)
		if is_admin:
			moderating_file = "moderating.json"
			if os.path.exists(moderating_file):
				with open(moderating_file, "r") as file:
					moderating_data = json.load(file)
				user_data = moderating_data.get(str(message.author.name), {"general count": 0, "tts count": 0})
				moderating_data[str(message.author.name)] = user_data
				await message.channel.send(f'{lan.translate(lang, "Estadísticas de moderación de contenido")}:\n{lan.translate(lang, "Número de intentos TTS no permitidos")}: {moderating_data[message.author.name]["tts count"]}.\n{lan.translate(lang, "Intentos de envío de mensajes no permitidos")}: {moderating_data[message.author.name]["general count"]}.')
			else:
				await message.channel.send(lan.translate(lang, "No hay estadísticas."))
		else:
			await message.channel.send(lan.translate(lang, "Este comando solo está disponible para los administradores."))
	if message.content == "!mod":
		# Enhable/disable use of blacklisted words in a general/TTS sessions:
		is_admin = admin_control.is_admin(message.author.name)
		if is_admin:
			if bot_config["moderation"]:
				bot_config["moderation"] = False
				await message.channel.send(lan.translate(lang, "Moderación de contenido desactivada."))
			else:
				bot_config["moderation"] = True
				await message.channel.send(lan.translate(lang, "Moderación de contenido activada. Vigilando el contenido del chat general y contenido TTS."))
		else:
			await message.channel.send(lan.translate(lang, "Este comando solo está disponible para los administradores."))
	if message.content == "!cleanup":
		is_admin = admin_control.is_admin(message.author.name)
		if is_admin:
			file_counter = helpers.remove_audio_cache(path_cache)
			if not file_counter == -1:
				await message.channel.send(f'{file_counter} {lan.translate(lang, "audios borrados.")}')
			else:
				await message.channel.send(lan.translate(lang, "No hay audio que limpiar."))
		else:
			await message.channel.send(lan.translate(lang, "Este comando solo está disponible para los administradores."))
	if message.content.startswith("!admin"):
		# !admin username
		is_admin = admin_control.is_admin(message.author.name)
		if is_admin:
			new_admin = message.content.split(" ")[1]
			admin_control.add_admin(new_admin)
			await message.channel.send(f'{new_admin} {lan.translate(lang, "es ahora un administrador del bot. Mirar la sección de comandos de administración en la documentación para más información.")}')
		else:
			await message.channel.send(lan.translate(lang, "Este comando solo está disponible para los administradores."))
	if message.content.startswith("!pay"):
		# !paid voicename user_who_bought
		is_admin = admin_control.is_admin(message.author.name)
		if is_admin:
			# Register the purchase of this voice in config:
			voicename = message.content.split(" ")[1]
			with open("list.md", "r", encoding="utf-8") as info_voces:
				lista = info_voces.read()
			real_voicename = searcher.get_paid_voice(lan, lang, lista, voicename)
			username = message.content.split(" ")[2]
			bot_config.setdefault("paid_voices", {}).setdefault(real_voicename, {})[username] = True
			config.write_bot_config(bot_config)
			await message.channel.send(f'{voicename} {lan.translate(lang, "fue registrado como comprado a")} {username}')
		else:
			await message.channel.send(lan.translate(lang, "Este comando solo está disponible para los administradores."))
	# User commands:
	if lan.translate(lang, "guía de piper") in message.content:
		await message.channel.send(f'{lan.translate(lang, "Esta es la guía de piper")}: https://github.com/rmcpantoja/Piper-Training-Guide-with-Screen-Reader')
	if lan.translate(lang, "cuaderno de entrenamiento piper") in message.content:
		await message.channel.send(
			f'{lan.translate(lang, "Cuaderno de entrenamiento general")}: https://colab.research.google.com/github/rmcpantoja/piper/blob/master/notebooks/piper_multilingual_training_notebook.ipynb\n{lan.translate(lang, "Cuaderno de entrenamiento en español")}: https://colab.research.google.com/github/rmcpantoja/piper/blob/master/notebooks/piper_multilenguaje_cuaderno_de_entrenamiento.ipynb'
		)
	if lan.translate(lang, "cuaderno para exportar piper") in message.content or lan.translate(lang, "exportador de modelo") in message.content:
		await message.channel.send(
			f'{lan.translate(lang, "Cuaderno para exportar tu modelo")}: https://colab.research.google.com/github/rmcpantoja/piper/blob/master/notebooks/piper_model_exporter.ipynb\n{lan.translate(lang, "Cuaderno en español para exportar tu modelo")}: https://colab.research.google.com/github/rmcpantoja/piper/blob/master/notebooks/piper_exportador_modelos_espa%C3%B1ol.ipynb'
		)
	if lan.translate(lang, "cuaderno de inferencia piper") in message.content or lan.translate(lang, "cuaderno de síntesis") in message.content:
		await message.channel.send(
			f'{lan.translate(lang, "Cuaderno de síntesis")}: https://colab.research.google.com/github/rmcpantoja/piper/blob/master/notebooks/piper_inference_(ONNX).ipynb\n{lan.translate(lang, "Cuaderno de síntesis en español")}: https://colab.research.google.com/github/rmcpantoja/piper/blob/master/notebooks/piper_inference_(ONNX).ipynb'
		)
	# Reset autoTTS to default state:
	autoTTS = False

@client.tree.command(description=lan.translate(lang, "Obtiene una lista de voces del sintetizador en específico."))
async def list(interaction: discord.Interaction, synthesizer: Literal ["piper", "RHVoice"]):
	if synthesizer == "piper":
		await interaction.response.send_message(f'{lan.translate(lang, "Aquí está la lista de voces")}:', file = discord.File("list.md"), ephemeral=True)
	elif synthesizer == "RHVoice":
		text_list = f"Lista de voces disponibles de RHVoice:\n\n{rhvoice.available_voices()}"
		await interaction.response.send_message(		text_list, ephemeral=True)

@client.tree.command(description=lan.translate(lang, "Buscar un modelo."))
async def search(interaction: discord.Interaction, term: str):
	with open("list.md", "r", encoding="utf-8") as info_voces:
		lista = info_voces.read()
	resultados = searcher.search(
		lan, lang, lista, term
	)
	if not resultados == -1:
		await interaction.response.send_message(f'{lan.translate(lang, "Resultados de la búsqueda para")} {term}:\n{resultados}', ephemeral=True)
	else:
		await interaction.response.send_message(f'{lan.translate(lang, "Lo siento, pero no hay una voz que se llame")} {term}.\n{lan.translate(lang, "Asegúrate de que tu término es correcto. Si necesitas esta voz, puedes proporcionarnos el dataset o el paquete exportado para entrenarlo o agregarlo.")}', ephemeral=True)

@client.tree.command(description=lan.translate(lang, "Información del bot y las voces."))
async def info(interaction: discord.Interaction):
	messageinfo = f'{lan.translate(lang, "Información de WorldTTS bot")} {worldttsbot_version}\n{lan.translate(lang, "World TTS: aprovecha el potencial del texto a voz en Discord usando múltiples sintetizadores. Desarrollado por Mateo Cedillo.")}\n"'
	with open("list.md", "r", encoding="utf-8") as info_voces:
		lista = info_voces.read()
	voces_totales, info = searcher.list_info(lan, lang, lista)
	messageinfo += f'{lan.translate(lang, "Hay")} {voces_totales} {lan.translate(lang, "voces en total.")}\n{lan.translate(lang, "Tenemos")} {len(info)} {lan.translate(lang, "idiomas disponibles")}:\n'
	for idioma in info:
		messageinfo += f'{idioma["language"]} {lan.translate(lang, "con")} {idioma["n_voices"]} {lan.translate(lang, "voces y")} {len(idioma["paid_voices"])} {lan.translate(lang, "voces de paga.")}\n'
	messageinfo += lan.translate(lang, "¿Tienes una nueva sugerencia? ¡Contáctanos!")
	await interaction.response.send_message(messageinfo)

@client.tree.command(description=lan.translate(lang, "Envía la información del modelo al chat (si está disponible)."))
async def mcard(interaction: discord.Interaction, voice: str):
	global path
	model_Card_path = f"{path}/{voice}/MODEL_CARD"
	if os.path.exists(model_Card_path):
		with open(model_Card_path, "r", encoding='utf-8') as model_Card:
			info = model_Card.read()
		await interaction.response.send_message(info)
	else:
		await interaction.response.send_message(f'{lan.translate(lang, "Lo siento, no hay información acerca del modelo")} {voice}.')

if christmas_time:
	async def christmas_tts_message():
		global channel
		if channel is None:
			return
		loop = asyncio.get_event_loop()
		async def send_christmas_message(channel, christmas_message, wav_filename):
			if channel is not None:
				await channel.send(christmas_message, file=discord.File(wav_filename))
				print("sent!")
		voice_command, christmas_message = Christmas.setup_Christmass_message()
		task = loop.create_task(
			piper_tts.piper_thread(
				voice_command, 0, 1, christmas_message, path, path_cache, cuda
			)
		)
		wav_filename = await task
		if wav_filename == -1:
			return
		asyncio.run_coroutine_threadsafe(send_christmas_message(channel, christmas_message, wav_filename), loop)

	@tasks.loop(seconds=1800)
	async def hilo_mensajes():
		await christmas_tts_message()


@client.tree.command(description=lan.translate(lang, "Texto A Voz con WorldTTS."))
@app_commands.describe(
	voice=lan.translate(lang, 'El nombre de una voz que se desea usar. Para obtener una lista, por favor usa /list.'),
	speaker=lan.translate(lang, 'si este modelo tiene varios hablantes, puedes establecer el id del hablante. 0, 1, 2...'),
	rate=lan.translate(lang, 'Cambia la velocidad de la voz (opcional). 1 normal, 0.5 más rápido, 2 más lento.'),
	pitch=lan.translate(lang, '(opcional) cambia el tono de la voz. 0.50 más grabe, 1 normal, 2 más agudo.'),
	text=lan.translate(lang, 'texto a sintetizar.')
)
async def wtts(
	interaction: discord.Interaction,
	synthesizer: Literal ["forward", "piper", "RHVoice"],
	voice: str,
	speaker: Optional[int] = 0,
	rate: Optional[float] = 1.00,
	pitch: Optional[float] = 1.00,
	text: Optional[str] = lan.translate(lang, "Esta es una prueba.")
):
	# Check if this user can make TTS requests:
	moderating_file = "moderating.json"
	if os.path.exists(moderating_file):
		with open(moderating_file, "r") as file:
			moderating_data = json.load(file)
		user_data = moderating_data.get(str(interaction.user), {"general count": 0, "tts count": 0})
		moderating_data[str(interaction.user)] = user_data
	else:
		moderating_data = {str(interaction.user): {"general count": 0, "tts count": 0}}
	if moderating_data[str(interaction.user)]["tts count"] >= 3:
		await interaction.response.send_message(f'{lan.translate(lang, "Lo siento")}, {interaction.user.mention}, {lan.translate(lang, "ya no puedes enviar solicitudes de TTS. Para la próxima, por favor crea un mejor contenido.")}', ephemeral=True)
		return
	# Check for blacklisted words first:
	global blacklisted_words, config
	blacklisted, _ = words.contains_blacklisted_words(text, blacklisted_words)
	if blacklisted:
		if bot_config["moderation"]:
			print(_)
			await interaction.response.send_message(f'{lan.translate(lang, "Lo siento")}, {interaction.user.mention}, {lan.translate(lang, "tu texto contienen una o más palabras que están establecidas en nuestra lista de palabras prohibidas.")}', ephemeral=True)
			await myself.send(
				f"Enviando reporte:\n{interaction.user} intentó sintetizar un audio usando una palabra no permitida en nuestra lista de palabras prohibidas: {_}.\nTexto que se intentó sintetizar: {utils.no_longe_text(lan, text, lang, 2)}"
			)
			moderating_data[str(interaction.user)]["tts count"] += 1
			with open(moderating_file, "w") as file:
				json.dump(moderating_data, file, indent=4)
			if moderating_data[str(interaction.user)]["tts count"] >= 3:
				await interaction.channel.send(f'{interaction.user.mention}, {lan.translate(lang, "a partir de ahora ya no podrás generar contenido de texto a voz.")}')
				await myself.send(f"Sigo reportando.\n{interaction.user} fue baneado en el ámbito TTS porque usó contenido no permitido 3 veces.")
			return
	# Check paid voices:
	with open("list.md", "r", encoding="utf-8") as info_voces:
		lista = info_voces.read()
	paid_voice = searcher.get_paid_voice(lan, lang, lista, voice)
	if paid_voice is None:
		paid_voice = voice
	if searcher.is_paid_voice(paid_voice, bot_config):
		# Check if the user has bought  this voice.
		if not searcher.has_paid_this_voice(
			config=bot_config,
			language_handler=lan,
			language=lang,
			voice=paid_voice,
			user=interaction.user.name
		):
			await interaction.response.send_message(f'{interaction.user.mention}, {lan.translate(lang, "Esta es una voz de paga. Para usarla, cómprala en")} {bot_config["paid_url"]}.\n{lan.translate(lang, "Registraremos la compra una vez lo hayas hecho y podrás usar esta voz. Para obtener información acerca del costo, por favor ponte en contacto con el creador del modelo.")}')
			return
	loop = asyncio.get_event_loop()
	await interaction.response.send_message(f'{lan.translate(lang, "Solicitud de texto a voz enviada por")} {interaction.user.mention}.\n{lan.translate(lang, "Iniciando...")}', ephemeral=True)
	if synthesizer == "forward":
		task = loop.create_task(
			forwardtaco.do_tts(
				voice, rate, pitch, 1.0, text, path_cache, cuda
			)
		)
	elif synthesizer == "piper":
		task = loop.create_task(
			piper_tts.piper_thread(
				voice,
				speaker,
				rate,
				pitch,
				text,
				path,
				path_cache,
				cuda
			)
		)
	elif synthesizer == "RHVoice":
		task = loop.create_task(
			rhvoice.do_tts(
				voice, rate, pitch, text, path_cache
			)
		)
	wav_filename = await task
	if wav_filename == -1:
		await interaction.channel.send(f'{lan.translate(lang, "¡Esta voz no existe! Por favor, usa /list para obtener una lista. La voz fue")}: {voice}.')
		return
	await interaction.channel.send (
		f'{interaction.user.mention}, {lan.translate(lang, "este es tu audio generado con")} {voice}\n{lan.translate(lang, "Texto")}: {utils.no_longe_text(lan, text, lang, 2)}',
		file=discord.File(wav_filename)
	)

@client.tree.command(description=lan.translate(lang, "Alternar autoTTS en un canal o usuario"))
async def autotts(
	interaction: discord.Interaction,
	mode: Literal["Channel", "User"],
):
	if not isinstance(interaction.channel, discord.TextChannel):
		await interaction.response.send_message(lan.translate(lang, "AutoTTS no está soportado en canales de voz o mensajes directos."))
		return
	if mode == "Channel":
		autotts_channel = interaction.channel.name
	else:
		autotts_channel = interaction.user.name
	try:
		autoTTS_config = bot_config["autoTTS"]
		if autoTTS_config[autotts_channel]:
			bot_config["autoTTS"][autotts_channel] = False
			await interaction.response.send_message(f'{lan.translate(lang, "AutoTTS desactivado para")} {autotts_channel}')
		else:
			bot_config["autoTTS"][autotts_channel] = True
			await interaction.response.send_message(f'{lan.translate(lang, "AutoTTS activado para")} {autotts_channel}')
	except KeyError:
		bot_config.setdefault("autoTTS", {})[autotts_channel] = True
		await interaction.response.send_message(f'{lan.translate(lang, "AutoTTS activado para")} {autotts_channel}')

@client.tree.command(description=lan.translate(lang, "Configurar autoTTS"))
async def autotts_setup(
	interaction: discord.Interaction,
	mode: Literal["Channel", "User"],
	voice: str,
):
	if mode == "Channel":
		autotts_channel = interaction.channel.name
	else:
		autotts_channel = interaction.user.name
	try:
		autoTTS_voices = bot_config["autoTTS_voices"]
		if not autotts_channel in autoTTS_voices:
			bot_config["autoTTS_voices"][autotts_channel] = voice
			await interaction.response.send_message(f'{autotts_channel} {lan.translate(lang, "usará esta voz como predeterminada para el autoTTS")}: {voice}.')
		else:
			await interaction.response.send_message(f'{autotts_channel} {lan.translate(lang, "cambió la voz para el auto TTS a")}: {voice}.')
			bot_config.setdefault("autoTTS_voices", {})[autotts_channel] = voice
	except KeyError:
		bot_config.setdefault("autoTTS_voices", {})[autotts_channel] = voice
		await interaction.response.send_message(f'{autotts_channel} {lan.translate(lang, "usará esta voz como predeterminada para el autoTTS")}: {voice}.')

@client.tree.command(description=lan.translate(lang, "Unirme a tu canal de voz"))
async def join(interaction: discord.Interaction):
	message = ""
	err = False
	if interaction.guild.voice_client is not None:
		message = "Estás en un canal de voz"
		if interaction.guild.voice_client.channel != interaction.user.voice.channel:
			message += " pero no en el que estoy. Voy a él..."
			await interaction.guild.voice_client.move_to(interaction.user.voice.channel)
			await interaction.response.send_message(f'{lan.translate(lang, "Me he movido a tu canal de voz. ¡Aquí estoy!")}')
		return interaction.guild.voice_client
	#else:
	#	message = "No estás conectado a un canal de voz."
	#	err = True
	if err:
		await interaction.response.send_message(f'{lan.translate(lang, "lo siento")}, {message}')
		return
	if interaction.user.voice is not None:
		await interaction.response.send_message(f'{lan.translate(lang, "¡Conectado al canal de voz!")}')
		await client.change_presence(
			activity=discord.Activity(type=discord.ActivityType.playing, name=lan.translate(lang, "TTS en canal de voz")),
			status=discord.Status.dnd
		)
		return await interaction.user.voice.channel.connect()

@client.tree.command(description=lan.translate(lang, "WorldTTS en canal de voz."))
@app_commands.describe(
	voice=lan.translate(lang, 'El nombre de una voz que se desea usar. Para obtener una lista, por favor usa /list.'),
	speaker=lan.translate(lang, 'si este modelo tiene varios hablantes, puedes establecer el id del hablante. 0, 1, 2...'),
	rate=lan.translate(lang, 'Cambia la velocidad de la voz (opcional). 1 normal, 0.5 más rápido, 2 más lento.'),
	pitch=lan.translate(lang, '(opcional) cambia el tono de la voz. 0.50 más grabe, 1 normal, 2 más agudo.'),
	text=lan.translate(lang, 'texto a sintetizar.')
)
async def wtts_vc(
	interaction: discord.Interaction,
	synthesizer: Literal ["forward", "piper", "RHVoice"],
	voice: str,
	speaker: Optional[int] = 0,
	rate: Optional[float] = 1.00,
	pitch: Optional[float] = 1.00,
	text: Optional[str] = lan.translate(lang, "Esta es una prueba.")
):
	# Voice client:
	if interaction.guild.voice_client is None:
		await interaction.response.send_message(f'{interaction.user.mention}, {lan.translate(lang, "No estoy en un canal de voz para hacer esto.")}')
	loop = asyncio.get_event_loop()
	await interaction.response.send_message(f'{lan.translate(lang, "Solicitud de texto a voz enviada por")} {interaction.user.mention}.\n{lan.translate(lang, "Iniciando...")}', ephemeral=True)
	if synthesizer == "forward":
		task = loop.create_task(
			forwardtaco.do_tts(
				voice, rate, pitch, 1.0, text, path, path_cache, cuda
			)
		)
	elif synthesizer == "piper":
		task = loop.create_task(
			piper_tts.piper_thread(
				voice,
				speaker,
				rate,
				pitch,
				text,
				path,
				path_cache,
				cuda
			)
		)
	elif synthesizer == "RHVoice":
		task = loop.create_task(
			rhvoice.do_tts(
				voice, rate, pitch, text, path_cache
			)
		)
	wav_filename = await task
	if wav_filename == -1:
		await interaction.channel.send(f'{lan.translate(lang, "¡Esta voz no existe! Por favor, usa /list para obtener una lista. La voz fue")}: {voice}.')
		return
	source = discord.PCMVolumeTransformer(
		discord.FFmpegPCMAudio(wav_filename)
	)
	#await interaction.guild.voice_client.play(source, after=lambda e: print(f'Player error: {e}'))
	await interaction.guild.voice_client.play(source)

@client.tree.command(description=lan.translate(lang, "Desconectarme del canal de voz."))
async def leave(interaction: discord.Interaction):
	vc = interaction.guild.voice_client
	await vc.disconnect()
	await interaction.response.send_message(f'{lan.translate(lang, "Desconectado del canal de voz. ¡Nos oímos pronto!")}')
	await client.change_presence(activity=None, status=None)

@client.tree.command(description=lan.translate(lang, "Subir modelo TTS"))
async def upload(
	interaction: discord.Interaction,
	synthesizer: Literal["piper", "RHVoice"]
):
	await interaction.response.send_modal(UI.Upload_TTS_model(synthesizer))
	# Refresh voice list, piper  in the future instead of refresh manually.:
	rhvoices = rhvoice.available_voices()
	if colab:
		print(lan.translate(lang, "Por favor, recuerda vaciar la papelera en tu Drive."))

def goodbye():
	global channel, bot_config
	config.write_bot_config(bot_config)
	#loop = asyncio.get_event_loop()
	#asyncio.run_coroutine_threadsafe(await channel.send(lan.translate(lang, "Dejaré de estar en ejecución. ¡Nos oímos pronto!")), loop)


if __name__ == "__main__":
	atexit.register(goodbye)
	client.run(bot_config["bot_token"])