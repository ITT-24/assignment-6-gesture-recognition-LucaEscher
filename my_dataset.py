import os
import pyglet
import sys
import xml.etree.ElementTree as ET

from pyglet import shapes

SAVE_PATH = 'dataset/my_data'
NAME = ''

if len(sys.argv) > 1:
    NAME = str(sys.argv[1])

TITLE = '1$ Recognizer'
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, TITLE)

user_line = []
index = 1

instruction_label = pyglet.text.Label(text='Draw a form!',
                                 font_name='Times New Roman',
                                 font_size=14,
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
index_label = pyglet.text.Label(text=f'Index: {index}',
                               font_name='Times New Roman',
                               font_size=14,
                               x=WINDOW_WIDTH//1.1, y=WINDOW_HEIGHT//1.1,
                               anchor_x='center', anchor_y='center',
                               )

@window.event
def on_key_press(symbol, modifiers):
    global index
    if symbol == pyglet.window.key.Q:
        os._exit(0)
    if symbol == pyglet.window.key.SPACE:
        index += 1
    if symbol == pyglet.window.key.R:
        index = 1


@window.event
def on_mouse_press(x, y, button, modifiers):
    user_line.clear()


@window.event
def on_mouse_release(x, y, button, modifiers):
    if index < 10:
        formatted_index = f"0{index}"
    else:
        formatted_index = str(index)
    if button and pyglet.window.mouse.LEFT:
        if len(user_line) > 0:
            gesture = ET.Element('Gesture')
            gesture.set('Name', NAME + str(formatted_index))
            gesture.set('Number', str(formatted_index))
            gesture.set('NumPts', str(len(user_line)))
            for point in user_line:
                item = ET.SubElement(gesture, 'Point')
                item.set('X', str(point[0]))
                item.set('Y', str(point[1]))
            
            # create a new XML file
            mydata = ET.tostring(gesture)
            myfile = open(f'{SAVE_PATH}/{NAME}{formatted_index}.xml', 'wb')
            myfile.write(mydata)

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
    instruction_label.draw()
    quit_label.draw()
    index_label.text = f'Index: {index}'
    index_label.draw()


if __name__ == '__main__':
    pyglet.app.run()
