
import pyglet
from pyglet import shapes
import random

from prediction_model import THREE_GESTURES

THRESHOLD = 100
SCORE_POINTS = 10

# Collision Oversize helps the player:
# - does not to have to hit the note exactly
# - player hits the note a bit before and a bit after collision
NOTE_COLLISION_OVERSIZE = 15
PLAYER_COLLISION_OVERSIZE_FRONT = 4
PLAYER_COLLISION_OVERSIZE_BACK = 15

hagrid_fight_path = 'images/hagrid.png'
dumbledore_fight_path = 'images/dumbeldore.png'
voldemort_fight_path = 'images/voldemort.png'


pigtail_path = 'images/pigtail.png'
carret_path = 'images/carret.png'
x_path = 'images/x.png'

IMG_SCALE_HAGRID = 0.5
IMG_SCALE_DUMBELDORE = 1.5
IMG_SCALE_VOLDEMORT = 1.5
SPELL_SCALE = 0.1
LABEL_COLOR_BLACK = (1, 1, 1, 255)


class HarryPotterGame:

    def __init__(self, window_width, window_height):
        self.window_width = window_width
        self.window_height = window_height
        self.batch = pyglet.graphics.Batch()
        self.notes_batch = pyglet.graphics.Batch()
        self.score = 0
        self.game_state = 0
        self.results = []

        self.hagrid = pyglet.image.load(hagrid_fight_path)
        self.dumbledore = pyglet.image.load(dumbledore_fight_path)
        self.voldemort = pyglet.image.load(voldemort_fight_path)

        self.pigtail = pyglet.image.load(pigtail_path)
        self.carret = pyglet.image.load(carret_path)
        self.x = pyglet.image.load(x_path)

    def create_sprite(self, img, name):
        sprite = pyglet.sprite.Sprite(img=img)
        sprite.y = self.window_height // 2.5
        sprite.x = self.window_width // 5.0
        sprite.name = name
        return sprite

    def create_label(self, text, x, y, size):
        label = pyglet.text.Label(text=text,
                                  font_name='Times New Roman',
                                  font_size=size,
                                  bold=True,
                                  x=x, y=y,
                                  anchor_x='center', anchor_y='center',
                                  )
        label.color = LABEL_COLOR_BLACK
        return label

    def update(self, user_line):
        skip_label = self.create_label('Press N to continue!', self.window_width//2, self.window_height//1.4, 15)

        match(self.game_state):
            case 0:
                intro = fight_label = self.create_label('Defeat all wizards!', self.window_width//2, self.window_height//1.1, 24)
                wizard_intro = fight_label = self.create_label('You have the following spells:', self.window_width//2, self.window_height//1.3, 18)
                spell_1 = fight_label = self.create_label('luminus:', self.window_width//2, self.window_height//1.6, 14)
                spell_2 = fight_label = self.create_label('avada kedabra:', self.window_width//2, self.window_height//2.0, 14)
                spell_3 = fight_label = self.create_label('erase:', self.window_width//2, self.window_height//2.6, 14)

                intro.draw()
                wizard_intro.draw()
                spell_1.draw()
                spell_2.draw()
                spell_3.draw()

                pigtail_sprite, sprite_name = (self.pigtail, 'pigtail')
                pigtail = self.create_sprite(pigtail_sprite, sprite_name)
                pigtail.scale = SPELL_SCALE
                pigtail.x = self.window_width // 1.5
                pigtail.y = self.window_height // 1.6 - pigtail.height / 2
                pigtail.draw()

                carret_sprite, sprite_name = (self.carret, 'carret')
                carret = self.create_sprite(carret_sprite, sprite_name)
                carret.scale = SPELL_SCALE
                carret.x = self.window_width // 1.5
                carret.y = self.window_height // 2.0 - carret.height / 2
                carret.draw()

                x_sprite, sprite_name = (self.x, 'x')
                x = self.create_sprite(x_sprite, sprite_name)
                x.scale = SPELL_SCALE
                x.x = self.window_width // 1.5
                x.y = self.window_height // 2.6 - x.height / 2
                x.draw()

                start_label = pyglet.text.Label(text='Press SPACE to start!',
                                                font_name='Times New Roman',
                                                font_size=24,
                                                bold=True,
                                                x=self.window_width//2, y=self.window_height//4,
                                                anchor_x='center', anchor_y='center',
                                                )
                start_label.color = LABEL_COLOR_BLACK
                start_label.draw()

            case 1:
                hagrid_sprite, sprite_name = (self.hagrid, 'hagrid')
                hagrid = self.create_sprite(hagrid_sprite, sprite_name)
                hagrid.scale = IMG_SCALE_HAGRID
                hagrid.draw()

                fight_label = self.create_label('Besiege Hagrid', self.window_width//2, self.window_height//1.1, 24)
                fight_label.draw()

                draw_label = self.create_label('Zeichne hier mit deiner Maus: ---------------------------------------', self.window_width//3.0, self.window_height//2.8, 14)
                draw_label.draw()

                for x, y in user_line:
                    point = shapes.Circle(x, y, 5, color=(255, 0, 0))
                    point.draw()

            case 1.5:
                result_label = self.create_label(self.results[0], self.window_width//2, self.window_height//1.1, 24)
                result_label.draw()
                skip_label.draw()
            case 2:
                dumbeldore_sprite, sprite_name = (self.dumbledore, 'dumbeldore')
                dumbeldore = self.create_sprite(dumbeldore_sprite, sprite_name)
                dumbeldore.scale = IMG_SCALE_DUMBELDORE
                dumbeldore.draw()

                fight_label = self.create_label('Besiege Dumbeldore', self.window_width//2, self.window_height//1.1, 24)
                fight_label.draw()

                draw_label = self.create_label('Zeichne hier mit deiner Maus: ---------------------------------------', self.window_width//3.0, self.window_height//2.8, 14)
                draw_label.draw()

                for x, y in user_line:
                    point = shapes.Circle(x, y, 5, color=(255, 0, 0))
                    point.draw()

            case 2.5:
                result_label = self.create_label(self.results[1], self.window_width//2, self.window_height//1.1, 24)
                result_label.draw()
                skip_label.draw()

            case 3:
                voldemort_sprite, sprite_name = (self.voldemort, 'voldemort')
                voldemort = self.create_sprite(voldemort_sprite, sprite_name)
                voldemort.scale = IMG_SCALE_VOLDEMORT
                voldemort.draw()

                fight_label = self.create_label('Besiege Voldemort', self.window_width//2, self.window_height//1.1, 24)
                fight_label.draw()

                draw_label = self.create_label('Zeichne hier mit deiner Maus: ---------------------------------------', self.window_width//3.0, self.window_height//2.8, 14)
                draw_label.draw()

                for x, y in user_line:
                    point = shapes.Circle(x, y, 5, color=(255, 0, 0))
                    point.draw()

            case 3.5:
                title = self.create_label("Finale Übersicht", self.window_width // 2, self.window_height // 1.1, 30)
                title.draw()

                add = 0.2
                height = 1.8
                for i in range(3):
                    result_label = self.create_label(self.results[i], self.window_width // 2, self.window_height // height, 24)
                    result_label.draw()
                    height += add

                final_score = self.create_label(f'Finaler Score = {self.score}', self.window_width // 2, self.window_height // 3.4, 30)
                final_score.draw()

                restart = self.create_label("press R to restart", self.window_width // 2, self.window_height // 4.5, 14)
                restart.draw()

    def draw(self):
        score_label = pyglet.text.Label(text=f'Score: {self.score}',
                                        font_name='Arial',
                                        font_size=15,
                                        bold=True,
                                        x=self.window_width - (self.window_width//1.1), y=self.window_height//1.1, batch=self.batch)
        score_label.color = LABEL_COLOR_BLACK

        if self.game_state != 3.5:
            self.batch.draw()

    def fight(self, input_user):
        com_choices = ['scissor', 'stone', 'paper']
        com_attack = random.choice(com_choices)

        player_attack = 'paper'
        match(input_user):
            case 'pigtail':
                player_attack = 'paper'
            case 'carret':
                player_attack = 'stone'
            case 'x':
                player_attack = 'scissor'
            case _:
                player_attack = random.choice(THREE_GESTURES)

        result_text = ''
        if player_attack == com_attack:
            result_text = 'Draw!'
            self.score += 0

        elif (player_attack == 'scissor' and com_attack == 'paper') or \
            (player_attack == 'stone' and com_attack == 'scissor') or \
                (player_attack == 'paper' and com_attack == 'stone'):
            result_text = 'You won!'
            self.score += 1
        else:
            result_text = 'Wizard won!'
            self.score -= 1

        self.results.append(result_text)
        self.game_state = self.game_state + 0.5

        print(f'Computer: {com_attack} || Player: {player_attack}')

    def restart(self):
        self.score = 0
        self.game_state = 0
        self.results.clear()
