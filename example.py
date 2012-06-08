from gui import * #@UnusedWildImport

#test window
class testwindow(Window):
	def __init__(self):
		Window.__init__(self, "Test Window", scrollbar=True)
		
		self.testlabel = label(self, "Hello World:")
		self.pack(self.testlabel)
		
		self.testbutton = button(self, "Hello World 3!", self.testbuttonclick)
		self.pack(self.testbutton, "right")
		
		self.nexttest = button(self, "Hello world 4!", self.testbuttonclick)
		self.pack(self.nexttest)
		
		self.entrylabel = label(self, "enter:")
		self.pack(self.entrylabel)
		
		self.nexttest = entry(self, 100)
		self.pack(self.nexttest, "right")
		
		self.check = checkbox(self, "hello world")
		self.pack(self.check)
		
		draw = drawer(self, "Test Title")

		draw.pack(label(self, "hi"))
		draw.pack(label(self, "hi"))
		draw.pack(label(self, "hi"))
		self.pict = picturebox(self, "test", "euohtasn.png", size=[50,50], clickevent=self.testbuttonclick)
		draw.pack(self.pict)
		
		self.pack(draw)
		
		self.pack(label(self, "hi"))
		self.pack(label(self, "hi"))
		self.pack(label(self, "hi"))
		self.pack(label(self, "hi"))
		self.pack(label(self, "hi"))
		self.pack(label(self, "hi"))
		self.pack(label(self, "hi"))
		
	def testbuttonclick(self):
		print "Hello world!"
