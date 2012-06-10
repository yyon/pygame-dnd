import os
import json

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
	print "writing:", data
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
		print "read:", self.text
		if self.text != "":
			self.data = json.loads(self.text)
			print "interpreted as", self.data
		else:
			self.data = {}
	
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
			return value
		except:
			return default
		
	def set(self, variable, value):
		self.data[variable] = value
	
	def tostring(self):
		return json.dumps(self.data)
	
	def write(self):
		set_data(self.tostring(), self.folder, self.filename)