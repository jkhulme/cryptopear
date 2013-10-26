
from SimpleCV import Camera
import json
import voting



def getCamera():
	cam = Camera()
	img = cam.getImage()
	img.save("mZOMGGUYS.png")
	return voting.encode_image("mZOMGGUYS.png")
	

#img.save("my-image.png")

def getUser():
	name = raw_input("Please enter your real name: ")
	return name

def getPubKey():
	return 'abc'

def returnJson():
	data = [{ 'name':getUser(), 'photo':getCamera(), 'publicKey':getPubKey() }]
	data_string = json.dumps(data)
	return data_string

print returnJson()


