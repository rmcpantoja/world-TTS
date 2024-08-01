#Administration support

import json
import os

class Admin:
	def __init__(self, file="admins.json"):
		self.admin_file = file
		self.admins = None
		if not os.path.exists(self.admin_file):
			raise FileNotFoundError(f"Admin file '{self.admin_file}' is not found.")
		else:
			self.load(True)

	def load(self, reload=False):
		if self.admins is None or reload:
			try:
				with open(self.admin_file, "r") as admins_handler:
					admins_list = admins_handler.read()
				self.admins = json.loads(admins_list)
			except FileNotFoundError:
				raise Exception("Admin file doesn't exists.")
			except json.JSONDecodeError:
				raise Exception("Error decoding the admin file. Please check your sintax.")
	# Moderation control:
	def is_admin(self, user):
		if self.admins is None:
			raise Exception("You must to load admins list. Please use admin_class.load()")
		return user in self.admins and self.admins[user]

	def add_admin(self, user):
		if self.admins is None:
			raise Exception("You must to load admins list. Please use admin_class.load()")
		if user in self.admins:
			raise Exception("This user is already an admin.")
		self.admins[user] = True
		with open(self.admin_file, "w") as admins_handler:
			json.dump(self.admins, admins_handler)
		return True

	def uncheck_admin(self, user):
		if self.admins is None:
			raise Exception("You must to load admins list. Please use admin_class.load()")
		if user not in self.admins:
			raise Exception("User not found.")
		self.admins[user] = False
		with open(self.admin_file, "w") as admins_handler:
			json.dump(self.admins, admins_handler)
		return True
