import data
import dungeonmap
import functools
import pygame
import resources
import os

class entity():
	def __init__(self, dungeon, name, pos):
		self.dungeon = dungeon
		self.name = name
		self.pos = pos
		self.data = data.database(dungeonmap.entityfolder, self.name)
		self.selected = False
		self.selectionimage, rect = resources.load_image("gui", "selection.png") #@UnusedVariable
		self.refresh()
		
	def refresh(self):
		self.icon, rect = resources.load_image(os.path.join(dungeonmap.entityimgfolder, self.name), "icon.png") #@UnusedVariable
		self.icon = pygame.transform.scale(self.icon, (dungeonmap.entitysize[0], dungeonmap.entitysize[1]))
		
	def move(self, pos):
		self.pos = pos
		
	def remove(self):
		self.dungeon.removeentity(self)
		
	def draw(self, screen):
		screenpos = self.dungeon.coordstopos(self.pos)
		if self.dungeon.mode == "edit":
			screen.blit(self.icon, screenpos)
		if self.selected:
			screen.blit(self.selectionimage, screenpos)
			
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