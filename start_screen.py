import os
import pgzrun
import pgzero
from pgzero.builtins import Actor
screen : pgzero.screen.Screen

os.environ['SDL_VIDEO_CENTERED'] = '1'

WIDTH = 1500
HEIGHT = 800

game_state = False

background = Actor('landscape1')
background.x = WIDTH / 2
background.y = HEIGHT / 2

start = Actor('start_no')
start.x = WIDTH / 2
start.y = HEIGHT / 2 + 100

def draw():
    background.draw()
    start.draw()

def on_mouse_move(pos, rel, buttons):
    if not game_state:
        x,y = pos
        if start.collidepoint(x, y):
            start.image = 'start_yes'
        else:
            start.image = 'start_no'

def on_mouse_down(pos, button):
    global game_state
    if not game_state:
        x,y = pos
        if start.collidepoint(x, y):
            game_state = True
            
def run():
    pgzrun.go()

if __name__ == '__main__':
    run()