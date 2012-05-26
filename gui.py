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
import numpy

import os, pygame
from pygame.locals import *

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

MOUSEBUTTONDRAGGED = "drag"
MOUSEBUTTONSTOPDRAG = "stopdrag"
MOUSEBUTTONHOVER = "hover"
MOUSEBUTTONSTOPHOVER = "stophover"

__author__ = "Ian Campbell"
__copyright__ = "GPL v3"
__version__ = "0.0.1"

#a simple rectangle with a move function that integrates with a window
class rect(pygame.Rect):
	def __init__(self, window, left, top=None, width=None, height=None):
		if top == None:
			pygame.Rect.__init__(self, left)
		else:
			pygame.Rect.__init__(self, left, top, width, height)
		self.window = window
	
	def move(self, pos):
		self.topleft = pos
		self.starttopleft = self.window.calcstarttopleft(self)

#a rectangle that can be clicked on
class clickRect(rect):
	def __init__(self, window, left, top, width, height, layer, clicked, allow_dragging = True, allow_hovering = True):
		rect.__init__(self, window, left, top, width, height)
		addclickarea(layer, self)

		self.clicked = clicked
		self.allow_dragging = allow_dragging
		self.allow_hovering = allow_hovering
		self.dragged = False
		self.hovering = False
		
		self.startdragpos = [0,0]
	
	def click(self, event, position):
		if self.allow_dragging:
			if event == MOUSEBUTTONDOWN:
				self.startdragpos = position
				self.dragged = True
			elif self.dragged:
				if event == MOUSEBUTTONSTOPDRAG:
					self.dragged = False
		if self.allow_hovering:
			if event == MOUSEBUTTONHOVER:
				self.hovering = True
			if event == MOUSEBUTTONSTOPHOVER:
				self.hovering = False
		self.clicked(event, position, self.startdragpos)
	
	def hover(self, position):
		pass

#a sprite that can be clicked on
class clickSprite(pygame.sprite.Sprite):
	def __init__(self, window, imagefolder, imagename, clickmethod, clicklayer=1, allow_dragging = True, allow_hovering = True):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = resources.load_image(imagefolder, imagename)
		self.rect = clickRect(window, self.rect.left, self.rect.top, self.rect.width, self.rect.height, layer=clicklayer, clicked=clickmethod, allow_dragging=allow_dragging, allow_hovering=allow_hovering)
	def draw(self, screen):
		screen.blit(self.image, self.rect)

#add an area to the list of areas that can be clicked
def addclickarea(layer, rect):
	if len(objlists.clickareas) < layer:
		for i in range(len(objlists.clickareas), layer):
			objlists.clickareas.append([])
	
	objlists.clickareas[layer-1].append(rect)

#a button control
class button(clickRect):
	def __init__(self, window, text, clickmethod, clicklayer=1, allow_dragging=False, allow_hovering=False, font=None):
		self.outlinewidth = 2
				
		self.rectangles = []

		self.textbuffer = 3

		font = pygame.font.Font(None, 14)
		self.text = font.render(text, 1, (0,0,0))
		self.textpos = rect(window, self.text.get_rect())
		self.rectangles.append(self.textpos)
		
		self.height = self.textpos.height + self.textbuffer*2
		self.width = self.textpos.width + self.textbuffer*2

		clickRect.__init__(self, window, 0, 0, self.width, self.height, clicklayer, clickmethod, allow_dragging, allow_hovering)

		self.textpos.topleft = [0,0]
		window.addrect(self.textpos)
		
		self.topleft = [0,0]
		window.addrect(self)
		
		window.objects.append(self)
	
	def move(self, pos):
		pos = [pos[0] + self.window.area.left, pos[1] + self.window.area.top]
		clickRect.move(self, pos)
		textpospos = [pos[0] + self.textbuffer, pos[1] + self.textbuffer]
		self.textpos.move(textpospos)
	
	def draw(self, screen):
		pygame.draw.rect(screen, pygame.color.Color("light grey"), self)
		pygame.draw.rect(screen, pygame.color.Color("black"), self, self.outlinewidth)
		screen.blit(self.text, self.textpos)

class Window(pygame.Rect):
	#init
	def __init__(self, title, left, top, width, height, minwidth=100, minheight=100):
		pygame.Rect.__init__(self, left, top, width, height)
		
		objlists.windows.append(self)

		self.rectangles = []
		
		self.objects = []
		
		self.minsize = [minwidth, minheight]
		
		self.titlebarheight = 15
		
		self.addrect(self, stretch=[True, True])
		
		#main area for contros
		self.areabuffer = 5
		self.area = rect(self, self.left + self.areabuffer, self.top + self.titlebarheight + self.areabuffer, self.width-self.areabuffer*2, self.height-self.titlebarheight-self.areabuffer*2)
		self.addrect(self.area, stretch=[True, True], bottomright=None)
		
		#keep track of where to put new contros
		self.packlist = []
		self.packbuffer = 4
		
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
		self.text = font.render(title, 1, (0,0,0))
		self.textpos = rect(self, self.text.get_rect())
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
	
	#add control to window
	def pack(self, rect, dir="down"):
		if dir == "down":
			packnexty = 0
			for layer in self.packlist:
				layerheights = [obj.height for obj in layer]
				layerheight = max(layerheights)
				packnexty += layerheight
				packnexty += self.packbuffer
			self.packlist.append([])
			self.packlist[len(self.packlist)-1].append(rect)
			rect.move([0, packnexty])
		elif dir == "right":
			layer = self.packlist[len(self.packlist)-1]
			packnextx = 0
			packnexty = 0
			
			for layer in self.packlist[:-1]:
				layerheights = [rect.height for rect in layer]
				layerheight = max(layerheights)
				packnexty += layerheight
				packnexty += self.packbuffer

			for obj in layer:
				packnextx += obj.width
				packnextx += self.packbuffer
			
			self.packlist[len(self.packlist)-1].append(rect)
			rect.move([packnextx, packnexty])
	
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
		if event == MOUSEBUTTONUP:
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
		if event == MOUSEBUTTONDOWN:
			self.originalpos = [self.left, self.top]
		if event == MOUSEBUTTONDRAGGED or event == MOUSEBUTTONDOWN:
			movevector = [position[0]-dragpos[0], position[1]-dragpos[1]]
			newpos = [self.originalpos[0] + movevector[0], self.originalpos[1] + movevector[1]]
			self.move(newpos)
	
	#corner is clicked for resizing
	def resizecornerclicked(self, event, position, dragpos, side=None):
		if event == MOUSEBUTTONDRAGGED or event == MOUSEBUTTONDOWN:
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
		if event == MOUSEBUTTONHOVER:
			self.hovering[self.resizebarsindexes[side]] = True
		if event == MOUSEBUTTONSTOPHOVER:
			self.hovering[self.resizebarsindexes[side]] = False

	#side is clicked for resizing
	def resizeclicked(self, event, position, dragpos, side=None):
		if event == MOUSEBUTTONDOWN:
			if side == "left" or side == "right":
				self.originalpos[0] = self.left
				self.originalsize[0] = self.width
			elif side == "top" or side == "bottom":
				self.originalpos[1] = self.top
				self.originalsize[1] = self.height
		if event == MOUSEBUTTONDRAGGED or event == MOUSEBUTTONDOWN:
			if side == "left" or side == "right":
				pos = position[0]
				dpos = dragpos[0]
			elif side == "top" or side == "bottom":
				pos = position[1]
				dpos = dragpos[1]
			movevector = pos-dpos
			self.resize(movevector, self.originalpos, self.originalsize, side)
		if event == MOUSEBUTTONHOVER:
			self.hovering[self.resizebarsindexes[side]] = True
		if event == MOUSEBUTTONSTOPHOVER:
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
	
	#update window
	def update(self):
		pass
	
	#draw everything
	def draw(self, screen):
		pygame.draw.rect(screen, pygame.color.Color("white"), self)
#		pygame.draw.rect(screen, pygame.color.Color("grey"), self.area)
		pygame.draw.rect(screen, pygame.color.Color("grey"), self, 3)
		pygame.draw.rect(screen, pygame.color.Color("cyan"), self.titlebar)
		pygame.draw.rect(screen, pygame.color.Color("grey"), self.titlebar, 3)
		screen.blit(self.text, self.textpos)
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

		self.testbutton = button(self, "Hello World!", self.testbuttonclick)
		self.pack(self.testbutton)

		self.nexttest = button(self, "Hello world 2!", self.testbuttonclick)
		self.pack(self.nexttest)
	
	def testbuttonclick(self, event, position, dragpos):
		if event == MOUSEBUTTONUP:
			print "Hello world!"

#test window
class testwindow(Window):
	def __init__(self):
		Window.__init__(self, "Test Window", 400, 100, 200, 400)

		self.testbutton = button(self, "Hello World 3!", self.testbuttonclick)
		self.pack(self.testbutton)

		self.nexttest = button(self, "Hello world 4!", self.testbuttonclick)
		self.pack(self.nexttest)
	
	def testbuttonclick(self, event, position, dragpos):
		if event == MOUSEBUTTONUP:
			print "Hello world!"

#run on main
def main():
	#Initialize Everything
	pygame.init()
	screensize = [1200, 700]
	screen = pygame.display.set_mode(screensize)
	pygame.display.set_caption('Project')

	#Create The Backgound
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((0,0,0))

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
			elif event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
				foundrect = False
				for layernum in range(len(objlists.clickareas)-1, -1, -1):
					layer = objlists.clickareas[layernum]
					for rectnum in range(len(layer)-1, -1, -1):
						rect = layer[rectnum]
						if rect.collidepoint(position):
							rect.click(event.type, position)
							foundrect = True
						if foundrect:
							break
					if foundrect:
						break
			else:
				for layer in objlists.clickareas:
					for rect in layer:
						if rect.dragged:
							if pygame.mouse.get_pressed()[0] == False:
								rect.click(MOUSEBUTTONSTOPDRAG, position)
							else:
								rect.click(MOUSEBUTTONDRAGGED, position)
						if rect.allow_hovering:
							if not rect.hovering:
								if rect.collidepoint(position):
									rect.click(MOUSEBUTTONHOVER, position)
							else:
								if not rect.collidepoint(position):
									rect.click(MOUSEBUTTONSTOPHOVER, position)


		objlists.allsprites.update()
		for window in objlists.windows:
			window.update()

		#Draw Everything
		screen.blit(background, (0, 0))
		objlists.allsprites.draw(screen)
		for window in objlists.windows:
			window.draw(screen)
		if len(objlists.windows) == 0:
			mainwindow()
		pygame.display.flip()

if __name__ == "__main__":
	objlists = ObjectLists()
	main()
