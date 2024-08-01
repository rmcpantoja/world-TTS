# Navidad/Christmas
from . import searcher
import random

# For Christmass we need the voices:
with open("list.md", "r") as info_voices:
	list = info_voices.read()

def choose_voice():
	global list
	commands = buscador.get_all_voices(lista)
	any_command = random.choice(comandos)
	# Formatearlo:
	language = any_command[:2]
	return any_command, language

def setup_Christmass_message():
	database = {
		"en": [
			"We are already in December, and the lights are lighting up. May peace be with you!",
			"Jingle bell, jingle bell, jingle bell rock, Jingle bells swing and jingle bells ring, Snowing and blowing in bushels of fun. Now the jingle hop has begun.",
			"We wish you a merry Christmas, and a happy new year!",
			"Have a holly jolly Christmas!",
			"Gifts are good, but friends are forever. merry Christmas!",
			"Christmas is like candy; it slowly melts in your mouth sweetening every taste bud, making you wish it could last forever.",
			"I will honor Christmas in my heart, and try to keep it all the year.",
			"Gifts of time and love are surely the basic ingredients of a truly merry Christmas.",
			"Christmas Day is in our grasp, as long as we have hands to clasp! Christmas Day will always be, just as long, as we have we! Welcome Christmas while we stand, heart to heart, and hand in hand!",
			"Christmas magic is silent. You don’t hear it — you feel it, you know it, you believe it."
		],
		"es": [
			"Ya es diciembre, y las luces se van encendiendo. ¡Que la paz te acompañe!",
			"Cascabel, cascabel, lindo cascabel.",
			"Llega diciembre, llega navidad, llega el pabo. ¡Disfrútalo con tus seres queridos!",
			"No solo hoy, no solo mañana, sino todos los días del año, vive y dá lo mejor de ti y transmite esa sabiduría a los seres que te aman.",
			"Que la magia de la Navidad toque cada corazón con su luz, brindándonos paz, amor y un camino de estrellas hacia el nuevo año.",
			"No existe la Navidad ideal, solo la Navidad que usted decida crear como reflejo de sus valores, deseos queridos y tradiciones",
			"Los mejores deseos y regalos de la Navidad no son materiales, sino personales.",
			"La Navidad es una época repleta de magia en la que lo mejor no son los regalos, sino los momentos tan bellos que vivimos al lado de nuestros seres queridos.",
			"Honraré la Navidad en mi corazón y procuraré conservarla durante todo el año.",
			"Aunque se pierdan otras cosas a lo largo de los años, mantengamos la Navidad como algo brillante.",
			"Feliz Navidad, felices fiestas y feliz Año Nuevo. Que las estrellas guíen tu camino y alumbren tus pasos y que la felicidad sea una constante en tu vida.",
			"Que los logros de este año sean sólo las semillas para ser plantadas y que se cosechen con enorme éxito en los años venideros. ¡Feliz Navidad  y felices fiestas!",
			"Que la paz y la armonía celebrada en Navidad  estén presentes todos los días de tu año nuevo. ¡Feliz Navidad  y felices fiestas!",
			"¿Qué es la Navidad? Es la ternura del pasado, el valor del presente y la esperanza del futuro. Es el deseo sincero de que cada taza se puede llenar con bendiciones ricas y eternas, y de que cada camino nos lleve a la paz.",
			"Te deseo una feliz Navidad y un próspero año nuevo, que todos tus objetivos se logren y que disfrutes de tus sueños.",
			"Que la Navidad  te ayude a cumplir todos los sueños de tu corazón, que te traiga alegría para cada día del año nuevo y que puedas compartir todo esto con las personas especiales que forman parte de su vida. ¡Feliz Navidad!",
			"Que la paz, la armonía y la solidaridad reinen en nuestro corazón esta Navidad y el Año Nuevo que se acerca. ¡Felices fiestas!",
			"Te deseo que tu Navidad  sea luminosa, te traiga alegría, amor, paz y armonía.",
			"La fe y la esperanza son las luces que nos deben iluminar en este tiempo de reflexión. ¡Felices Fiestas!",
			"Que este año encuentres felicidad, salud, amor, dinero, paz y aquello que necesites, y todo lo que no encuentres, ¡búscalo en Google!"
		]
	}
	command, language = elige_voz()
	message_list = database.get(idioma, [])
	message = random.choice(message_list)
	return command, message