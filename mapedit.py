from gui import * #@UnusedWildImport
import dungeonmap #@UnusedWildImport
import entityeditor
import shutil
import data
import copy

def closeeditor():
	objlists.dungeonmap.mode = None
	for window in objlists.editorwindows:
		Window.close(window)
	objlists.editorwindows = []
	objlists.dungeonmap.savemap()

def openmap():
	mapselector(openeditor)

def openeditor(name):
	objlists.dungeonmap.mode = "edit"
	objlists.dungeonmap.openmap(name)
	tileswindow = tiles()
	objlists.editorwindows.append(tileswindow)
	optionswindow = options()
	objlists.editorwindows.append(optionswindow)
	entitieslist = entitieswindow()
	objlists.editorwindows.append(entitieslist)

class options(Window):
	def __init__(self):
		Window.__init__(self, "Edit Options", scrollbar=True)
		
		self.showgrid = checkbox(self, "Show Grid", clickmethod = self.togglegrid)
		self.showgrid.checked = True
		self.pack(self.showgrid)
		
		self.expandlabel = label(self, "Expand Map")
		self.pack(self.expandlabel)
		
		self.expandup = button(self, "/\\", functools.partial(self.expand, "up"))
		self.pack(self.expandup)

		self.expandleft = button(self, "<", functools.partial(self.expand, "left"))
		self.pack(self.expandleft)

		self.expandright = button(self, ">", functools.partial(self.expand, "right"))
		self.pack(self.expandright, "right")

		self.expanddown = button(self, "\\/", functools.partial(self.expand, "down"))
		self.pack(self.expanddown)
		
		self.contractlabel = label(self, "Contract Map")
		self.pack(self.contractlabel)
		
		self.contractup = button(self, "\\/", functools.partial(self.contract, "up"))
		self.pack(self.contractup)

		self.contractleft = button(self, ">", functools.partial(self.contract, "left"))
		self.pack(self.contractleft)

		self.contractright = button(self, "<", functools.partial(self.contract, "right"))
		self.pack(self.contractright, "right")

		self.contractdown = button(self, "/\\", functools.partial(self.contract, "down"))
		self.pack(self.contractdown)
		
		self.togglegrid()
		
	def expand(self, direction):
		objlists.dungeonmap.expand(direction)
		
	def contract(self, direction):
		objlists.dungeonmap.contract(direction)
		
	def togglegrid(self):
		objlists.dungeonmap.showgrid = self.showgrid.checked

	def close(self):
		closeeditor()
	
class tiles(Window):
	def __init__(self):
		Window.__init__(self, "Tiles", scrollbar=True)
		
		self.tilebuttons = {}
		
		self.refreshtiles()
		
	def refreshtiles(self):
		self.addtilebutton = button(self, "Add Tile", self.addtile)
		self.pack(self.addtilebutton)
		
		for tile in os.listdir(os.path.join(resources.resfolder, dungeonmap.tileimgfolder)):
			tilename = ".".join(tile.split(".")[:-1])
			
			imgbutton = picturebox(self, dungeonmap.tileimgfolder, tile, clickevent=functools.partial(self.selecttile, tilename), size=dungeonmap.actualtilesize)
			self.tilebuttons[tilename]=imgbutton
			self.pack(imgbutton)
			
			group = controlgroup(self)
			
			editbutton = picturebox(self, "gui", "edit.png", clickevent=functools.partial(self.edittile, tilename), size=[25,25])
			group.pack(editbutton)

			editbutton = picturebox(self, "gui", "rename.png", clickevent=functools.partial(self.rename, tilename), size=[25,25])
			group.pack(editbutton, "right")

			copybutton = picturebox(self, "gui", "copy.png", clickevent=functools.partial(self.startcopytile, tilename), size=[25,25])
			group.pack(copybutton, "right")

			delbutton = picturebox(self, "gui", "delete.png", clickevent=functools.partial(self.deletetile, tilename), size=[25,25])
			group.pack(delbutton, "right")
			
			namelabel = label(self, tilename)
			group.pack(namelabel)
			
			self.pack(group, "right")
			
		objlists.dungeonmap.refreshtiles()
	
	def selecttile(self, tile):
		objlists.dungeonmap.selectedtile = tile #@UnusedVariable
		objlists.dungeonmap.changeeditmode("tile")
	
	def addtile(self):
		inputbox("Tile Name", "Enter Tile Name", self.finishaddtile)
	
	def finishaddtile(self, name):
		namedatabase = data.database("", "names")
		tilenames = namedatabase.get("tiles", [])
		tilenames.append(name)
		namedatabase.set("tiles", tilenames)
		namedatabase.write()
				
		self.edittile(name)
	
	def startcopytile(self, tile):
		inputbox("Tile Name", "Enter new tile name", functools.partial(self.finishcopytile, tile))
	
	def finishcopytile(self, oldtile, newtile):
		shutil.copy(resources.fullname(dungeonmap.tileimgfolder, oldtile+".png"), resources.fullname(dungeonmap.tileimgfolder, newtile+".png"))
		shutil.copy(data.fullname(dungeonmap.tilefolder, oldtile), data.fullname(dungeonmap.tilefolder, newtile))

		namedatabase = data.database("", "names")
		tilenames = namedatabase.get("tiles", [])
		tilenames.append(newtile)
		namedatabase.set("tiles", tilenames)
		namedatabase.write()
		
		self.refreshlist()
		
	def rename(self, tile):
		inputbox("Tile Name", "Enter new tile name", functools.partial(self.newname, tile))
	
	def newname(self, oldname, newname):
		shutil.move(resources.fullname(dungeonmap.tileimgfolder, oldname+".png"), resources.fullname(dungeonmap.tileimgfolder, newname+".png"))
		shutil.move(data.fullname(dungeonmap.tilefolder, oldname), data.fullname(dungeonmap.tilefolder, newname))
		objlists.dungeonmap.renametile(oldname, newname)

		namedatabase = data.database("", "names")
		tilenames = namedatabase.get("tiles", [])
		tilenames[tilenames.index(oldname)] = newname
		namedatabase.set("tiles", tilenames)
		namedatabase.write()
		
		self.refreshlist()
	
	def deletetile(self, tile):
		os.remove(resources.fullname(dungeonmap.tileimgfolder, tile+".png"))
		os.remove(data.fullname(dungeonmap.tilefolder, tile))
		if objlists.dungeonmap.selectedtile == tile:
			objlists.dungeonmap.selectedtile = None
		
		namedatabase = data.database("", "names")
		tilenames = namedatabase.get("tiles", [])
		tilenames.remove(tile)
		namedatabase.set("tiles", tilenames)
		namedatabase.write()

		self.refreshlist()
	
	def edittile(self, name):
		edittile(name, self)
	
	def refreshlist(self):
		self.unpack()
		self.refreshtiles()
	
	def close(self):
		closeeditor()
	
	def draw(self, screen):
		Window.draw(self, screen)
		if objlists.dungeonmap.selectedtile != None:
			pygame.draw.rect(self.area, pygame.color.Color("blue"), self.tilebuttons[objlists.dungeonmap.selectedtile], 2)

class entitieswindow(Window):
	def __init__(self):
		Window.__init__(self, "Entities", scrollbar=True)
		
		self.entitybuttons = {}
		
		self.refreshentities()
		
	def refreshentities(self):
		self.addtilebutton = button(self, "Add Entity", self.addentity)
		self.pack(self.addtilebutton)

		imgbutton = picturebox(self, "gui", "removeentity.png", clickevent=functools.partial(self.selectentity, None), size=dungeonmap.actualentitysize)
		self.entitybuttons[None]=imgbutton
		self.pack(imgbutton)
		
		for entity in os.listdir(os.path.join(data.datafolder, dungeonmap.entityfolder)):
			imgbutton = picturebox(self, os.path.join(dungeonmap.entityimgfolder, entity), "icon.png", clickevent=functools.partial(self.selectentity, entity), size=dungeonmap.actualentitysize)
			self.entitybuttons[entity]=imgbutton
			self.pack(imgbutton)
			
			group = controlgroup(self)

			editbutton = picturebox(self, "gui", "edit.png", clickevent=functools.partial(self.editentity, entity), size=[25,25])
			group.pack(editbutton)

			editbutton = picturebox(self, "gui", "rename.png", clickevent=functools.partial(self.rename, entity), size=[25,25])
			group.pack(editbutton, "right")

			typebutton = picturebox(self, "gui", "type.png", clickevent=functools.partial(self.changetype, entity), size=[25,25])
			group.pack(typebutton, "right")
			
			copybutton = picturebox(self, "gui", "copy.png", clickevent=functools.partial(self.startcopyentity, entity), size=[25,25])
			group.pack(copybutton, "right")

			delbutton = picturebox(self, "gui", "delete.png", clickevent=functools.partial(self.deleteentity, entity), size=[25,25])
			group.pack(delbutton, "right")
			
			name = label(self, entity)
			group.pack(name)
			
			self.pack(group, "right")

		objlists.dungeonmap.refreshentities()
	
	def changetype(self, entity):
		entityeditor.entitytypeselector(functools.partial(self.finishchangetype, entity))
		
	def finishchangetype(self, entity, entitytype):
		database = data.database(dungeonmap.entityfolder, entity)
		database.set("type", entitytype)
		database.write()
	
	def selectentity(self, entity):
		objlists.dungeonmap.selectedentity = entity #@UnusedVariable
		objlists.dungeonmap.changeeditmode("entity")
	
	def addentity(self):
		inputbox("Entity Name", "Enter Entity Name", self.finishaddentity)
		
	def finishaddentity(self, name):
		os.makedirs(resources.fullname(dungeonmap.entityimgfolder, name))
		
		namedatabase = data.database("", "names")
		entitynames = namedatabase.get("entities", [])
		entitynames.append(name)
		namedatabase.set("entities", entitynames)
		namedatabase.write()

		self.editentity(name)
		
		self.refreshlist()

	def rename(self, tile):
		inputbox("Entity Name", "Enter new entity name", functools.partial(self.newname, tile))
	
	def newname(self, oldentity, newentity):
		shutil.copytree(resources.fullname(dungeonmap.entityimgfolder, oldentity), resources.fullname(dungeonmap.entityimgfolder, newentity))
		shutil.rmtree(resources.fullname(dungeonmap.entityimgfolder, oldentity))
		shutil.move(data.fullname(dungeonmap.entityfolder, oldentity), data.fullname(dungeonmap.entityfolder, newentity))
		objlists.dungeonmap.renameentity(oldentity, newentity)
		
		namedatabase = data.database("", "names")
		entitynames = namedatabase.get("entities", [])
		entitynames[entitynames.index(oldentity)] = newentity
		namedatabase.set("entities", entitynames)
		namedatabase.write()
		
		self.refreshlist()
	
	def startcopyentity(self, tile):
		inputbox("Entity Name", "Enter new entity name", functools.partial(self.finishcopyentity, tile))
	
	def finishcopyentity(self, oldentity, newentity):
		shutil.copytree(resources.fullname(dungeonmap.entityimgfolder, oldentity), resources.fullname(dungeonmap.entityimgfolder, newentity))
		shutil.copy(data.fullname(dungeonmap.entityfolder, oldentity), data.fullname(dungeonmap.entityfolder, newentity))
		
		namedatabase = data.database("", "names")
		entitynames = namedatabase.get("entities", [])
		entitynames.append(newentity)
		namedatabase.set("entities", entitynames)
		namedatabase.write()
		
		self.refreshlist()
	
	def deleteentity(self, entity):
		shutil.rmtree(resources.fullname(dungeonmap.entityimgfolder, entity))
		os.remove(data.fullname(dungeonmap.entityfolder, entity))
		if objlists.dungeonmap.selectedentity == entity:
			objlists.dungeonmap.selectedentity = None

		namedatabase = data.database("", "names")
		entitynames = namedatabase.get("entities", [])
		entitynames.remove(entity)
		namedatabase.set("entities", entitynames)
		namedatabase.write()
		
		self.refreshlist()
	
	def editentity(self, name):
		database = data.database(dungeonmap.entityfolder, name)
		entityeditor.editors[database.get("type", dungeonmap.entitytypes[0])](name, self)
	
	def refreshlist(self):
		self.unpack()
		self.refreshentities()
	
	def close(self):
		closeeditor()
	
	def draw(self, screen):
		Window.draw(self, screen)
		if objlists.dungeonmap.editmode == "entity":
			pygame.draw.rect(self.area, pygame.color.Color("blue"), self.entitybuttons[objlists.dungeonmap.selectedentity], 2)
		
class edittile(Window):
	def __init__(self, tilename, tilewindow, scrollbar=True):
		Window.__init__(self, tilename)
		
		self.name = tilename
		self.originalname = copy.copy(self.name)
		
		self.tilewindow = tilewindow

		self.database = data.database(dungeonmap.tilefolder, self.name)
		
#		self.namelabel = label(self, "Name: " + self.name)
#		self.pack(self.namelabel)
				
		self.imagebox = picturebox(self, dungeonmap.tileimgfolder, self.name+".png", size=[50,50])
		self.pack(self.imagebox)
		
		self.testcheck = checkbox(self, "test value")
		self.testcheck.checked = self.database.get("test", True)
		self.pack(self.testcheck)
		
	def close(self):
		self.database.set("test", self.testcheck.checked)
		self.database.write()
		Window.close(self)
		self.tilewindow.refreshlist()
	
	def refresh(self):
		self.imagebox.makesprite()
		self.namelabel.text = self.name
		
class mapselector(Window):
	def __init__(self, method):
		Window.__init__(self, "Maps", scrollbar=True)
		
		self.method = method
		
		self.entitybuttons = {}
		
		self.refreshmaps()
		
	def refreshmaps(self):
		self.addtilebutton = button(self, "New Map", self.newmap)
		self.pack(self.addtilebutton)
		
		for mapname in os.listdir(os.path.join(data.datafolder, dungeonmap.mapfolder)):
			mapbutton = button(self, mapname, functools.partial(self.openmap, mapname))
			self.pack(mapbutton)
			
			editbutton = picturebox(self, "gui", "edit.png", clickevent=functools.partial(self.editmap, mapname), size=[25,25])
			self.pack(editbutton, "right")

			copybutton = picturebox(self, "gui", "copy.png", clickevent=functools.partial(self.startcopymap, mapname), size=[25,25])
			self.pack(copybutton, "right")

			delbutton = picturebox(self, "gui", "delete.png", clickevent=functools.partial(self.deletemap, mapname), size=[25,25])
			self.pack(delbutton, "right")
	
	def newmap(self):
		inputbox("Map Name", "Enter new map name", self.editmap)
	
	def startcopymap(self, tile):
		inputbox("Map Name", "Enter new map name", functools.partial(self.finishcopymap, tile))
	
	def finishcopymap(self, oldmap, newmap):
		shutil.copy(data.fullname(dungeonmap.mapfolder, oldmap), data.fullname(dungeonmap.mapfolder, newmap))
#		shutil.copy(data.fullname(dungeonmap.mappropertiesfolder, oldmap), data.fullname(dungeonmap.mappropertiesfolder, newmap))
#		shutil.copy(data.fullname(dungeonmap.mapentityfolder, oldmap), data.fullname(dungeonmap.mapentityfolder, newmap))
		self.refreshlist()
	
	def deletemap(self, mapname):
		os.remove(data.fullname(dungeonmap.mapfolder, mapname))
#		os.remove(data.fullname(dungeonmap.mappropertiesfolder, mapname))
#		os.remove(data.fullname(dungeonmap.mapentityfolder, mapname))
		self.refreshlist()
		
	def editmap(self, name):
		openeditor(name)
		self.close()
	
	def openmap(self, name):
		self.method(name)
		self.close()
	
	def refreshlist(self):
		self.unpack()
		self.refreshmaps()
