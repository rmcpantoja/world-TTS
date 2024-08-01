from typing import Optional
from .translator import *

def no_longe_text(
	language_handler: Translator,
	text: str,
	language: Optional[str]="en",
	mode: Optional[int]=1,
	limit: Optional[int]=1500
):
	text_len = len(text)
	if text_len > limit:
		if mode == 1:
			text = language_handler.translate(language, "Texto largo.")
		elif mode == 2:
			text = text[:limit-3]+"..."
		else:
			raise Exception(language_handler.translate(language, "Invalid mode."))
	return text