import json
import os

def read_bot_config():
	if os.path.exists("bot.json"):
		with open("bot.json", "r", encoding="utf-8") as config:
			base = config.read()
		settings = json.loads(base)
	else:
		# first time:
		print("Hi! It looks like this is your first time running piperTTS bot. Let's setting up! :)")
		bot_token = input("What's your bot token?")
		server_id = input("Please give me the server ID to set up the bot commands.")
		general_channel = input("What's your channel id to set up bot messages? It's recommended to copy the *general* channel id.")
		your_id = input("As you're hosting this bot, what's your user ID? This is used to send you moderation reports, when people upload things and more.")
		languages = ["en", "es"]
		language = input(f"Select the bot's language, available options: {languages}")
		if not os.path.exists(f"lng/{language}.lang"):
			raise Exception("This language doesn't exists. If you need this language, please read the translation guide.")
		settings = {
			"language": language,
			"bot_token": bot_token,
			"bot_server_id": server_id,
			"bot_general_channel": general_channel,
			"user_id": your_id,
			"moderation": True,
			"welcome": True,
			"local_paths": {
				"ftvoices_path": os.path.join(os.getcwd(), "ftvoices"),
				"voices_path": os.path.join(os.getcwd(), "voices"),
				"rhvoices_path": os.path.join(os.getcwd(), "rhvoice", "voices"),
				"audio_cache_path": os.path.join(os.getcwd(), "audio_cache")
			},
			"colab_paths": {
				"ftvoices_path": "/content/drive/Othercomputers/My computer/ftvoices",
				"voices_path": "/content/drive/Othercomputers/My computer/voices",
				"rhvoices_path": "/content/drive/Othercomputers/My computer/rhvoice/voices",
				"audio_cache_path": "/content/piper_cache"
			}
		}
		write_bot_config(settings)
	return settings

def write_bot_config(cfg):
	with open("bot.json", "w", encoding="utf-8") as config:
		json.dump(cfg, config, indent=4)