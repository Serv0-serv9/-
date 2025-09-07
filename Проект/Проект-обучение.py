import pygame as pg
import random
import sys
import time
from itertools import combinations
import numpy as np

pg.init()

width = 800
height = 600
txt_c = (250, 110, 0)
bckg_c = (0, 0, 0)
FPS = 60
font = pg.font.SysFont(None, 40)
minimum_speed_obstacle = height // 60
maximum_speed_obstacle = height // 40
new_rate_obstacle_added = 30
pl_movement_rate = height // 90
counting = 1
cache = 0
obstacle_size = (width / 45, height / 12.5)
collide_aura = 15
counting_seconds = 0
objects = []
loop = True
objects = []
n_states = 26255
goal_state = 3
learning_rate = 0.8
discount_factor = 0.95
exploration_prob = 0.2
cliff_detect = 0
opponent_move = [0, 0, 0, 0]
LEARNING_FILE = 'ai_learning_data.json'
#np.savetxt(LEARNING_FILE, np.zeros((n_states, 5)))

class Car(pg.sprite.Sprite):
    def __init__(self, x, filename):
        pg.sprite.Sprite.__init__(self)
        sur = pg.image.load(filename).convert_alpha()
        self.image = pg.transform.scale(sur, (width / 45, height / 12.5))
        self.rect = self.image.get_rect(center=(x, 0))

    def car_movement(self, moving_left, moving_right, moving_up, moving_down):
        if moving_left and self.rect.left > 0:
            self.rect.move_ip(-1 * pl_movement_rate, 0)
        if moving_right and self.rect.right < width:
            self.rect.move_ip(pl_movement_rate, 0)
        if moving_up and self.rect.top > 0:
            self.rect.move_ip(0, -1 * pl_movement_rate)
        if moving_down and self.rect.bottom < height:
            self.rect.move_ip(0, pl_movement_rate)

    def car_crash(self, obstacl):
        for ado in obstacl:
            if self.rect.colliderect(ado['rect']):
                return True
        return False

class Button():
    def __init__(self, x, y, wid, heig, buttonText='Button', onclickFunction=None, onePress=False, choosed=False):
        self.x = x
        self.y = y
        self.width = wid
        self.height = heig
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.alreadyPressed = False
        self.choosed = choosed

        self.fillColors = {
            'normal': (255, 255, 255),
            'hover': (102, 102, 102),
            'pressed': (51, 51, 51),
        }
        self.buttonSurface = pg.Surface((self.width, self.height))
        self.buttonRect = pg.Rect(self.x, self.y, self.width, self.height)
        self.buttonSurf = font.render(buttonText, True, (20, 20, 20))
        objects.append(self)

    def process(self):
        mousePos = pg.mouse.get_pos()
        if self.choosed:
            self.buttonSurface.fill(self.fillColors['pressed'])
        else: self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if pg.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress:
                    time.sleep(0.25)
                    exec (self.onclickFunction)
                elif not self.alreadyPressed:
                    time.sleep(0.25)
                    exec (self.onclickFunction)
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False
        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width / 2 - self.buttonSurf.get_rect().width / 2,
            self.buttonRect.height / 2 - self.buttonSurf.get_rect().height / 2
        ])
        screen_display_window.blit(self.buttonSurface, self.buttonRect)

    def recolor(self, norm, hov, pres):
        self.fillColors = {
            'normal': norm,
            'hover': hov,
            'pressed': pres,
        }

def loader(register):
    for obj in register:
        obj['rect'].move_ip(0, obj['speed'])
        if obj['rect'].top > height:
            register.remove(obj)
        screen_display_window.blit(obj['surface'], obj['rect'])

def Press_Key_shortcut():
    while True:
        for event in pg.event.get():
            if event.type != pg.QUIT:
                return True
            elif event.type != pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return True
            else: return False

def txt_objects(t, x, y):
    txt_objects = fontsize.render(t, 1, txt_c)
    txt_Rect = txt_objects.get_rect()
    txt_Rect.topleft = (x, y)
    screen_display_window.blit(txt_objects, txt_Rect)

def semi_random(low_num, high_num, log):
    s_random = random.randint(low_num, high_num)
    if max(s_random, log) - 100 <= min(s_random, log):
        return semi_random(low_num, high_num, log)
    else:
       return s_random

def timer(second):
    hour, minute = 0, 0
    xran = []
    if second >= 60:
        minute += second // 60
        second -= 60 * (second // 60)
    if minute >= 60:
        hour += minute // 60
        minute -= 60 * (minute // 60)
    for i in (hour, minute, second):
        if i < 10:
            xran.append(f"0{i}")
        else:
            xran.append(i)
    return xran

def zerkalo(x, y):
    if x > y:
        return x - y
    else:
        return 100 + (x - y) // 10

def scan_distance():
    if len(obstacle) < 1:
        obst_rect = [300, 300]
    else: obst_rect = max(obstacle, key=lambda x:x['rect'][0] + x['rect'][1])['rect']
    if obst_rect[0] + obst_rect[1] < car1.rect.topleft[0] + car1.rect.topleft[1]:
        return obst_rect
    else: return car1.rect.topleft

# Запуск
pg.init()
time_clock = pg.time.Clock()
screen_display_window = pg.display.set_mode((width, height))
pg.display.set_caption('Гонка')
menu, run, pause, setting = 0, 1, 2, 3
state = menu

back_button = Button( 270, 500, 250, 50, 'Вернуться в меню',
                      'global state, loop;global counting;state = menu;loop = False')
start_button = Button( 300, 320, 200, 50, 'Старт',
                       'global state;state = run')
setting_button = Button( 300, 390, 200, 50, 'Настройки',
                         'global state;state = setting')
quit_button = Button( 300, 460, 200, 50, 'Выход',
                      'pg.quit();sys.exit()')
choose1_button = Button( 100, 367, 150, 30, 'Вариант1',
                      'global car1;car1 = Car(10, "image/variant1.png");car1.rect.topleft = (400, 400);'
                      'self.choosed = True;choose2_button.choosed = False;choose3_button.choosed = False', choosed=True)
choose2_button = Button( 300, 367, 150, 30, 'Вариант2',
                      'global car1;car1 = Car(10, "image/variant2.jpg");car1.rect.topleft = (400, 400);'
                      'self.choosed = True;choose1_button.choosed = False;choose3_button.choosed = False')
choose3_button = Button( 500, 367, 150, 30, 'Вариант3',
                      'global car1;car1 = Car(10, "image/variant3.jpg");car1.rect.topleft = (400, 400);'
                      'self.choosed = True;choose1_button.choosed = False;choose2_button.choosed = False')

# Шрифты
fontsize = pg.font.SysFont(None, 30)

# Картинки
first = (pg.image.load('image/first.jpg'))
first = pg.transform.scale(first, (width, height))
another = []
opponents = []
for obst in range (1, 12):
    another.append(pg.image.load('image/obstacle' + str(obst) + '.jpg'))
for opp in range (1, 5):
    opponents.append('image/computer_car' + str(opp) + '.png')
opponen = opponents[0]
w_left = pg.image.load('image/left_side.png')
w_right = pg.image.load('image/right_side.png')
road_sect = pg.image.load('image/track_road.jpg')
variant1 = pg.image.load("image/variant1.png")
variant2 = pg.image.load("image/variant2.jpg")
variant3 = pg.image.load("image/variant3.jpg")
pause_fon = pg.Surface((width, height), pg.SRCALPHA)
pause_fon.fill((73, 77, 78, 250))
car1 = Car(10, 'image/variant1.png')

while counting > 0:
    start_time = pg.time.get_ticks()
    obstacle = []
    filler = []
    background = []
    fon = []
    score = 0
    opponent = Car(20, opponen)
    car1.rect.topleft = (400, 400)
    opponent.rect.topleft = (200, 400)
    pl_moving_left = pl_moving_right = pl_moving_up = pl_moving_down = False
    adding_counter_obstacle = 0
    load_background = 0
    while loop:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if state == run: state = pause
                    elif state == pause: state = run
                if event.key == pg.K_LEFT:
                    pl_moving_right = False
                    pl_moving_left = True
                elif event.key == pg.K_RIGHT:
                   pl_moving_left = False
                   pl_moving_right = True
                elif event.key == pg.K_UP:
                    pl_moving_down = False
                    pl_moving_up = True
                elif event.key == pg.K_DOWN:
                    pl_moving_up = False
                    pl_moving_down = True

            if event.type == pg.KEYUP:
                if event.key == pg.K_LEFT:
                    pl_moving_left = False
                elif event.key == pg.K_RIGHT:
                    pl_moving_right = False
                elif event.key == pg.K_UP:
                    pl_moving_up = False
                elif event.key == pg.K_DOWN:
                    pl_moving_down = False

        if state == menu:
            screen_display_window.blit(first, (0, 0))
            txt_objects('Нажмите любую кнопку для старта', (width - 320) / 2 , (height / 3))
            txt_objects('Удачи', (width - 40) / 2, (height / 3) + 30)
            objects[1].process()
            objects[2].process()
            objects[3].process()
            pg.display.update()

        if state == run:
            Q_table = np.loadtxt(LEARNING_FILE)
            timestamp = counting_seconds
            counting_seconds = (pg.time.get_ticks() - start_time) // 1000
            adding_counter_obstacle += 1 # Препятствия
            load_background +=1
            if (counting_seconds % 15 == 0 and new_rate_obstacle_added > 8 and counting_seconds != 0
                    and timestamp != counting_seconds):
                new_rate_obstacle_added -= 1
            if adding_counter_obstacle >= new_rate_obstacle_added:
                adding_counter_obstacle = 0
                obst_rect = semi_random((width // 5) + 10, ((4 * width) // 5) - 10, cache)
                new_obstacle = {'rect': pg.Rect(obst_rect, -30, obstacle_size[0], obstacle_size[1]),
                                'speed': random.randint(minimum_speed_obstacle, maximum_speed_obstacle),
                                'surface': pg.transform.scale(random.choice(another), obstacle_size),
                                'register': pg.Surface((30, 40)),
                                    }
                obstacle.append(new_obstacle)
                filler.append(new_obstacle)
                cache = obst_rect
            if load_background == 10:
                load_background = 0
                left_side = {'rect': pg.Rect(0, -100, 163, 600),#height, 800 - width
                            'speed': 10,
                            'surface': pg.transform.scale(w_left, (160, height)),
                             }
                background.append(left_side)
                right_side = {'rect': pg.Rect(637, -100, 160, 600),
                             'speed': 10,
                             'surface': pg.transform.scale(w_right, (160, height)),
                              }
                background.append(right_side)
                road = {'rect': pg.Rect(160, -100, 480, 600),
                             'speed': 10,
                             'surface': pg.transform.scale(road_sect, (480, height)),
                              }
                fon.append(road)

            car1.car_movement(pl_moving_left, pl_moving_right, pl_moving_up, pl_moving_down)

            # Отображение игры в экране
            screen_display_window.fill(bckg_c)

            loader(fon)

            # Отображение счета
            txt_objects('Счет: %s' % (score), width / 4, height / 60)

            txt_objects(f"{timer(counting_seconds)[0]} : {timer(counting_seconds)[1]} : {timer(counting_seconds)[2]}", 500, 10)

            screen_display_window.blit(car1.image, car1.rect)
            screen_display_window.blit(opponent.image, opponent.rect)

            loader(obstacle)
            loader(background)

            pg.display.update()

            if opponent.rect.topleft[0] - 160 < 60:
                cliff_detect = 1
            elif 640 - opponent.rect.topleft[0] < 60:
                cliff_detect = 2

            # Проверка коллизии
            if car1.car_crash(obstacle) or car1.car_crash(background):
                time.sleep(1)
                txt_objects('Конец', (width - 90) / 2, (height - 10) / 3)
                txt_objects('Нажмите любую кнопку для рестарта', (width - 350) / 2, (height - 10) / 2.75)
                pg.display.update()
                time.sleep(1)
                break
            for obst1, obst2 in combinations(obstacle, 2):
                while (abs(obst2['rect'][0] - obst1['rect'][0]) < obstacle_size[0] + collide_aura and
                        abs(obst2['rect'][1] - obst1['rect'][1]) < obstacle_size[1] + collide_aura):
                        obst2['rect'][0] -= random.choice([1, -1])

            current_state = int(str(cliff_detect) + str(zerkalo(opponent.rect.topleft[0], scan_distance()[0]))
                                + str(abs(scan_distance()[1] // 10)))
            if np.random.rand() < exploration_prob:
                action = np.random.randint(0, 4)
            else:
                action = np.argmax(Q_table[current_state])
            if action != 4:
                opponent_move[action] = 1
            else:
                opponent_move = [0, 0, 0, 0]
            opponent.car_movement(opponent_move[0], opponent_move[1], opponent_move[2], opponent_move[3])
            next_state = int(str(cliff_detect) + str(zerkalo(opponent.rect.topleft[0], scan_distance()[0]))
                             + str(abs(scan_distance()[1] // 10)))
            reward = -1 if opponent.car_crash(obstacle) or opponent.car_crash(background) == True else 0
            Q_table[current_state, action] += learning_rate * reward + discount_factor * np.max(Q_table[next_state]) - \
                                              Q_table[current_state, action]
            if reward == -1:
                c = np.savetxt(LEARNING_FILE, Q_table)
                Q_table = np.loadtxt(LEARNING_FILE)
            if opponent.car_crash(obstacle) or opponent.car_crash(background):
                opponent.rect.topleft = (width / 4, height - 100)
            #print(current_state)

            for obst in filler:
                if abs(obst['rect'][1] - car1.rect[1]) <= 10:
                    score += 100
                    filler.remove(obst)

        time_clock.tick(FPS)

            # Конец игры
        if state == pause:
            pg.display.flip()
            screen_display_window.blit(pause_fon, (0, 0))
            txt_objects('Пауза', (width - 90) / 2, (height - 10) / 3)
            txt_objects('Нажмите ESC чтобы продолжить', (width - 350) / 2, (height - 10) / 2.75)
            objects[0].process()

        if state == setting:
            pg.display.flip()
            screen_display_window.blit(pause_fon, (0, 0))
            screen_display_window.blit(variant1, (150, 250))
            screen_display_window.blit(variant2, (370, 250))
            screen_display_window.blit(variant3, (570, 250))
            txt_objects('Настройки', (width - 90) /2, height / 60)
            objects[4].process()
            objects[5].process()
            objects[6].process()
            objects[0].process()

    counting -= 1
    if counting < 1:
        loop = True
        counting = 1