import data
import dungeonmap
import functools

class entity():
	def __init__(self, dungeon, name, pos):
		self.dungeon = dungeon
		self.name = name
		self.pos = pos
		self.data = data.database(dungeonmap.entityfolder, self.name)
	
	def move(self, pos):
		self.pos = pos
	
	def remove(self):
		self.dungeon.removeentity(self)
	
	def getrightclickitems(self):
		items = []
		
		if self.dungeon.mode == "edit":
			items.append(["remove", self.remove])
		
		return items
	
	def getselectedrightclickitems(self, pos):
		items = []
		
		items.append(["move here", functools.partial(self.move, pos)])
		
		return items

class npc(entity):
	def __init__(self, dungeon, name, pos):
		entity.__init__(self, dungeon, name, pos)
		
	def getrightclickitems(self):
		items = []
		
		for item in entity.getrightclickitems(self):
			items.append(item)
		
		return items
	
	def getselectedrightclickitems(self, pos):
		items = []
		
		for item in entity.getselectedrightclickitems(self, pos):
			items.append(item)
		
		return items