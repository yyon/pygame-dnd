import resources
import functools
import shlex, subprocess
import objlists

import os, pygame
from pygame.locals import * #@UnusedWildImport

if not pygame.mixer: print 'Warning, sound disabled'
if not pygame.font: print 'Warning, fonts disabled'

MOUSEBUTTONDRAGGED = 50
MOUSEBUTTONSTOPDRAG = 51
MOUSEBUTTONHOVER = 52
MOUSEBUTTONSTOPHOVER = 53

screensize = [1200, 700]

__author__ = "Ian Campbell"
__copyright__ = "GPL v3"

def is_click(event):
	return (event.type == MOUSEBUTTONDOWN and event.button == 1)

#a simple rectangle with a move function
class rect(pygame.Rect):
	def __init__(self, left, top=None, width=None, height=None):
		if top == None:
			pygame.Rect.__init__(self, left)
		else:
			pygame.Rect.__init__(self, left, top, width, height)
	
	#move rectangle to a new position
	def move(self, pos):
		self.topleft = pos

#a rectangle that can be clicked on
class clickRect(rect):
	def __init__(self, window, left, top, width, height, layer, clicked, allow_dragging = True, allow_hovering = True):
		rect.__init__(self, left, top, width, height)
		window.addclickarea(layer, self)
		
		self.clickedevent = clicked
		self.allow_dragging = allow_dragging
		self.allow_hovering = allow_hovering
		self.dragged = False
		self.hovering = False
		
		self.startdragpos = [0,0]
	
	def clickrectevent(self, event, position):
		if self.allow_dragging:
			if event.type == MOUSEBUTTONDOWN:
				self.startdragpos = position
				self.dragged = True
			elif self.dragged:
				if event.type == MOUSEBUTTONSTOPDRAG:
					self.dragged = False
		if self.allow_hovering:
			if event.type == MOUSEBUTTONHOVER:
				self.hovering = True
			if event.type == MOUSEBUTTONSTOPHOVER:
				self.hovering = False
		self.clickedevent(event, position, self.startdragpos)
	
	def move(self, pos):
		rect.move(self, pos)
	
	def hover(self, position):
		pass

#a simple sprite
class sprite(pygame.sprite.Sprite):
	def __init__(self, window, imagefolder, imagename, size=None):
		pygame.sprite.Sprite.__init__(self)
		self.imagename = imagename
		self.imagefolder = imagefolder
		self.size = size
		self.visible = True
		self.refresh()

	def refresh(self):
		self.image, self.rect = resources.load_image(self.imagefolder, self.imagename)
		if self.size != None:
			self.image = pygame.transform.scale(self.image, (int(self.size[0]), int(self.size[1])))
			self.rect.width = int(self.size[0])
			self.rect.height = int(self.size[1])

	def draw(self, screen):
		if self.visible:
			if self.image != None:
				screen.blit(self.image, self.rect)

	def move(self, pos):
		self.rect.topleft = pos

#a sprite that can be clicked on
class clickSprite(sprite):
	def __init__(self, window, imagefolder, imagename, clickmethod, size=None, clicklayer=1, allow_dragging = True, allow_hovering = True):
		sprite.__init__(self, window, imagefolder, imagename, size)
		self.rect = clickRect(window, self.rect.left, self.rect.top, self.rect.width, self.rect.height, layer=clicklayer, clicked=clickmethod, allow_dragging=allow_dragging, allow_hovering=allow_hovering)

#control
class control():
	def __init__(self, window):
		self.tabbable = False
		self.editable = True
		self.window = window
		self.visible = True
	def select(self):
		pass
	def deselect(self):
		pass
	def event(self, event, position):
		pass

#a picturebox control
class picturebox(clickRect, control):
	def __init__(self, window, imagefolder, imagename, size=[50, 50], clickevent=None):
		control.__init__(self, window)

		self.window = window
		self.imagefolder = imagefolder
		self.imagename = imagename
		
		self.iconsize = size[0] / 2.0
		self.size = size
		
		self.clickevent = clickevent

#		self.gimpsprite = clickSprite(self.window, "gui", "gimp.png", self.gimpedit, size=[self.iconsize, self.iconsize], allow_dragging=False, allow_hovering=False, clicklayer=2)
#		self.refreshsprite = clickSprite(self.window, "gui", "refresh.png", self.refresh, size=[self.iconsize, self.iconsize], allow_dragging=False, allow_hovering=False, clicklayer=2)

		self.makesprite()
		
		if self.sprite:
			clickRect.__init__(self, window.area, 0, 0, self.sprite.rect.width, self.sprite.rect.height, 1, self.click)
		else:
			clickRect.__init__(self, window.area, 0, 0, size[0], size[1], 1, self.click)
	
	def click(self, event, position, dragpos=None):
		if is_click(event):
			if self.clickevent != None:
				self.clickevent()
		if self.editable:
			rightclickmenu(event, [["edit", self.gimpedit], ["refresh", self.refresh]])

	def makesprite(self):
		fullname = resources.fullname(self.imagefolder, self.imagename)
		if os.path.exists(fullname):
			self.sprite = sprite(self.window, self.imagefolder, self.imagename, size=self.size)
			self.sprite.move(self.topleft)
			self.width = self.sprite.rect.width
			self.height = self.sprite.rect.height
#			self.toggleicons()
		else:
			self.sprite = None
	
	def gimpedit(self):
		fullname = resources.fullname(self.imagefolder, self.imagename)
		if not os.path.exists(fullname):
			os.system("convert -define png:color-type=6 -size " + str(self.size[0]) + "x" + str(self.size[1]) + " xc:transparent " + str(fullname))
		subprocess.Popen(shlex.split("gimp \""+str(fullname)+"\""))
		
	def refresh(self):
		self.makesprite()
	
	def draw(self, screen):
		pygame.draw.rect(screen, pygame.color.Color("black"), self, 1)
		if self.sprite:
			self.sprite.draw(screen)
	
	def move(self, pos):
		rect.move(self, pos)
		if self.sprite:
			self.sprite.move(pos)

#a checkbox control
class checkbox(rect, control):
	def __init__(self, window, text, font=None, clickmethod=None):
		control.__init__(self, window)
		self.sprite = clickSprite(window.area, "gui", "check.png", self.click, allow_dragging=False, allow_hovering=False)

		self.clickmethod = clickmethod

		self.buffer = 5

		if font == None:
			font = pygame.font.Font(None, 14)
		self.text = font.render(text, 1, (0,0,0))
		self.textpos = rect(self.text.get_rect())

		rect.__init__(self, 0, 0, self.sprite.rect.width + self.textpos.width, self.sprite.rect.height)
		self.checked = False
	
	def click(self, event, position, dragposition):
		if is_click(event):
			if self.editable:
				self.checked = not self.checked
				if self.clickmethod != None:
					self.clickmethod()

	def draw(self, screen):
		if self.checked:
			self.sprite.draw(screen)
		pygame.draw.rect(screen, pygame.color.Color("black"), self.sprite.rect, 1)
		screen.blit(self.text, self.textpos)
	
	def move(self, pos):
		rect.move(self, pos)
		self.textpos.move(pos)
		self.textpos.left += self.sprite.rect.width + self.buffer
		self.sprite.move(pos)

#a label control
class label(clickRect, control):
	def __init__(self, window, text, method=None, font=None, fontsize=14):
		control.__init__(self, window)
		pos=[0,0]
		
		self.font = font
		self.text = text
		
		self.method = method
		
		if self.font == None:
			self.font = pygame.font.Font(None, fontsize)
		self.label = self.font.render(self.text, 1, (0,0,0))
		clickRect.__init__(self, self.window, self.label.get_rect().left, self.label.get_rect().top, self.label.get_rect().width, self.label.get_rect().height, 1, self.click)
		
		self.move(pos)
		
	def click(self, event, position, dragpos=None):
		if is_click(event):
			if self.method != None:
				self.method()
		
	def move(self, pos):
		clickRect.move(self, pos)
	
	def draw(self, screen):
		self.label = self.font.render(self.text, 1, (0,0,0))
		self.height = self.label.get_rect().height
		self.width = self.label.get_rect().width
		screen.blit(self.label, self)

#a button control
class button(clickRect, control):
	def __init__(self, window, text, clickmethod, clicklayer=1, allow_dragging=False, allow_hovering=False, font=None):
		control.__init__(self, window)
		
		self.outlinewidth = 2
		
		self.rectangles = []

		self.textbuffer = 3
		
		self.tabbable = True
		
		self.clickmethod = clickmethod
		
		self.outlinecolor = pygame.color.Color("black")
		
		if font == None:
			font = pygame.font.Font(None, 14)
		self.text = font.render(text, 1, (0,0,0))
		self.textpos = rect(self.text.get_rect())
		self.rectangles.append(self.textpos)
		
		self.height = self.textpos.height + self.textbuffer*2
		self.width = self.textpos.width + self.textbuffer*2
		
		clickRect.__init__(self, window.area, 0, 0, self.width, self.height, clicklayer, self.click, allow_dragging, allow_hovering)
		
		self.textpos.topleft = [0,0]
		
		self.topleft = [0,0]
	
	def click(self, event, position, drag_pos = None):
		if self.editable:
			if is_click(event):
				self.clickmethod()
	
	def move(self, pos):
		clickRect.move(self, pos)
		textpospos = [pos[0] + self.textbuffer, pos[1] + self.textbuffer]
		self.textpos.move(textpospos)
	
	def select(self):
		self.outlinecolor = pygame.color.Color("green")

	def unselect(self):
		self.outlinecolor = pygame.color.Color("black")
	
	def draw(self, screen):
		pygame.draw.rect(screen, pygame.color.Color("light grey"), self)
		pygame.draw.rect(screen, self.outlinecolor, self, self.outlinewidth)
		screen.blit(self.text, self.textpos)

class menuitem(clickRect, control):
	def __init__(self, window, text, clickmethod, width=None, clicklayer=1, allow_dragging=False, font=None):
		control.__init__(self, window)
		
		self.rectangles = []

		self.textbuffer = 3
		
		self.clickmethod = clickmethod
		if width == None:
			self.width = window.area.rect.width
		else:
			self.width = width
		
		self.selected = False
		
		if font == None:
			font = pygame.font.Font(None, 14)
		self.text = font.render(text, 1, (0,0,0))
		self.textpos = rect(self.text.get_rect())
		self.rectangles.append(self.textpos)
		
		self.height = self.textpos.height + self.textbuffer*2
		
		clickRect.__init__(self, window.area, 0, 0, self.width, self.height, clicklayer, self.event, allow_dragging)
		
		self.textpos.topleft = [0,0]
		
		self.topleft = [0,0]
	
	def event(self, event, position, drag_pos = None):
		if self.editable:
			if is_click(event):
				self.clickmethod()
		if event.type == MOUSEBUTTONHOVER:
			self.selected = True
		elif event.type == MOUSEBUTTONSTOPHOVER:
			self.selected = False
	
	def move(self, pos):
		clickRect.move(self, pos)
		textpospos = [pos[0] + self.textbuffer, pos[1] + self.textbuffer]
		self.textpos.move(textpospos)
	
	def draw(self, screen):
		if self.selected:
			pygame.draw.rect(screen, pygame.color.Color("light blue"), self)
		screen.blit(self.text, self.textpos)

#an entry box control
class entry(clickRect, control):
	def __init__(self, window, width, clicklayer=1, font=None, method=None, numbers=False):
		control.__init__(self, window)
		
		self.textpospos = [0,0]
		
		self.window = window
		
		self.outlinewidth = 2
		
		self.rectangles = []
		
		self.controlwidth = width

		self.textbuffer = 3
		self.controlwidth -= self.textbuffer * 2
		
		self.tabbable = True
		
		self.method = method
		self.changemethod = []
		
		self.numbers = numbers
		
		self.outlinecolor = pygame.color.Color("black")
		
		self.text = ""
		
		self.font = font
		if self.font == None:
			self.font = pygame.font.Font(None, 14)
		
		self.rendertext()

		clickmethod = self.click
		clickRect.__init__(self, window.area, 0, 0, self.width, self.height, clicklayer, clickmethod, None, None)
		
		self.rtextpos.topleft = [0,0]
		
		self.topleft = [0,0]
	
	def rendertext(self):
		try:
			self.rectangles.remove(self.rtextpos)
		except:
			pass
		self.rtext = self.font.render(str(self.text), 1, (0,0,0))
		self.rtextpos = rect(self.rtext.get_rect())
		self.rtextpos.width = self.controlwidth
		self.rtextpos.move(self.textpospos)
		self.rectangles.append(self.rtextpos)
		
		self.height = self.rtextpos.height + self.textbuffer*2
		self.width = self.rtextpos.width + self.textbuffer*2
	
	def move(self, pos):
		self.pos = pos
		clickRect.move(self, pos)
		textpospos = [pos[0] + self.textbuffer, pos[1] + self.textbuffer]
		self.textpospos = textpospos
		self.rtextpos.move(textpospos)
		
	def click(self, event, position, startdragpos=None):
		if is_click(event):
			self.window.tab(self.window.gettablist().index(self))
	
	def select(self):
		self.outlinecolor = pygame.color.Color("green")

	def unselect(self):
		self.outlinecolor = pygame.color.Color("black")
	
	def draw(self, screen):
		pygame.draw.rect(screen, pygame.color.Color("light grey"), self)
		pygame.draw.rect(screen, self.outlinecolor, self, self.outlinewidth)
		screen.blit(self.rtext, self.rtextpos)

	def event(self, event, position):
		if event.type == KEYDOWN:
			if self.editable:
				if event.key == K_BACKSPACE:
					if len(str(self.text)) >= 1:
						self.text = str(self.text)[:-1]
						if self.changemethod != []:
							for method in self.changemethod:
								method()
				elif event.key == K_RETURN:
					if self.method != None:
						self.method()
				else:
					key = event.unicode
					if self.numbers == False or str(key) in ["1","2","3","4","5","6","7","8","9","0"]:
						self.text = str(self.text)
						self.text += key
						if self.changemethod != []:
							for method in self.changemethod:
								method()
		self.rendertext()

class eventhandler():
	def __init__(self, window, offset=None):
		self.clickareas = []
		self.windoweventhandler = window
		self.offset = offset
	
	#add clickable area to window
	def addclickarea(self, layer, rect):
		if len(self.clickareas)-1 < layer:
			for i in range(len(self.clickareas), layer+1): #@UnusedVariable
				self.clickareas.append([])
		
		self.clickareas[layer].append(rect)
	
	#get mouse event
	def event(self, event, position):
		if self.offset != None:
			position = [position[0] - self.rect.left, position[1] - self.rect.top + self.scrolltop]
			
		if event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
			foundrect = False
			for layernum in range(len(self.clickareas)-1, -1, -1):
				layer = self.clickareas[layernum]
				for rectnum in range(len(layer)-1, -1, -1):
					rect = layer[rectnum]
					if rect.collidepoint(position):
						rect.clickrectevent(event, position)
						foundrect = True
					if foundrect:
						break
				if foundrect:
					break
		elif event.type == KEYDOWN and event.key == K_TAB:
			self.tab()
		else:
			if len(self.windoweventhandler.gettablist()) != 0:
				self.windoweventhandler.gettablist()[self.windoweventhandler.tabindex].event(event, position)
	
	#update hovering and dragging
	def update(self):
		position = pygame.mouse.get_pos()
		if self.offset != None:
			position = [position[0] - self.rect.left, position[1] - self.rect.top + self.scrolltop]

		for layer in self.clickareas:
			for rect in layer:
				if rect.dragged:
					if pygame.mouse.get_pressed()[0] == False and pygame.mouse.get_pressed()[2] == False:
						rect.clickrectevent(pygame.event.Event(MOUSEBUTTONSTOPDRAG), position)
					else:
						button = pygame.mouse.get_pressed().index(True)+1
						rect.clickrectevent(pygame.event.Event(MOUSEBUTTONDRAGGED, {"button":button}), position)
				if rect.allow_hovering:
					if not rect.hovering:
						if rect.collidepoint(position):
							rect.clickrectevent(pygame.event.Event(MOUSEBUTTONHOVER), position)
					else:
						if not rect.collidepoint(position):
							rect.clickrectevent(pygame.event.Event(MOUSEBUTTONSTOPHOVER), position)

#main area for window
class windowarea(pygame.Surface, eventhandler):
	def __init__(self, window, left, top, width, height):
		self.window = window
		
		self.resize([1,1])
		eventhandler.__init__(self, self.window, self)
		
		self.rect = clickRect(window, self.get_rect().left, self.get_rect().top, self.get_rect().width, self.get_rect().height, 1, self.event, False, False)
		self.rect.topleft = [left, top]
		self.rect.width = width
		self.rect.height = height
		
		if self.window.has_scrollbar == True:
			self.rect.width -= self.window.scrollbarwidth
		
		window.addrect(self.rect, stretch=[True, True], bottomright=None)
		
		self.scrollpercent = 0.0
		self.scrolltop = 0
		
		self.objects = []
		
	def resize(self, size):
		pygame.Surface.__init__(self, (int(size[0]), int(size[1])))
	
	def draw(self, screen):
		screenrect = rect(0, self.scrolltop, self.rect.width, self.rect.height)
		screen.blit(self, [self.rect.left,self.rect.top], area=screenrect)
		pygame.draw.rect(self, pygame.color.Color("white"), screenrect)
		for obj in self.objects:
			obj.draw(self)
			
	def addclickarea(self, layer, rect):
		eventhandler.addclickarea(self, layer, rect)
#		if len(self.clickareas)-1 < layer:
#			for i in range(len(self.clickareas), layer+1): #@UnusedVariable
#				self.clickareas.append([])
#		
#		self.clickareas[layer].append(rect)
	
	def event(self, event, position, dragstartpos=None):
		if event.type == MOUSEBUTTONDOWN and event.button in [4,5]:
			if self.window.has_scrollbar:
				if event.button == 4:
					scrolldist = 10
				else:
					scrolldist = -10
				
				if float(self.rect.height - self.window.scrollbar.height) == 0:
					newscrollpercent = 0.0
				else:
					newscrollpercent = (self.window.scrollbar.top - (self.rect.top + scrolldist)) / float(self.rect.height - self.window.scrollbar.height)		
				self.scrollpercent = newscrollpercent
							
				self.window.scroll(newscrollpercent)
		else:
			eventhandler.event(self, event, position)

#		elif event.type in [MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEBUTTONDRAGGED, MOUSEBUTTONSTOPDRAG, MOUSEBUTTONHOVER, MOUSEBUTTONSTOPHOVER]:
#			foundrect = False
#			for layernum in range(len(self.clickareas)-1, -1, -1):
#				layer = self.clickareas[layernum]
#				for rectnum in range(len(layer)-1, -1, -1):
#					rect = layer[rectnum]
#					if rect.collidepoint(position):
#						rect.click(event, position)
#						foundrect = True
#					if foundrect:
#						break
#				if foundrect:
#					break
	
	def update(self):
		eventhandler.update(self)

class grid():
	def __init__(self, packoffset=[0,0]):
		self.packlist = []
		self.packbuffer = 4
		self.packoffset = packoffset
	
	def repack(self):
		for y, layer in enumerate(self.packlist):
			for x, rect in enumerate(layer): #@UnusedVariable
				if y == 0:
					posy = self.packoffset[1]
				else:
					height = self.packlist[y-1][0].top
					#add height of last column
					columnheights = [obj.height for obj in self.packlist[y-1]]
					columnheight = max(columnheights)
					height += columnheight
					posy = height
					posy += self.packbuffer
				
				posx = self.packoffset[0]
				for obj in layer[:x]:
					posx += obj.width
					posx += self.packbuffer
				
				rect.move([posx, posy])
			
	#add control to window
	def pack(self, rect, direction="down"):
		if direction == "down":
			self.packlist.append([])
			self.packlist[len(self.packlist)-1].append(rect)
		elif direction == "right":
			self.packlist[len(self.packlist)-1].append(rect)

		self.repack()
	
	def unpack(self, rect=None):
		if rect == None:
			self.packlist = []
		else:
			for index, column in enumerate(self.packlist): #@UnusedVariable
				try:
					self.packlist[index].remove(rect)
					break
				except:
					pass
			self.repack()
	
	def getheight(self):
		#get distance to last column
		if len(self.packlist) == 0:
			height = 0
		else:
			height = self.packlist[-1][0].top - self.packoffset[1]
			#add height of last column
			columnheights = [obj.height for obj in self.packlist[-1]]
			columnheight = max(columnheights)
			height += columnheight
		
		return height
	
	def getwidth(self):
		#get distance to last column
		if len(self.packlist) == 0:
			width = 0
		else:
			columnwidths = []
			for layer in self.packlist:
				columnwidth = 0
				for obj in layer:
					try:
						columnwidth += obj.width
						columnwidth += self.packbuffer
					except:
						pass
				columnwidths.append(columnwidth)
			width = max(columnwidths)
		return width

class controlgroup(rect, grid, control):
	def __init__(self, window):
		rect.__init__(self, 0, 0, 1, 1)
		control.__init__(self, window)
		self.window = window
		grid.__init__(self)
		
	def pack(self, rect, direction = "down"):
		grid.pack(self, rect, direction)
		self.recalcsize()
		
	def recalcsize(self):
		if self.visible:
			self.packoffset = self.topleft
			self.width = self.getwidth()
			self.height = self.getheight()
		else:
			self.width = 0
			self.height = 0
		
	def repack(self):
		self.recalcsize()
		grid.repack(self)
		self.window.repack()
		
	def move(self, pos):
		for layer in self.packlist:
			for obj in layer:
				posoffset = [obj.left - self.left, obj.top - self.top]
				newpos = [pos[0] + posoffset[0], pos[1] + posoffset[1]]
				obj.move(newpos)
		rect.move(self, pos)
		
	def draw(self, screen):
		if self.visible:
			for layer in self.packlist:
				for obj in layer:
					obj.draw(screen)
	
class drawer(controlgroup):
	def __init__(self, window, title):
		controlgroup.__init__(self, window)
		
		self.titlearea = controlgroup(window)
		
		self.togglebutton = picturebox(window, "gui", "arrowdown.png", size=[20,20], clickevent=self.togglevisible)
		self.titlearea.pack(self.togglebutton)
		
		self.titlelabel = label(window, title, fontsize=20)
		self.titlearea.pack(self.titlelabel, "right")
		
		self.items = controlgroup(window)
		
		self.itemsvisible = False
		self.itemspacked = False
		
		self.refresh()
		
	def togglevisible(self):
		self.itemsvisible = not self.itemsvisible
		self.refresh()
		
	def refresh(self):
		self.unpack()
		
		controlgroup.pack(self, self.titlearea)
		
		if self.itemsvisible:
			self.togglebutton.imagename = "arrowdown.png"
		else:
			self.togglebutton.imagename = "arrowside.png"
		self.togglebutton.refresh()

		if self.itemsvisible:
			if self.itemspacked == False:
				self.packitems()
				self.itemspacked = True
			controlgroup.pack(self, self.items)
		
		self.recalcsize()
		self.repack()
		
	def packitems(self):
		pass
		
	def pack(self, rect, direction="down"):
		self.items.pack(rect, direction)
		self.refresh()

class listbox(controlgroup):
	def __init__(self, window, title, items, method=None):
		controlgroup.__init__(self, window)
		
		self.items = items
		self.title = title
		self.method = method
		
		self.refreshitems()
		
	def refreshitems(self):
		self.unpack()
		
		addbutton = picturebox(self.window, "gui", "plus.png", clickevent=self.startadditem, size=[10,10])
		self.pack(addbutton)
		
		titlelabel = label(self.window, self.title)
		self.pack(titlelabel, "right")
		
		for item in list(self.items):
			removebutton = picturebox(self.window, "gui", "minus.png", clickevent=functools.partial(self.removeitem, item), size=[10,10])
			self.pack(removebutton)
			
			itemlabel = label(self.window, item, functools.partial(self.click, item))
			self.pack(itemlabel, "right")
			
		self.recalcsize()
		self.repack()
	
	def repack(self):
		self.packoffset = [self.left, self.top]
		grid.repack(self)
	
	def click(self, item):
		if self.method != None:
			self.method(item)
		
	def removeitem(self, item):
		self.items.remove(item)
		self.refreshitems()
		
	def startadditem(self):
		inputbox("New Item", "Enter new item", self.finishadditem)
	
	def finishadditem(self, newitem):
		self.items.append(newitem)
		self.refreshitems()

class Window(pygame.Rect, grid, eventhandler):
	#init
	def __init__(self, title, width=None, height=None, left=None, top=None, scrollbar=False, has_titlebar=True, minwidth=100, minheight=50):		
		self.auto_width = False
		self.auto_height = False
		if width == None:
			self.auto_width = True
			width = minwidth
		if height == None:
			self.auto_height = True
			height = minheight

		centerleft, centertop = placewindow(width, height)
		if top == None:
			top=centertop
		if left == None:
			left = centerleft
		
		pygame.Rect.__init__(self, left, top, width, height)
		eventhandler.__init__(self, self)
		
		objlists.windows.insert(0, self)
		focus(self)
		
		self.rectangles = []
		self.objects = []
		
		self.title = title
		
		self.minsize = [minwidth, minheight]
		
		if has_titlebar:
			self.titlebarheight = 15
		else:
			self.titlebarheight = 0
				
		self.addrect(self, stretch=[True, True])
		
		self.areabuffer = 5
		
		#keep track of where to put new controls
		grid.__init__(self)
		
		#scrollbar stuff
		self.has_scrollbar = scrollbar
		self.scrollbarwidth = 10
		
		#main area for controls
		self.area = windowarea(self, self.left + self.areabuffer, self.top + self.titlebarheight + self.areabuffer, self.width-self.areabuffer*2, self.height-self.titlebarheight-self.areabuffer*2)

		#scrollbar
		if self.has_scrollbar:
			self.scrollbardifference = 0
			self.scrollbar = clickRect(self, self.right-self.areabuffer-self.scrollbarwidth, self.area.rect.top, self.scrollbarwidth, self.area.rect.bottom, 1, self.clickscrollbar, allow_hovering=False)
			self.addrect(self.scrollbar, stretch=[False, False], addsize=[True, False])		
			self.resizescrollbar()
		
		#window background
		self.back = pygame.Surface([width, height])
		self.back = self.back.convert()
		self.back.fill((250,250,250))
		
		#window outline
		self.lines = pygame.Surface([width, height])
		self.lines = self.lines.convert()
		self.lines.fill((100,100,100))
		
		#titlebar
		self.has_titlebar = has_titlebar
		
		if self.has_titlebar:
			self.titlebar = clickRect(self, left, top, width, self.titlebarheight, 1, self.titlebarclicked, True)
			self.addrect(self.titlebar, stretch=[True, False])
			
			textbuffer = 2
			font = pygame.font.Font(None, 14)
			self.text = font.render(self.title, 1, pygame.color.Color("black"))
			self.textpos = rect(self.text.get_rect())
			self.textpos.top = self.top + textbuffer
			self.textpos.left = self.left + textbuffer
			self.addrect(self.textpos)
			
			#x button
			buttonbuffer = 2
			self.xbutton = clickSprite(self, "gui", "x.png", self.close_button, clicklayer=3)
			self.xbutton.rect.topleft = [self.right-buttonbuffer-self.xbutton.rect.width,self.top+buttonbuffer]
			self.addrect(self.xbutton.rect, addsize=[True, False])
			self.objects.append(self.xbutton)
		
		#resize areas around sides
		self.showresizeareas = False
		
		self.resizebuffer = 2

		self.resizeleft = clickRect(self, left-self.resizebuffer, top, self.resizebuffer*2, height, 2, functools.partial(self.resizeclicked, side="left"), True)
		self.addrect(self.resizeleft, stretch=[False, True])

		self.resizetop = clickRect(self, left, top-self.resizebuffer, width, self.resizebuffer*2, 2, functools.partial(self.resizeclicked, side="top"), True)
		self.addrect(self.resizetop, stretch=[True, False])
		
		self.resizeright = clickRect(self, self.right-self.resizebuffer, top, self.resizebuffer*2, height, 2, functools.partial(self.resizeclicked, side="right"), True)
		self.addrect(self.resizeright, addsize=[True, False], stretch=[False, True])

		self.resizebottom = clickRect(self, left, self.bottom-self.resizebuffer, width, self.resizebuffer*2, 2, functools.partial(self.resizeclicked, side="bottom"), True)
		self.addrect(self.resizebottom, addsize=[False, True], stretch=[True, False])
		
		#resize areas at corners
		self.cornerresizebuffer = 3
		
		self.resizetopleft = clickRect(self, left-self.cornerresizebuffer, top-self.cornerresizebuffer, self.cornerresizebuffer*2, self.cornerresizebuffer*2, 3, functools.partial(self.resizecornerclicked, side="topleft"), True)
		self.addrect(self.resizetopleft)

		self.resizetopright = clickRect(self, self.right-self.cornerresizebuffer, top-self.cornerresizebuffer, self.cornerresizebuffer*2, self.cornerresizebuffer*2, 3, functools.partial(self.resizecornerclicked, side="topright"), True)
		self.addrect(self.resizetopright, addsize=[True, False])

		self.resizebottomleft = clickRect(self, left-self.cornerresizebuffer, self.bottom-self.cornerresizebuffer, self.cornerresizebuffer*2, self.cornerresizebuffer*2, 3, functools.partial(self.resizecornerclicked, side="bottomleft"), True)
		self.addrect(self.resizebottomleft, addsize=[False, True])

		self.resizebottomright = clickRect(self, self.right-self.cornerresizebuffer, self.bottom-self.cornerresizebuffer, self.cornerresizebuffer*2, self.cornerresizebuffer*2, 3, functools.partial(self.resizecornerclicked, side="bottomright"), True)
		self.addrect(self.resizebottomright, addsize=[True, True])
		
		#list of all resize areas
		self.resizebars = [self.resizeleft, self.resizetop, self.resizeright, self.resizebottom, self.resizetopleft, self.resizetopright, self.resizebottomleft, self.resizebottomright]
		self.resizebarsindexes = {"left":0, "top":1, "right":2, "bottom":3, "topleft":4, "topright":5, "bottomleft":6, "bottomright":7}
		self.hovering = [False]*8
		
		#used in resize()
		self.originalpos = [0,0]
		self.originalsize = [0,0]
		
		self.tabindex = -1
		
		#rect that contains everything that can be clicked on in a window
		self.boundarybuffer = self.cornerresizebuffer
		self.boundaries = rect(self.left - self.boundarybuffer, self.top - self.boundarybuffer, self.width + 2*self.boundarybuffer, self.height + 2*self.boundarybuffer)
		self.addrect(self.boundaries, stretch=[True, True])
			
	def event(self, event, position, dragpos=None):
		eventhandler.event(self, event, position)
	
	def addclickarea(self, layer, rect):
		eventhandler.addclickarea(self, layer, rect)
	
	def update(self):
		eventhandler.update(self)
		self.area.update()
	
	#add control to window
	def pack(self, rect, direction="down"):
		self.area.objects.append(rect)
		
		grid.pack(self, rect, direction)

		if self.auto_height:
			newheight = self.getareaheight()
			newheight += self.height - self.area.rect.height
			newheight = max(newheight, self.minsize[1])
			self.originalpos[1] = self.top
			self.originalsize[1] = self.height
			self.resize(newheight-self.height, self.originalpos, self.originalsize, "bottom")
		if self.auto_width:
			newwidth = self.getareawidth()
			newwidth += self.width - self.area.rect.width
			newwidth = max(newwidth, self.minsize[0])
			self.originalpos[0] = self.left
			self.originalsize[0] = self.width
			self.resize(newwidth-self.width, self.originalpos, self.originalsize, "right")
		
		self.area.resize([self.getareawidth(), self.getareaheight()])

		if self.has_scrollbar:
			self.resizescrollbar()
	
	def unpack(self, rect=None):
		grid.unpack(self, rect)
		
		if rect == None:
			self.area.objects = []
		else:
			self.repack()
		
		if self.has_scrollbar:
			self.resizescrollbar()
			
	def getareaheight(self):
		return grid.getheight(self)
	
	def getareawidth(self):
		return grid.getwidth(self)
	
	#window has changed, update scrollbar
	def resizescrollbar(self):
		controlsheight = self.getareaheight()
		areaheight = self.area.rect.height
		if controlsheight < areaheight:
			scrollsizepercent = 1.0
		else:
			scrollsizepercent = float(areaheight) / float(controlsheight)
		self.scrollbar.height = scrollsizepercent * float(areaheight)
		self.scrollbar.top = (self.scrollbar.height - areaheight) * self.area.scrollpercent + self.area.rect.top
		self.calculatescrolltop()
	
	def clickscrollbar(self, event, position, drag_position):
		if is_click(event):
			self.scrollbardifference = (drag_position[1]-self.scrollbar.top)
		elif event.type == MOUSEBUTTONDRAGGED:
			#find new scroll bar top
			newscrollbartop = position[1] - self.scrollbardifference
			#find scroll bar percent
			if (self.scrollbar.height - self.area.rect.height) == 0:
				newscrollpercent = 1.0
			else:
				newscrollpercent = (newscrollbartop - self.area.rect.top) / float(self.area.rect.height - self.scrollbar.height)
			self.scroll(newscrollpercent)
	
	def scroll(self, newscrollpercent):
		#recalculate with mins and maxes
		if newscrollpercent > 1.0:
			newscrollpercent = 1.0
		elif newscrollpercent < 0.0:
			newscrollpercent = 0.0
		self.area.scrollpercent = newscrollpercent
		self.calculatescrolltop()
		
	def calculatescrolltop(self):
		self.area.scrolltop = self.area.scrollpercent * (self.getareaheight() - self.area.rect.height)
		if self.area.scrolltop == 0:
			self.area.scrollpercent = 0.0
		self.scrollbar.top = float(self.area.rect.height - self.scrollbar.height) * self.area.scrollpercent + self.area.rect.top	
		self.scrollbar.starttopleft = self.calcstarttopleft(self.scrollbar)
	
	#get lists of controls that can be selected
	def gettablist(self):
		tablist = []
		for row in self.packlist:
			for item in row:
				if item.tabbable:
					tablist.append(item)
		return tablist
	
	#update tab index
	def tab(self, newtab = None):
		tablist = self.gettablist()
		
		if len(tablist) != 0:
			tablist[self.tabindex].unselect()
		if newtab == None:
			newtab = self.tabindex + 1
		self.tabindex = newtab
		if self.tabindex > len(tablist)-1:
			self.tabindex = 0
		if len(tablist) != 0:
			tablist[self.tabindex].select()
	
	#add rectangle to list of rectangles, set properties
	def addrect(self, rect, addsize=[False, False], topleft=None, stretch=[False, False], bottomright=[0,0]):
		rect.starttopleftaddsize = addsize
		if topleft == None:
			topleft = self.calcstarttopleft(rect)
		if bottomright == None:
			bottomright = self.calcbottomright(rect)
		rect.startbottomright = bottomright
		rect.starttopleft = topleft
		rect.stretch = stretch
		self.rectangles.append(rect)
	
	#close window
	def close_button(self, event, position, dragpos):
		if event.type == MOUSEBUTTONUP:
			self.close()
	
	def close(self):
		objlists.windows.remove(self)
	
	#calculate difference between topleft of window and topleft of widget
	def calcstarttopleft(self, rect):
		topleft = [rect.left - self.left, rect.top - self.top]
		if rect.starttopleftaddsize[0] == True:
			topleft[0] -= self.width
		if rect.starttopleftaddsize[1] == True:
			topleft[1] -= self.height
		return topleft
	
	#calculate difference between bottomright of window and bottomright of widget
	def calcbottomright(self, rect):
		bottomright = [rect.right - self.right, rect.bottom - self.bottom]
		return bottomright
	
	#called whenever titlebar is clicked
	def titlebarclicked(self, event, position, dragpos):
		if is_click(event):
			self.originalpos = [self.left, self.top]
		if (event.type == MOUSEBUTTONDRAGGED and event.button == 1) or is_click(event):
			movevector = [position[0]-dragpos[0], position[1]-dragpos[1]]
			newpos = [self.originalpos[0] + movevector[0], self.originalpos[1] + movevector[1]]
			self.move(newpos)
	
	#corner is clicked for resizing
	def resizecornerclicked(self, event, position, dragpos, side=None):
		if event.type == MOUSEBUTTONDRAGGED or is_click(event):
			resizeclickedfunction = functools.partial(self.resizeclicked, event, position, dragpos)
			
			if side == "topleft":
				resizeclickedfunction(side="top")
				resizeclickedfunction(side="left")
			elif side == "topright":
				resizeclickedfunction(side="top")
				resizeclickedfunction(side="right")
			elif side == "bottomleft":
				resizeclickedfunction(side="bottom")
				resizeclickedfunction(side="left")
			elif side == "bottomright":
				resizeclickedfunction(side="bottom")
				resizeclickedfunction(side="right")
		if event.type == MOUSEBUTTONHOVER:
			self.hovering[self.resizebarsindexes[side]] = True
		if event.type == MOUSEBUTTONSTOPHOVER:
			self.hovering[self.resizebarsindexes[side]] = False

	#side is clicked for resizing
	def resizeclicked(self, event, position, dragpos, side=None):
		if is_click(event):
			if side == "left" or side == "right":
				self.originalpos[0] = self.left
				self.originalsize[0] = self.width
			elif side == "top" or side == "bottom":
				self.originalpos[1] = self.top
				self.originalsize[1] = self.height
		if event.type == MOUSEBUTTONDRAGGED or is_click(event):
			if side == "left" or side == "right":
				pos = position[0]
				dpos = dragpos[0]
			elif side == "top" or side == "bottom":
				pos = position[1]
				dpos = dragpos[1]
			movevector = pos-dpos
			self.resize(movevector, self.originalpos, self.originalsize, side)
		if event.type == MOUSEBUTTONHOVER:
			self.hovering[self.resizebarsindexes[side]] = True
		if event.type == MOUSEBUTTONSTOPHOVER:
			self.hovering[self.resizebarsindexes[side]] = False
	
	#resize window
	def resize(self, vector, originalpos, originalsize, side):
		for rectangle in self.rectangles:
			addtopleft = self.calcaddtopleft(rectangle)
			if side == "left":
				if originalsize[0] - vector > self.minsize[0]:
					if rectangle.stretch[0] == True:
						rectangle.width = originalsize[0] - vector + rectangle.startbottomright[0] - rectangle.starttopleft[0]
					rectangle.left = originalpos[0] + rectangle.starttopleft[0] + addtopleft[0] + vector
			elif side == "top":
				if originalsize[1] - vector > self.minsize[1]:
					if rectangle.stretch[1] == True:
						rectangle.height = originalsize[1] - vector + rectangle.startbottomright[1] - rectangle.starttopleft[1]
					rectangle.top = originalpos[1] + rectangle.starttopleft[1] + addtopleft[1] + vector
			elif side == "right":
				if originalsize[0] + vector > self.minsize[0]:
					if rectangle.stretch[0] == True:
						rectangle.width = originalsize[0] + vector + rectangle.startbottomright[0] - rectangle.starttopleft[0]
					rectangle.left = originalpos[0] + rectangle.starttopleft[0] + addtopleft[0]
			elif side == "bottom":
				if originalsize[1] + vector > self.minsize[1]:
					if rectangle.stretch[1] == True:
						rectangle.height = originalsize[1] + vector + rectangle.startbottomright[1] - rectangle.starttopleft[1]
					rectangle.top = originalpos[1] + rectangle.starttopleft[1] + addtopleft[1]
		if side == "top" or side == "bottom":
			if self.has_scrollbar:
				self.resizescrollbar()
	
	#add width or height to control topleft if needed
	def calcaddtopleft(self, rectangle):
		addtopleft = [0,0]
		if rectangle.starttopleftaddsize[0] == True:
			addtopleft[0] = self.width
		if rectangle.starttopleftaddsize[1] == True:
			addtopleft[1] = self.height
		return addtopleft
	
	#move window
	def move(self, pos):
		for rectangle in self.rectangles:
			addtopleft = self.calcaddtopleft(rectangle)
			rectangle.left = pos[0] + rectangle.starttopleft[0] + addtopleft[0]
			rectangle.top = pos[1] + rectangle.starttopleft[1] + addtopleft[1]
			
	#draw everything
	def draw(self, screen):
		pygame.draw.rect(screen, pygame.color.Color("white"), self)
#		pygame.draw.rect(screen, pygame.color.Color("grey"), self, 3)
		if self.has_scrollbar:
			pygame.draw.rect(screen, pygame.color.Color("black"), self.scrollbar, 1)
		if self.has_titlebar:
			pygame.draw.rect(screen, pygame.color.Color("light grey"), self.titlebar)
#			pygame.draw.rect(screen, pygame.color.Color("grey"), self.titlebar, 3)
			screen.blit(self.text, self.textpos)
		self.area.draw(screen)
		for obj in self.objects:
			obj.draw(screen)

		for i in range(len(self.resizebars)):
			if self.hovering[i] == True:
				resizebar = self.resizebars[i]
				pygame.draw.rect(screen, pygame.color.Color("green"), resizebar)

#place a window randomly
def placewindow(sizex, sizey):
	x=screensize[0]/2.0 - sizex/2.0
	y=screensize[1]/2.0 - sizey/2.0
	return x, y

#run on main
def pygameinit():
	#Initialize Everything
	pygame.init()
	objlists.screen = pygame.display.set_mode(screensize)
	pygame.display.set_caption('Project')
	
	#Create The Background
	objlists.background = pygame.Surface(objlists.screen.get_size())
	objlists.background = objlists.background.convert()
	objlists.background.fill((20,20,20))

	#Objects
	objlists.allsprites = pygame.sprite.RenderPlain(())
	objlists.clock = pygame.time.Clock()
	
	#Display The Background
	objlists.screen.blit(objlists.background, (0, 0))
	pygame.display.flip()
	
	pygame.key.set_repeat(500, 50)
	
def focus(window):
	if len(objlists.windows) != 0:
		if not window in objlists.unfocusable:
			try:
				objlists.windows.insert(0, objlists.windows.pop(objlists.windows.index(window)))
			except:
				pass
			
def send_to_back(window):
	if len(objlists.windows) != 0:
		objlists.windows.append(objlists.windows.pop(objlists.windows.index(window)))
		
class inputbox(Window):
	def __init__(self, title, question, method):
		Window.__init__(self, title, scrollbar=True)
		
		self.method = method
		
		self.questionlabel = label(self, question)
		self.pack(self.questionlabel)
		
		self.entrybox = entry(self, 100, method=self.ok)
		self.pack(self.entrybox)
		
		self.tab(0)
		
		self.cancelbutton = button(self, "Cancel", self.cancel)
		self.pack(self.cancelbutton)
		self.okbutton = button(self, "OK", self.ok)
		self.pack(self.okbutton, "right")
		
	def ok(self):
		self.method(self.entrybox.text)
		self.close()
	
	def cancel(self):
		self.close()

def rightclickmenu(event, items):
	if event.type == MOUSEBUTTONDOWN and event.button == 3:
		menu(items)

class menu(Window):
	def __init__(self, items):
		pos = pygame.mouse.get_pos()
		Window.__init__(self, "hi", left=pos[0], top=pos[1], width=100, scrollbar=False, has_titlebar=False, minheight = 20)
		
		self.packbuffer = 0
		
		objlists.clickoffwindows.append(self)
		
		self.menuitems = []
		
		for item in items:
			self.menuitems.append(menuitem(self, item[0], functools.partial(self.clickitem, item[1])))
			self.pack(self.menuitems[-1])
			
	def clickitem(self, method):
		method()
		self.close()
		
	def close(self):
		Window.close(self)
		objlists.clickoffwindows.remove(self)
		
	def clickoff(self):
		self.close()
		
def close():
	for window in objlists.windows:
		window.close()
	pygame.quit()

def mainloop(mainwindow):
	#Main Loop
	while True:
		objlists.clock.tick(60)
		
		#Handle Input Events
		for event in pygame.event.get():
			position = pygame.mouse.get_pos()
			if event.type == QUIT:
				close()
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				close()
			else:
				if event.type == MOUSEBUTTONDOWN and event.button in [1, 3]:
					for window in objlists.clickoffwindows:
						if not window.boundaries.collidepoint(position):
							window.clickoff()
				
				#find window, send event to window
				for windowindex in range(0, len(objlists.windows)):
					window = objlists.windows[windowindex]
					if window.boundaries.collidepoint(position):
						if event.type in [MOUSEBUTTONDOWN] and event.button == 1:
							#focus window
							focus(window)
						#event
						window.event(event, position)
						break

		objlists.allsprites.update()
		for window in objlists.windows:
			window.update()
		
		#Draw Everything
		objlists.screen.blit(objlists.background, (0, 0))
		objlists.allsprites.draw(objlists.screen)
		for windowindex in range(len(objlists.windows)-1, -1, -1):
			window = objlists.windows[windowindex]
			window.draw(objlists.screen)
		if len(objlists.windows) == 0:
			mainwindow()
		pygame.display.flip()