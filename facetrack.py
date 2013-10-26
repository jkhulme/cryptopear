import time
from SimpleCV import *
import os 
display = Display()
cam = Camera()
#haarcascade = HaarCascade("face")
def isFace():
	while display.isNotDone():
		image = cam.getImage().flipHorizontal().scale(0.25)
		faces = image.findHaarFeatures( os.getcwd() + "/haarcascade_frontalface_alt.xml")
		
		if faces:
		 	face = faces[-1]
		 	face.draw(Color.RED, 1)
		 	image.show()
		else:
			return "Break connection"

isFace()