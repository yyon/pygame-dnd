import os, pygame
from pygame.locals import * #@UnusedWildImport

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

resfolder = "res"

def load_image(folder, name, colorkey=None, alpha=True):
	fullpath = fullname(folder, name)
	image = pygame.image.load(fullpath)
	if alpha:
		image = image.convert_alpha()
	else:
		image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image, image.get_rect()

def fullname(folder, name):
	return os.path.join(resfolder, folder, name)