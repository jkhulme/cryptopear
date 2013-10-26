import pygame
import pygame.camera
from pygame.locals import *

pygame.init()
pygame.camera.init()

camlist = pygame.camera.list_cameras()
if camlist:
    cam = pygame.camera.Camera(camlist[0],(640,480))
cam.start()
image = cam.get_image()

pygame.display.init()
screen = pygame.display.set_mode((640, 480))
screen.blit(image,(0,0))
pygame.display.flip()