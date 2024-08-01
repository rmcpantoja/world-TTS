import markdown
from markdown.extensions import tables
from bs4 import BeautifulSoup
import webbrowser
from typing import Optional
from .translator import *

def get_all_voices(content):
	voices = []
	md = markdown.Markdown(extensions=[tables.TableExtension()])
	html = md.convert(content)
	soup = BeautifulSoup(html, 'html.parser')
	for row in soup.find_all('tr'):
		cells = row.find_all('td')
		if cells:
			voices.append(cells[1].get_text())
	return voices

def get_paid_voices(
	language_handler: Translator,
	language: str,
	content: str
):
	voices = []
	md = markdown.Markdown(extensions=[tables.TableExtension()])
	html = md.convert(content)
	soup = BeautifulSoup(html, 'html.parser')
	for row in soup.find_all('tr'):
		cells = row.find_all('td')
		if cells:
			current_voice = cells[0].get_text()
			if is_paid_voice(current_voice):
				voices.append(current_voice)
	return voices

def get_paid_voice(
	language_handler: Translator,
	language: str,
	content: str,
	voice_command: str
):
	md = markdown.Markdown(extensions=[tables.TableExtension()])
	html = md.convert(content)
	soup = BeautifulSoup(html, 'html.parser')
	for row in soup.find_all('tr'):
		cells = row.find_all('td')
		if cells:
			current_voice = cells[0].get_text()
			current_voice_command = cells[1].get_text()
			if is_paid_voice(current_voice) and current_voice_command == voice_command:
				return current_voice
	return None

def is_paid_voice(
	voice: str,
	config: Optional[dict]={"paid_url": "https://paypal.me/Xx_Nessu_xX"},
	open: Optional[bool]=False
):
	if "(paid)" in voice:
		resp = True
	else:
		resp = False
	if not open:
		return resp
	else:
		return resp, webbrowser.open(config["paid_url"])

def has_paid_this_voice(
	config: dict,
	language_handler: Translator,
	language: str,
	voice: str,
	user: str,
):
	if not is_paid_voice(voice, config):
		raise Exception("This is not a paid voice.")
	try:
		if is_paid_voice(voice, config) and config["paid_voices"][voice][user]:
			return True
		else:
			return False
	except KeyError:
		return False

def list_info(
	language_handler: Translator,
	language: str,
	content: str
):
	globalcounter = 0
	languages = []
	md = markdown.Markdown(extensions=[tables.TableExtension()])
	html = md.convert(content)
	soup = BeautifulSoup(html, 'html.parser')
	current_language = None
	voices = []
	paid_voices = []
	for row in soup.find_all(['h2', 'tr']):
		if row.name == 'h2':
			if current_language is not None:
				languages.append({
					'language': current_language,
					'n_voices': len(voices),
					'voices': voices,
					'paid_voices': paid_voices
				})
			current_language = row.get_text(strip=True)
			voices = []
			paid_voices = []
		elif row.name == 'tr':
			cells = row.find_all('td')
			if cells:
				voice_name = cells[0].get_text(strip=True)
				if not is_paid_voice(voice_name):
					voices.append(voice_name)
				else:
					paid_voices.append(voice_name)
				globalcounter = globalcounter+1
	if current_language is not None:
		languages.append({
			'language': current_language,
			'n_voices': len(voices),
			'voices': voices,
			'paid_voices': paid_voices
		})
	return globalcounter, languages


def search(
	language_handler: Translator,
	language: str,
	content: str,
	text: str
):
	md = markdown.Markdown(extensions=[tables.TableExtension()])
	html = md.convert(content)
	soup = BeautifulSoup(html, 'html.parser')
	resultados = []
	for row in soup.find_all('tr'):
		cells = row.find_all('td')
		if cells:
			if text.lower() in cells[0].get_text().lower():
				resultados.append(
					f'{cells[0].get_text()} {language_handler.translate(language, "por")} {cells[3].get_text()}, {language_handler.translate(language, "comando")}: {cells[1].get_text()}'
				)
	resultados_string = '\n'.join(resultados)
	if resultados_string.strip():
		return resultados_string
	else:
		return -1
