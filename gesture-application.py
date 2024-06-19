# application for task 3

from harry_potter import HarryPotterGame
import os
import pyglet
import sys

from pyglet import shapes
from pyglet.gl import glClearColor
from prediction_model import PredictionModel


MODEL_LOADED = False
if len(sys.argv) > 1:
    MODEL_LOADED = str(sys.argv[1]) == 'True'


TITLE = 'Harry Potter'
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
LABEL_COLOR_BLACK = (1, 1, 1, 255)

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, TITLE)
glClearColor (255, 255, 255, 1.0)

print(MODEL_LOADED)
print(type(MODEL_LOADED))
recognizer = PredictionModel(MODEL_LOADED)
user_line = []




quit_label = pyglet.text.Label(text='press Q to quit',
                               font_name='Times New Roman',
                               font_size=14,
                               x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//1.2,
                               anchor_x='center', anchor_y='center',
                               )


quit_label.color = LABEL_COLOR_BLACK


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        os._exit(0)
    if symbol == pyglet.window.key.SPACE:
        if game.game_state == 0:
            game.game_state = 1
    if symbol == pyglet.window.key.R:
        game.restart()
    if symbol == pyglet.window.key.N:
        if game.game_state == 1.5:
            game.game_state = 2
        if game.game_state == 2.5:
            game.game_state = 3


@window.event
def on_mouse_press(x, y, button, modifiers):
    user_line.clear()


@window.event
def on_mouse_release(x, y, button, modifiers):
    if game.game_state == 1 or game.game_state == 2 or game.game_state == 3:
        if button and pyglet.window.mouse.LEFT:
            if len(user_line) > 0:
                prediction = recognizer.predict_gesture(user_line)
                game.fight(prediction)
                user_line.clear()


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if buttons & pyglet.window.mouse.LEFT:
        user_line.append([int(x), int(y)])


@window.event
def on_draw():
    global game
    
    window.clear()
    game.update(user_line)
    game.draw()
    
    if game.game_state == 1 or game.game_state == 2 or game.game_state == 3:
        quit_label.draw()
        
    

if __name__ == '__main__':
    global game
    game = HarryPotterGame(WINDOW_WIDTH, WINDOW_HEIGHT)
    pyglet.app.run()
