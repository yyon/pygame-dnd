#/usr/bin/env python

#Dungeons and Dragons v3.5 program
#Copyright (C) 2012  Ian Campbell

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import resources
import functools
import shlex, subprocess

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

		self.clicked = clicked
		self.allow_dragging = allow_dragging
		self.allow_hovering = allow_hovering
		self.dragged = False
		self.hovering = False
		
		self.startdragpos = [0,0]
	
	def click(self, event, position):
		if self.allow_dragging:
			if is_click(event):
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
		self.clicked(event, position, self.startdragpos)
	
	def move(self, pos):
		rect.move(self, pos)
	
	def hover(self, position):
		pass

#a simple sprite
class sprite(pygame.sprite.Sprite):
	def __init__(self, window, imagefolder, imagename, size=None):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = resources.load_image(imagefolder, imagename)
		if size != None:
			self.image = pygame.transform.scale(self.image, (int(size[0]), int(size[1])))
			self.rect.width = int(size[0])
			self.rect.height = int(size[1])
		self.visible = True
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
	def __init__(self):
		self.tabbable = False
	def select(self):
		pass
	def deselect(self):
		pass
	def event(self, event, position):
		pass

#a picturebox control
class picturebox(clickRect, control):
	def __init__(self, window, imagefolder, imagename, size=[50, 50]):
		control.__init__(self)

		self.window = window
		self.imagefolder = imagefolder
		self.imagename = imagename
		
		self.iconsize = size[0] / 2.0
		self.size = size

		self.gimpsprite = clickSprite(self.window, "gui", "gimp.png", self.gimpedit, size=[self.iconsize, self.iconsize], allow_dragging=False, allow_hovering=False, clicklayer=2)
		self.refreshsprite = clickSprite(self.window, "gui", "refresh.png", self.refresh, size=[self.iconsize, self.iconsize], allow_dragging=False, allow_hovering=False, clicklayer=2)

		self.makesprite()
		
		if self.sprite:
			clickRect.__init__(self, window, 0, 0, self.sprite.rect.width, self.sprite.rect.height, 1, self.showicons)
		else:
			clickRect.__init__(self, window, 0, 0, size[0], size[1], 1, self.showicons)
	
	def showicons(self, event, position, dragpos=None):
		if is_click(event):
			self.toggleicons()
	
	def toggleicons(self):
		self.gimpsprite.visible = not self.gimpsprite.visible
		self.refreshsprite.visible = not self.refreshsprite.visible
	
	def makesprite(self):
		fullname = resources.fullname(self.imagefolder, self.imagename)
		if os.path.exists(fullname):
			self.sprite = sprite(self.window, self.imagefolder, self.imagename)
			self.sprite.move(self.topleft)
			self.width = self.sprite.rect.width
			self.height = self.sprite.rect.height
			self.toggleicons()
		else:
			self.sprite = None
	
	def gimpedit(self, event, position, dragpos=None):
		if is_click(event):
			if self.gimpsprite.visible and self.refreshsprite.visible:
				fullname = resources.fullname(self.imagefolder, self.imagename)
				if not os.path.exists(fullname):
					os.system("convert -size " + str(self.size[0]) + "x" + str(self.size[1]) + " xc:transparent " + str(fullname))
				subprocess.Popen(shlex.split("gimp "+str(fullname)))
			else:
				self.toggleicons()
		
	def refresh(self, event, position, dragpos=None):
		if is_click(event):
			if self.gimpsprite.visible and self.refreshsprite.visible:
				self.makesprite()
			else:
				self.toggleicons()
		
	
	def draw(self, screen):
		pygame.draw.rect(screen, pygame.color.Color("black"), self, 1)
		if self.sprite:
			self.sprite.draw(screen)
		self.gimpsprite.draw(screen)
		self.refreshsprite.draw(screen)
	
	def move(self, pos):
		rect.move(self, pos)
		self.gimpsprite.move(pos)
		self.refreshsprite.move([pos[0]+self.iconsize, pos[1]])
		if self.sprite:
			self.sprite.move(pos)

#a checkbox control
class checkbox(rect, control):
	def __init__(self, window, text, font=None):
		control.__init__(self)
		self.sprite = clickSprite(window, "gui", "check.png", self.click, allow_dragging=False, allow_hovering=False)

		self.buffer = 5

		if font == None:
			font = pygame.font.Font(None, 14)
		self.text = font.render(text, 1, (0,0,0))
		self.textpos = rect(self.text.get_rect())

		rect.__init__(self, 0, 0, self.sprite.rect.width + self.textpos.width, self.sprite.rect.height)
		self.checked = False
		self.setvisible()
	
	def setvisible(self):
		if self.checked:
			self.sprite.visible = True
		else:
			self.sprite.visible = False
	
	def click(self, event, position, dragposition):
		if is_click(event):
			self.checked = not self.checked
			self.setvisible()

	def draw(self, screen):
		self.sprite.draw(screen)
		pygame.draw.rect(screen, pygame.color.Color("black"), self.sprite.rect, 1)
		screen.blit(self.text, self.textpos)
	
	def move(self, pos):
		rect.move(self, pos)
		self.textpos.move(pos)
		self.textpos.left += self.sprite.rect.width + self.buffer
		self.sprite.move(pos)
		

#a label control
class label(rect, control):
	def __init__(self, text, font=None):
		control.__init__(self)
		pos=[0,0]
		
		if font == None:
			font = pygame.font.Font(None, 14)
		self.text = font.render(text, 1, (0,0,0))
		rect.__init__(self, self.text.get_rect())
		
		self.move(pos)
		
	def move(self, pos):
		rect.move(self, pos)
	
	def draw(self, screen):
		screen.blit(self.text, self)

#a button control
class button(clickRect, control):
	def __init__(self, window, text, clickmethod, clicklayer=1, allow_dragging=False, allow_hovering=False, font=None):
		control.__init__(self)
		
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
		
		clickRect.__init__(self, window, 0, 0, self.width, self.height, clicklayer, clickmethod, allow_dragging, allow_hovering)
		
		self.textpos.topleft = [0,0]
		
		self.topleft = [0,0]
	
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

#a button control
class entry(clickRect, control):
	def __init__(self, window, width, clicklayer=1, font=None):
		control.__init__(self)
		
		self.textpospos = [0,0]
		
		self.window = window
		
		self.outlinewidth = 2
		
		self.rectangles = []
		
		self.controlwidth = width

		self.textbuffer = 3
		
		self.tabbable = True
		
		self.outlinecolor = pygame.color.Color("black")
		
		self.text = ""
		
		self.font = font
		if self.font == None:
			self.font = pygame.font.Font(None, 14)
		
		self.rendertext()

		clickmethod = self.click
		clickRect.__init__(self, window, 0, 0, self.width, self.height, clicklayer, clickmethod, None, None)
		
		self.rtextpos.topleft = [0,0]
		
		self.topleft = [0,0]
	
	def rendertext(self):
		try:
			self.rectangles.remove(self.rtextpos)
		except:
			pass
		self.rtext = self.font.render(self.text, 1, (0,0,0))
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
		
	def click(self, event, position):
		if is_click(event):
			self.window.window.tab(self.window.window.gettablist().index(self))
	
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
			if event.key == K_BACKSPACE:
				if len(self.text) >= 1:
					self.text = self.text[:-1]
			else:
				self.text += event.unicode
		self.rendertext()

#main area for window
class windowarea(pygame.Surface):
	def __init__(self, window, left, top, width, height):
		pygame.Surface.__init__(self, (screensize[0], screensize[1]))

		self.window = window
		
		self.rect = clickRect(window, self.get_rect().left, self.get_rect().top, self.get_rect().width, self.get_rect().height, 1, self.event)
		self.rect.topleft = [left, top]
		self.rect.width = width
		self.rect.height = height
		
		if self.window.has_scrollbar == True:
			self.rect.width -= self.window.scrollbarwidth
		
		window.addrect(self.rect, stretch=[True, True], bottomright=None)
		
		self.scrollpercent = 0.0
		self.scrolltop = 0
		
		self.objects = []
		self.clickareas = []
	
	def draw(self, screen):
		screenrect = rect(0, self.scrolltop, self.rect.width, self.rect.height)
		screen.blit(self, [self.rect.left,self.rect.top], area=screenrect)
		pygame.draw.rect(self, pygame.color.Color(240, 240, 240), screenrect)
		for obj in self.objects:
			obj.draw(self)
			
	#add clickable area to window
	def addclickarea(self, layer, rect):
		if len(self.clickareas)-1 < layer:
			for i in range(len(self.clickareas), layer+1): #@UnusedVariable
				self.clickareas.append([])
		
		self.clickareas[layer].append(rect)
	
	def event(self, event, position, dragstartpos=None):
		position = [position[0] - self.rect.left, position[1] - self.rect.top + self.scrolltop]
		
		if is_click(event) or (event.type == MOUSEBUTTONUP and event.button == 1):
			foundrect = False
			for layernum in range(len(self.clickareas)-1, -1, -1):
				layer = self.clickareas[layernum]
				for rectnum in range(len(layer)-1, -1, -1):
					rect = layer[rectnum]
					if rect.collidepoint(position):
						rect.click(event, position)
						foundrect = True
					if foundrect:
						break
				if foundrect:
					break
		elif event.type == MOUSEBUTTONDOWN and event.button in [4,5]:
			if event.button == 4:
				scrolldist = 10
				print "scrolling up"
			else:
				scrolldist = -10
				print "scrolling down"
			
			if float(self.rect.height - self.window.scrollbar.height) == 0:
				newscrollpercent = 0.0
			else:
				newscrollpercent = (self.window.scrollbar.top - (self.rect.top + scrolldist)) / float(self.rect.height - self.window.scrollbar.height)		
			self.scrollpercent = newscrollpercent
						
			self.window.scroll(newscrollpercent)
		else:
			self.window.gettablist()[self.window.tabindex].event(event, position)

class Window(pygame.Rect):
	#init
	def __init__(self, title, left, top, width, height, scrollbar=False, minwidth=100, minheight=100):
		pygame.Rect.__init__(self, left, top, width, height)
		
		objlists.windows.append(self)

		self.rectangles = []
		self.objects = []
		
		self.clickareas = []
		
		self.title = title
		
		self.minsize = [minwidth, minheight]
		
		self.titlebarheight = 15
				
		self.addrect(self, stretch=[True, True])
		
		self.areabuffer = 5
		
		#keep track of where to put new controls
		self.packlist = []
		self.packbuffer = 4
		
		#scrollbar stuff
		self.has_scrollbar = scrollbar
		self.scrollbarwidth = 10
		
		#main area for controls
		self.area = windowarea(self, self.left + self.areabuffer, self.top + self.titlebarheight + self.areabuffer, self.width-self.areabuffer*2, self.height-self.titlebarheight-self.areabuffer*2)

		#scrollbar
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
		self.titlebar = clickRect(self, left, top, width, self.titlebarheight, 1, self.titlebarclicked, True)
		self.addrect(self.titlebar, stretch=[True, False])
		
		textbuffer = 2
		font = pygame.font.Font(None, 14)
		self.text = font.render(self.title, 1, (0,0,0))
		self.textpos = rect(self.text.get_rect())
		self.textpos.top = self.top + textbuffer
		self.textpos.left = self.left + textbuffer
		self.addrect(self.textpos)
		
		#x button
		buttonbuffer = 2
		self.xbutton = clickSprite(self, "gui", "x.png", self.close, clicklayer=3)
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


			
	#add control to window
	def pack(self, rect, direction="down"):
		if direction == "down":
			packnexty = self.getareaheight()
			packnexty += self.packbuffer
			self.packlist.append([])
			self.packlist[len(self.packlist)-1].append(rect)
			rect.move([0, packnexty])
		elif direction == "right":
			layer = self.packlist[len(self.packlist)-1]
			packnextx = 0

			if len(self.packlist) == 0:
				packnexty = 0
			else:
				packnexty = self.packlist[-1][0].top

			for obj in layer:
				packnextx += obj.width
				packnextx += self.packbuffer
			
			self.packlist[len(self.packlist)-1].append(rect)
			rect.move([packnextx, packnexty])
		self.area.objects.append(rect)
		self.resizescrollbar()
		
	def getareaheight(self):
		#get distance to last column
		if len(self.packlist) == 0:
			height = 0
		else:
			height = self.packlist[-1][0].top
			#add height of last column
			columnheights = [obj.height for obj in self.packlist[-1]]
			columnheight = max(columnheights)
			height += columnheight
		
		return height
	
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
	def close(self, event, position, dragpos):
		if event.type == MOUSEBUTTONUP:
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
		if event.type == MOUSEBUTTONDRAGGED or is_click(event):
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
	
	#add clickable area to window
	def addclickarea(self, layer, rect):
		if len(self.clickareas)-1 < layer:
			for i in range(len(self.clickareas), layer+1): #@UnusedVariable
				self.clickareas.append([])
		
		self.clickareas[layer].append(rect)
	
	#get mouse event
	def event(self, event, position):
		if is_click(event) or (event.type == MOUSEBUTTONUP and event.button == 1):
			foundrect = False
			for layernum in range(len(self.clickareas)-1, -1, -1):
				layer = self.clickareas[layernum]
				for rectnum in range(len(layer)-1, -1, -1):
					rect = layer[rectnum]
					if rect.collidepoint(position):
						rect.click(event, position)
						foundrect = True
					if foundrect:
						break
				if foundrect:
					break
		elif event.type == KEYDOWN and event.key == K_TAB:
			self.tab()
		else:
			self.area.event(event, position, None)
	
	#update window
	def update(self):
		position = pygame.mouse.get_pos()
		for layer in self.clickareas:
			for rect in layer:
				if rect.dragged:
					if pygame.mouse.get_pressed()[0] == False:
						rect.click(pygame.event.Event(MOUSEBUTTONSTOPDRAG), position)
					else:
						rect.click(pygame.event.Event(MOUSEBUTTONDRAGGED), position)
				if rect.allow_hovering:
					if not rect.hovering:
						if rect.collidepoint(position):
							rect.click(pygame.event.Event(MOUSEBUTTONHOVER), position)
					else:
						if not rect.collidepoint(position):
							rect.click(pygame.event.Event(MOUSEBUTTONSTOPHOVER), position)
	
	#draw everything
	def draw(self, screen):
		pygame.draw.rect(screen, pygame.color.Color("white"), self)
		pygame.draw.rect(screen, pygame.color.Color("grey"), self, 3)
		pygame.draw.rect(screen, pygame.color.Color("black"), self.scrollbar, 1)
		pygame.draw.rect(screen, pygame.color.Color("cyan"), self.titlebar)
		pygame.draw.rect(screen, pygame.color.Color("grey"), self.titlebar, 3)
		screen.blit(self.text, self.textpos)
		self.area.draw(screen)
		for obj in self.objects:
			obj.draw(screen)

		for i in range(len(self.resizebars)):
			if self.hovering[i] == True:
				resizebar = self.resizebars[i]
				pygame.draw.rect(screen, pygame.color.Color("green"), resizebar)

#keeps track of ALL objects
class ObjectLists():
	def __init__(self):
		pass

#main window
class mainwindow(Window):
	def __init__(self):
		Window.__init__(self, "Main Window", 100, 100, 100, 500)

		self.testbutton = button(self.area, "Hello World!", self.testbuttonclick)
		self.pack(self.testbutton)
		
	def testbuttonclick(self, event, position, dragpos):
		if event.type == MOUSEBUTTONUP:
			print "Hello world!"

#test window
class testwindow(Window):
	def __init__(self):
		Window.__init__(self, "Test Window", 400, 100, 200, 400, scrollbar=True)
		
		self.testlabel = label("Hello World:")
		self.pack(self.testlabel)
		
		self.testbutton = button(self.area, "Hello World 3!", self.testbuttonclick)
		self.pack(self.testbutton, "right")

		self.nexttest = button(self.area, "Hello world 4!", self.testbuttonclick)
		self.pack(self.nexttest)
		
		self.entrylabel = label("enter:")
		self.pack(self.entrylabel)

		self.nexttest = entry(self.area, 100)
		self.pack(self.nexttest, "right")

		self.check = checkbox(self.area, "hello world")
		self.pack(self.check)
		
		self.pict = picturebox(self.area, "test", "euohtasn.png")
		self.pack(self.pict)
		
		self.pack(label("hi"))
		self.pack(label("hi"))
		self.pack(label("hi"))
		self.pack(label("hi"))
		self.pack(label("hi"))
	
	def testbuttonclick(self, event, position, dragpos):
		if event.type == MOUSEBUTTONUP:
			print "Hello world!"

#run on main
def main():
	#Initialize Everything
	pygame.init()
	screen = pygame.display.set_mode(screensize)
	pygame.display.set_caption('Project')

	#Create The Backgound
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((20,20,20))

	#Objects
	objlists.allsprites = pygame.sprite.RenderPlain(())
	objlists.windows = []
	objlists.clickareas = []
	clock = pygame.time.Clock()
	
	#Display The Background
	screen.blit(background, (0, 0))
	pygame.display.flip()
	
	mainwindow()
	testwindow()
	
	pygame.key.set_repeat(500, 50)
	
	#Main Loop
	while True:
		clock.tick(60)

		#Handle Input Events
		for event in pygame.event.get():
			position = pygame.mouse.get_pos()
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				return
			else:
				#find window, send event to window
				for windowindex in range(0, len(objlists.windows)):
					window = objlists.windows[windowindex]
					if window.boundaries.collidepoint(position):
						window.event(event, position)
						if event.type in [MOUSEBUTTONDOWN, MOUSEBUTTONUP] and event.button == 1:
							#focus window
							if len(objlists.windows) != 0:
								objlists.windows.insert(0, objlists.windows.pop(windowindex))
						break

		objlists.allsprites.update()
		for window in objlists.windows:
			window.update()

		#Draw Everything
		screen.blit(background, (0, 0))
		objlists.allsprites.draw(screen)
		for windowindex in range(len(objlists.windows)-1, -1, -1):
			window = objlists.windows[windowindex]
			window.draw(screen)
		if len(objlists.windows) == 0:
			mainwindow()
		pygame.display.flip()

if __name__ == "__main__":
	objlists = ObjectLists()
	main()
