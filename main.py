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

from gui import * #@UnusedWildImport
import dungeonmap
import mapedit
import example
import network

#main window
class mainwindow(Window):
	def __init__(self):
		Window.__init__(self, "Main Window")
		
		self.testbutton = button(self, "Show Test Window", self.testbuttonclick)
		self.pack(self.testbutton)
		
		self.hostbutton = button(self, "Host", self.starthost)
		self.pack(self.hostbutton)
		
		self.clientbutton = button(self, "Connect to Host", self.connecttohost)
		self.pack(self.clientbutton)
		
		self.editmapbutton = button(self, "Maps", self.openmapclick)
		self.pack(self.editmapbutton)
		
		self.closebutton = button(self, "Quit", self.stop)
		self.pack(self.closebutton)
		
	def starthost(self):
		host = network.Host()
		print host.getsockname()
		self.startclient(host.getsockname()[0])
	
	def connecttohost(self):
		inputbox("Host IP", "Enter Host IP Address", self.startclient)
	
	def startclient(self, ip):
		network.Client(ip)
		network.loop()
		
	def stop(self):
		pygame.quit()
	
	def testbuttonclick(self):
		example.testwindow()
	
	def openmapclick(self):
		mapedit.openmap()
	
	def close(self):
		pass

def main():
	pygameinit()
	
	mainwindow()
	dungeonmapwindow = dungeonmap.mapwindow()
	objlists.dungeonmap = dungeonmapwindow.subsurface
	
	mainloop(mainwindow)

main()