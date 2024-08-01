# Blacklisted words
import base64

def load_blacklisted_words(file_path="words.dat"):
	with open(file_path, "r") as listed_words:
		data = listed_words.read()
	words = base64.b64decode(data).decode("utf-8")
	return set(words.splitlines())

def contains_blacklisted_words(text, blacklisted_words):
	# Eatch blacklisted words/comments are separated in lines
	text = text.lower()
	for word in blacklisted_words:
		if word.lower() in text:
			return True, word
	return False, None
