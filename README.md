# WorldTTS

This is a new, modern Discord bot. It allows you to use custom TTS systems in any place.

## Bot features

* Multilingual: the bot's interface and voices what you want to use can be multilingual.
* Multi-synthesizer: you can use multiple speech synthesizers with different voices to play. Mainly supports [piper](https://github.com/rhasspy/piper), then other synthesizers (see the section).
* AutoTTS: have the bot automatically generate audio when someone types a message, instead of typing command manually to generate TTS content.
* Moderation: This bot provides management control to monitor whether the text-to-speech content being generated is appropriate or not.

### List of synthesizers

The bot, outside piper, supports these following speech synthesizers. Each one has its own features. However, we try to make the use of all speech synthesizers supported in this bot work globally anywhere.

* [⏩ForwardTacotron](https://github.com/as-ideas/ForwardTacotron), AI. Controllable TTS with robustness and customization of comon synthesis parametters. It is inspired in fast speech.
* [🚀RHVoice](https://github.com/RHVoice/RHVoice), non-AI. a free and open-source speech synthesizer with voices built using recordings of natural speech. It is fastest and controllable.

## Installation

1. Clone the repo:

```
https://github.com/rmcpantoja/world-TTS
```

2. Optionally, create a virtual env for this project.

3. Install Python requirements.

```
cd world-TTS
pip install -r "requirements - bot.txt"
```

4. Run the bot

Before running, create a new app in your [discord's developper portal](https://discord.com/developers/applications). Set permissions to `administrator`, and get a token key. Then, please save the token, because the bot will need it.
Also, you'll need to enhable developer mode in Discord to get server and channel ids.

To run, type:

```
python discordbot.py
```

At the first run, a setup wizard will open and install your bot into your newly created app. Please fill these fields:

* The app's token, the one you saved in the app creation process.
* Server ID, You can do it by right clicking on your server, selecting the option `get server id`.
* Your id, to send moderation reports and more. You assume responsibility for taking necessary action based on the TTS content your members are generating, if content moderation is enabled (it is by default) (see usage).
* Language, for bot User Interface.

5. Get voices for your bot.

Each synthesizer have paths to his voices.
* ForwardTacotron - ftvoices
* Piper - voices/language-voice-quality
* RHVoice - rhvoice/voices
	* Aditionally, rhvoices/languages/language to set up a new language.

## Usage

### Standard commands
* /list: Gets a full list of all available voices.
* /search: Shows the list of voices found in the search term you will type.
* /info: About the bot, voices and languages.
* /mcard: Shows the model card for a specified voice command.
* /wtts: Make a text-to-speech request using any synthesizer by typing the voice name, and extra synth options as speaker, rate and pitch, and the text to synthesize. To use decimal numbers in rate and pitch options, you need to type the comma as a separator instead of a dot.
* /autotts: toggle autoTTS to a channel or yourself. When autoTTS is enabled, TTS content will be auto-generated with a specific voice or by choosing a voice yourself.
* /autotts_setup: setup autoTTS for a channel or for yourself by specifying a voice that can be used by default.
* /join: joins the bot to your voice channel.
* /wtts_vc: same as /wtts but to play TTS in the voice channel set in /join.
* /leave: Disconnect the bot from the voice channel.
* /upload: Uploads a TTS model through a form. Just press enter and this will be shown to you.

### Admin commands:

These commands can be typed in any chat, even in a private message to the bot. It serves to control the administration stuff.
* !admin: makes someone as an administrator. This should be the username displayed on discord. This can be someone interacting from Direct Messages or from a server.
* !mod: Turn general and TTS content moderation on or off. When this is enabled, any content containing profanity will be blocked and the user and a user responsible for receiving reports will be warned to take actions.
* !stats: shows statistics on how content moderation doing is, if it's enabled.
* !delstats: deletes moderation counts and actions, both general content and TTS content.
* !pay (!pay voice_command discord_username): This buys a voice, if the user purchased one of our paid voices and an administrator received payment.
* !cleanup: Clears the audio cache. This is useful when there are a lot of TTS requests going up over a period of time. As long as they aren't very popular servers or /wtts or /wtts_vc does not have massive uses, this should not be used many times.

## Acknowledgements

* [Discord.py](https://github.com/Rapptz/discord.py), the head of this project.
* [Piper, a fast an local, neurol Text-To-Speech](https://github.com/rhasspy/piper), also the [NVDA driver](https://github.com/mush42/sonata-nvda) for piperTTS support.
* [RHVoice Python binding](https://github.com/Aculeasis/rhvoice-proxy), and the [official project](https://github.com/RHVoice/RHVoice) for the RHVoiceTTS support.