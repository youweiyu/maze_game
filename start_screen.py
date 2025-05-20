import os
import pgzrun
import pgzero
from pgzero.builtins import Actor
screen : pgzero.screen.Screen

os.environ['SDL_VIDEO_CENTERED'] = '1'

WIDTH = 480
HEIGHT = 852

background = Actor('background')
background.x = WIDTH / 2
background.y = HEIGHT / 2

start = Actor('start_no')
start.x = WIDTH / 2
start.y = HEIGHT / 2 + 100

def draw():
    background.draw()
    start.draw()

def update():
    pass

def on_mouse_move(pos, rel, buttons):
    x = pos[0]
    y = pos[1]
    if(start.collidepoint(x, y)):
        start.image = 'start_yes'
    else:
        start.image = 'start_no'

pgzrun.go()