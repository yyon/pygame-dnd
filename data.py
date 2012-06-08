import os

datafolder = "data"

def get_data(folder, filename):
	filename = os.path.join(datafolder, folder, filename)
	if not os.path.exists(filename):
		open(filename, "w").close()
	f = open(filename, "r")
	return f.read()
	f.close()

def set_data(data, folder, filename):
	filename = os.path.join(datafolder, folder, filename)
	f = open(filename, "w")
	f.write(data)
	f.close()
	
def fullname(folder, name):
	return os.path.join(datafolder, folder, name)

class database():
	def __init__(self, folder, filename):
		self.folder = folder
		self.filename = filename
		self.load()
	
	def load(self):
		self.text = get_data(self.folder, self.filename)
		self.lines = self.text.split("\n")
		self.data = {}
		for line in self.lines:
			if line != "":
				dataline = line.split("=")
				variable = dataline[0]
				value = dataline[1]
				self.data[variable] = value
	
	def reverseget(self, var, default=None):
		self.reversedata = {}
		for variable in self.data:
			value = self.data[variable]
			self.reversedata[value] = variable
		try:
			return self.reversedata[var]
		except:
			if default == None:
				try:
					default = int(variable) + 1
				except UnboundLocalError:
					default = 0
				self.set(default, var)
			return default
	
	def get(self, variable, default=None):
		try:
			value = self.data[variable]
			if value == "True":
				value = True
			elif value == "False":
				value = False
			if ":" in value:
				value = value.split(":")
			return value
		except:
			return default
		
	def set(self, variable, value):
		self.data[variable] = value
	
	def tostring(self):
		string = ""
		for index, variable in enumerate(self.data):
			value = self.data[variable]
			if value == True and isinstance(value, (bool)):
				value = "True"
			elif value == False and isinstance(value, (bool)):
				value = "False"
			if isinstance(value, (list)):
				value = ":".join(value)
			string += str(variable) + "=" +str(value) + "\n"
		return string
	
	def write(self):
		set_data(self.tostring(), self.folder, self.filename)