import pygame #@UnusedImport
from pygame.locals import * #@UnusedWildImport
from gui import * #@UnusedWildImport
import numpy
import data
import copy

actualtilesize = [50, 50]
tilesize = [50, 50]

tilefolder = "tiles"
tileimgfolder = "tile"

mapfolder = "maps"

actualentitysize = [50, 50]
entitysize = [50, 50]

entityfolder = "entities"
entityimgfolder = "entities"

class Map(pygame.Surface):
	def __init__(self, area):
		pygame.Surface.__init__(self, (screensize[0], screensize[1]))
		self.area = area
		self.area.resize(screensize)
		self.window = self.area.window
		self.rect = clickRect(self.area, self.get_rect().left, self.get_rect().top, self.get_rect().width, self.get_rect().height, 1, self.click, True, True)

		self.background = pygame.Surface((self.rect.width, self.rect.height))
		self.background.convert()
		self.background.fill((0,0,0))
		
		self.topleft = numpy.array([0,0])
		
		self.width = 0
		self.height = 0
		
		self.mapwidth = 10
		self.mapheight = 10
		
		self.rightclickbuffer = 2
		
		self.newmap()
		
		self.area.objects.append(self)
		
		self.mapname = None

		self.mode = None
		self.editmode = "tile"
		
		self.selectedtile = None
		self.showgrid = False
		
		self.selectedentity = None
		
		self.tiles = {}
		self.entityicons = {}
		self.refreshtiles()
		self.refreshentities()
		
	def changeeditmode(self, newmode):
		self.editmode = newmode
		if newmode == "tile":
			self.selectedentity = None
		elif newmode == "entity":
			self.selectedtile = None
		
	def newmap(self):
		self.map = []
		self.entities = []
		for y in range(self.mapheight): #@UnusedVariable
			self.map.append([])
			for x in range(self.mapwidth): #@UnusedVariable
				self.map[y].append(self.blanktile())
		
	def expand(self, direction):
		if direction == "up":
			self.mapheight += 1
			self.map.insert(0, [self.blanktile()]*self.mapwidth)
			for index in range(len(self.entities)):
				self.entities[index][1][1] += 1
		elif direction == "down":
			self.mapheight += 1
			self.map.append([self.blanktile()]*self.mapwidth)
		elif direction == "left":
			self.mapwidth += 1
			for y in range(len(self.map)):
				self.map[y].insert(0, self.blanktile())
			for index in range(len(self.entities)):
				self.entities[index][1][0] += 1
		elif direction == "right":
			self.mapwidth += 1
			for y in range(len(self.map)):
				self.map[y].append(self.blanktile())
				
	def contract(self, direction):
		if direction == "up":
			if self.mapheight != 1:
				self.mapheight -= 1
				self.map.pop(0)
			for index, entity in enumerate(self.entities):
				self.entities[index][1][1] -= 1
		elif direction == "down":
			if self.mapheight != 1:
				self.mapheight -= 1
				self.map.pop(-1)
		elif direction == "left":
			if self.mapwidth != 1:
				self.mapwidth -= 1
				for y in range(len(self.map)):
					self.map[y].pop(0)
			for index, entity in enumerate(self.entities):
				self.entities[index][1][0] -= 1
		elif direction == "right":
			if self.mapwidth != 1:
				self.mapwidth -= 1
				for y in range(len(self.map)):
					self.map[y].pop(-1)
		
		entitiestoremove = []
		
		for index, entity in enumerate(self.entities):
			if not self.inbounds(self.entities[index][1]):
				entitiestoremove.append(entity)
		
		for entity in entitiestoremove:
			self.removeentity(entity)
		
	def blanktile(self):
		return "blank"
	
	def tilesprite(self, name):
		return name
		
	def click(self, event, position, dragstartpos):
		tilecoords = [int((position[0] - self.topleft[0]) / tilesize[0]), int((position[1] - self.topleft[1]) / tilesize[1])]
		if event.type == MOUSEBUTTONDOWN and event.button == 3:
			self.startdragpos = self.topleft
		if (event.type == MOUSEBUTTONDRAGGED or event.type == MOUSEBUTTONUP) and event.button == 3:
			vector = numpy.array(position) - numpy.array(dragstartpos)
			self.topleft = self.startdragpos + vector
			if event.type == MOUSEBUTTONUP:
				if abs(vector[0]) < self.rightclickbuffer and abs(vector[1]) < self.rightclickbuffer:
					if self.inbounds(tilecoords):
						self.rightclick(tilecoords)
		if (event.type == MOUSEBUTTONDRAGGED or event.type == MOUSEBUTTONDOWN) and event.button == 1:
			if self.inbounds(tilecoords):
				if self.mode == "edit":
					if self.editmode == "tile":
						if self.selectedtile != None:
							self.settile(self.selectedtile, tilecoords)
					elif self.editmode == "entity":
						if event.type == MOUSEBUTTONDOWN:
							if self.selectedentity != None:
								self.addentity(self.selectedentity, tilecoords)
							else:
								self.removeentityatposition(tilecoords)
	
	def inbounds(self, tilecoords):
		return ( tilecoords[0] >= 0 and tilecoords[1] >= 0 and tilecoords[0] < len(self.map[0]) and tilecoords[1] < len(self.map) )
	
	def rightclick(self, position):
		menuitems = []
		
		if self.getentities(position) != []:
			if self.mode == "edit":
				menuitems.append(["remove", functools.partial(self.removeentityatposition, position)])
		
		menu(menuitems)
	
	def nothing(self):
		pass
	
	def settile(self, tile, pos):
		try:
			self.map[pos[1]][pos[0]] = tile
		except IndexError:
			pass
		
	def getentities(self, pos):
		entities = []
		for otherentity in self.entities:
			if otherentity[1] == pos:
				entities.append(otherentity)
		return entities
		
	def addentity(self, entity, pos):
		if self.getentities(pos) == []:
			self.entities.append([entity, pos])
		
	def removeentityatposition(self, pos):
		entitiestoremove = []
		
		for entity in self.entities:
			if entity[1] == pos:
				entitiestoremove.append(entity)
		
		for entity in entitiestoremove:
			self.removeentity(entity)
	
	def removeentity(self, entity):
		self.entities.remove(entity)
			
	def renameentity(self, originalname, newname):
		for index, entity in self.entities:
			if entity[0] == originalname:
				self.entities[index][0] = newname
		
	def renametile(self, originalname, newname):
		for y in range(self.mapheight):
			for x in range(self.mapwidth):
				if self.map[y][x] == originalname:
					self.map[y][x] = newname
		self.refreshtiles()
		
	def refreshtiles(self):
		for tile in os.listdir(os.path.join(resources.resfolder, tileimgfolder)):
			tilename = ".".join(tile.split(".")[:-1])
			
			self.tiles[tilename], rect = resources.load_image(tileimgfolder, tilename + ".png")
			self.tiles[tilename] = pygame.transform.scale(self.tiles[tilename], (tilesize[0], tilesize[1]))
	
	def refreshentities(self):
		for entity in os.listdir(os.path.join(data.datafolder, entityfolder)):
			self.entityicons[entity], rect = resources.load_image(os.path.join(entityimgfolder, entity), "icon.png")
			self.entityicons[entity] = pygame.transform.scale(self.entityicons[entity], (entitysize[0], entitysize[1]))
	
	def update(self):
		self.width, self.height = self.area.rect.width, self.area.rect.height
		
	def draw(self, screen):
		self.blit(self.background, [0,0])
		gridy = range(max((0 - tilesize[1] - self.topleft[1])/tilesize[1]+1, 0), min((self.height - self.topleft[1])/tilesize[1]+1, self.mapheight))
		gridx = range(max((0 - tilesize[0] - self.topleft[0])/tilesize[0]+1, 0), min((self.width - self.topleft[0])/tilesize[0]+1, self.mapwidth))
		for y in gridy:#range(self.mapheight):
			posy = tilesize[1]*y + self.topleft[1]
			for x in gridx:#range(self.mapwidth):
				posx = tilesize[0]*x + self.topleft[0]
				tile = self.map[y][x]
#				if (posx+tilesize[0]) > 0 and (posy+tilesize[1] > 0) and posx < self.width and posy < self.height:
				self.blit(self.tiles[tile], [posx, posy])
				if self.mode == "edit" and self.showgrid == True:
					pygame.draw.rect(self, pygame.color.Color("white"), rect(posx, posy, tilesize[0], tilesize[1]), 1)
		for entity in self.entities:
			pos = [entity[1][0]*tilesize[0] + self.topleft[0], entity[1][1]*tilesize[1] + self.topleft[1]]
			if self.mode == "edit":
				self.blit(self.entityicons[entity[0]], pos)
		
		screen.blit(self, [0,0])
		
	def openmap(self, name):
		self.mapname = name

		mapdatabase = data.database(mapfolder, self.mapname)

		self.mapwidth = int(mapdatabase.get("width", self.mapwidth))
		self.mapheight = int(mapdatabase.get("height", self.mapheight))
		
		self.newmap()
		
		mapdata = mapdatabase.get("map", [[0]*self.mapwidth]*self.mapheight)#data.get_data(mapfolder, self.mapname)
		
		namedatabase = data.database("", "names")
		tilenames = namedatabase.get("tiles", [])
		
		if mapdata != "":
			for y, line in enumerate(mapdata):
				for x, tile in enumerate(line):
					try:
						tile = tilenames[int(tile)]
					except:
						tile = tilenames[0]
					self.map[y][x] = self.tilesprite(tile)
		
		entitynames = namedatabase.get("entities", [])
		
		mapentities = mapdatabase.get("entities", [])
		
		for entity in mapentities:
			entityposition = entity[1]
			try:
				entityname = entitynames[int(entity[0])]
			except:
				entityname = None
			if entityname != None:
				self.entities.append([entityname, entityposition])
		
		namedatabase.write()
	
	def savemap(self):
		if self.mapname != None:
			mapdatabase = data.database(mapfolder, self.mapname)
			
			namedatabase = data.database("", "names")
			
			tilenames = namedatabase.get("tiles", [])
			
			strmap = copy.deepcopy(self.map)
			
			for y, row in enumerate(strmap):
				for x, tile in enumerate(row):
					if not tile in tilenames:
						tilenames.append(tile)
						print "WARNING: tile did not exist"
					strmap[y][x] = str(tilenames.index(tile))
			
			entitynames = namedatabase.get("entities")
			if entitynames == None:
				entitynames = []
			
			entitylist = copy.deepcopy(self.entities)
			
			if entitylist == None:
				entitylist = []
			
			for entity in entitylist:
				if not entity[0] in entitynames:
					entitynames.append(entity[0])
					print "WARNING: entity did not exist"
				entity[0] = entitynames.index(entity[0])

			mapdatabase.set("map", strmap)
			
			mapdatabase.set("entities", entitylist)
			
			mapdatabase.set("width", self.mapwidth)
			mapdatabase.set("height", self.mapheight)
			
			namedatabase.set("tiles", tilenames)
			namedatabase.set("entities", entitynames)
			
			namedatabase.write()
			mapdatabase.write()

class mapwindow(Window):
	def __init__(self):
		Window.__init__(self, "Dungeon", 1000, 600, 100, 50)
		self.subsurface = Map(self.area)
		objlists.unfocusable.append(self)
		send_to_back(self)
	
	def update(self):
		Window.update(self)
		self.subsurface.update()
		
	def close(self):
		pass
		