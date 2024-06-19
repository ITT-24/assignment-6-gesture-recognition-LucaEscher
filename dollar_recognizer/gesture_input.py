import os
import pyglet

from pyglet import shapes
from recognizer import Recognizer, FIVE

TITLE = '1$ Recognizer'
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, TITLE)
recognizer = Recognizer(FIVE)
recognizer.initialize()

user_line = []
result_label = pyglet.text.Label(text='Gesture: ',
                                 font_name='Times New Roman',
                                 font_size=24,
                                 bold=True,
                                 x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//1.1,
                                 anchor_x='center', anchor_y='center',
                                 )

quit_label = pyglet.text.Label(text='press Q to quit',
                               font_name='Times New Roman',
                               font_size=14,
                               x=WINDOW_WIDTH//2, y=WINDOW_HEIGHT//1.2,
                               anchor_x='center', anchor_y='center',
                               )


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        os._exit(0)


@window.event
def on_mouse_press(x, y, button, modifiers):
    user_line.clear()


@window.event
def on_mouse_release(x, y, button, modifiers):
    if button and pyglet.window.mouse.LEFT:
        if len(user_line) > 0:
            result, score = recognizer.recognize(user_line)
            print("RESULT", result[0], score)
            result_label.text = f'Gesture: {result[0]}'


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if buttons & pyglet.window.mouse.LEFT:
        user_line.append([int(x), int(y)])


@window.event
def on_draw():
    window.clear()
    for x, y in user_line:
        point = shapes.Circle(x, y, 8, color=(255, 255, 0))
        point.draw()
    result_label.draw()
    quit_label.draw()


if __name__ == '__main__':
    pyglet.app.run()
