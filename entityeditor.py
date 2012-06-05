from gui import * #@UnusedWildImport
import functools
import data

entitytypes = ["npc"]

class entitytypeselector(Window):
	def __init__(self, method):
		Window.__init__(self, "Entity Type", scrollbar=True)
		
		self.method = method
		
		self.refreshentities()
		
	def refreshentities(self):
		for entitytype in entitytypes:
			b = button(self, entitytype, functools.partial(self.selectentity, entitytype))
			self.pack(b)
			
	def selectentity(self, entity):
		self.method(entity)

class npceditor(Window):
	def __init__(self, entity):
		Window.__init__(self)
		
		self.entity = entity
		
		self.database = data.database("entities", self.entity)