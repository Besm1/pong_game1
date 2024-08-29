import math

import arcade
import time

# print(help(arcade))

"""
Игра "пинг-понг".

Надо как можно дольше отбивать шарик ракеткой, не давая ему провалиться "в подвал". 
У игрока за игру есть определённое количество попыток (раундов). Как только шарик падает в подвал, раунд заканчивается, 
    и игрок теряет одну попытку. Как только у игрока не остаётся ни одной попытки, игра заканчивается.
Во время игры ведётся счёт, это количество отражённых ударов.

Управление:
    Подача - клавиша "пробел"
    Движение ракетки - стрелки влево и вправо
    Начало новой игры - клавиша "Enter"    

Особенности:
    * Ракетка имеет закруглённые края в виде полукруга, и эта геометрия учитывается при отбивании шарика краем ракетки.
    * Если при отражении щарика ракетка находится в движении, то это немного влияет на горизонтальную скорость шарика 
        (увеличивает, если направления движения ракетки и шарика совпадают, или уменьшает в противном случае)
         
"""

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = 'Pong Game'

COLLISION_WIDTH = 2  # Глубина прогибв ракетки при столкновении (выяснилось эксперименальным путём)

INIT_BALL_SPEED_X = 2  # Начальная скорость шара
INIT_BALL_SPEED_Y = 4

BAR_MOVEMENT_SPEED = 5  # Скорость ракетки при движении

INIT_TRIALS_QTY = 3  # Начальное количество попыток


class Bar(arcade.Sprite):
    def __init__(self):
        super().__init__('Bar.png', 1)

    def update(self):  # Движение ракетки
        if (self.change_x > 0 and self.right < SCREEN_WIDTH) or (self.change_x < 0 and self.left > 0):
            self.center_x += self.change_x  # Двигаемся, если не длостигли краёв
        else:
            self.change_x = 0   # Достигли краёв


class Ball(arcade.Sprite):
    def __init__(self):
        super().__init__('Ball.png', 1)

    def setup(self):
        pass

    def update(self):  # Движение шара
        if self.right >= SCREEN_WIDTH or self.left <= 0:    # При ударе об край меняется знак скорости по x
            self.change_x = -self.change_x  # Отражаемся от бортов
        if self.top >= SCREEN_HEIGHT:
            self.change_y = -self.change_y  # Отражаемся от потолка
        self.center_x += self.change_x  # Двигаемся
        self.center_y += self.change_y


class Game(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.bar = Bar()
        self.ball = Ball()
        self.setup_game()   # Инициализация игры из 3-х раундов
        self.setup_round()  # Инициализация раунда

    def on_draw(self):
        self.clear(color=(255, 255, 255))
        self.bar.draw()      # Рисуем объекты
        self.ball.draw()
        # Пишем остаток жизней и счёт
        arcade.draw_text(f'Lives left: {self.lives_left}' +
                         ('   GAME OVER! <ENTER> to start new game.' if self.lives_left == 0 else '')
                         , 10, 20, arcade.color.BLACK, 14)
        arcade.draw_text(text=f'Score: {self.ball_hits}', start_x=SCREEN_WIDTH * 0.75, start_y=20,
                         color=arcade.color.BLACK, font_size=14)

    def setup_game(self):
        self.lives_left = INIT_TRIALS_QTY
        self.ball_hits = 0

    def setup_round(self):
        # Позиционируем ракетку
        self.bar.center_x = SCREEN_WIDTH / 2
        self.bar.center_y = SCREEN_HEIGHT / 5
        # Задаём скорость движения ракетки
        self.change_x = 0
        # ПОзиционируем шар
        self.ball.center_x = self.bar.center_x + self.bar.width / 10  # Сместим шарик чуть вправо от середины ракетки
        self.ball.bottom = self.bar.top
        #  Задаём скорость движения шара
        self.ball.change_x = 0  # INIT_BALL_SPEED_X
        self.ball.change_y = 0  # INIT_BALL_SPEED_Y

        # Установки:
        self.in_collision = False  # Не в столкновении
        self.in_game_start = True  # На старте игры

    def update(self, delta_time: float):
        if self.ball.top <= 0 and not self.in_game_start:  # Упустили шар
            self.lives_left -= 1
            time.sleep(3)
            self.in_game_start = True
            if self.lives_left > 0:
                self.setup_round()
        elif arcade.check_for_collision(self.bar, self.ball):
            if not self.in_collision:
                # if self.ball.bottom + COLLISION_WIDTH >= self.bar.top:
                #     self.ball.change_y = -self.ball.change_y
                # else:
                # self.bar_right_center_x = self.bar.right - self.bar.height / 2
                # self.bar_left_center_x = self.bar.left + self.bar.height / 2
                # if self.ball.center_x > self.bar_right_center_x:  # Шар справа
                #     self.ball.center_y <= self.bar.center_y:
                # self.ball.change_y *=
                self.ball_hits += 1
                self.in_collision = True
                # self.ball.change_y = -self.ball.change_y
                self.ball.change_x, self.ball.change_y = self.change_ball_speed(
                    ball_center=(self.ball.center_x, self.ball.center_y),
                    bar_center=(self.bar.center_x, self.bar.center_y),
                    bar_dim=(self.bar.width, self.bar.height),
                    ball_speed_i=(self.ball.change_x, self.ball.change_y),
                    bar_speed=self.bar.change_x
                )
        else:
            self.in_collision = False

        if ((not self.in_game_start) or
                ((self.bar.change_x > 0 and self.bar.right < SCREEN_WIDTH) or (
                  self.bar.change_x < 0 and self.bar.left > 0))):
            self.ball.update()
        self.bar.update()

    def change_ball_speed(self, ball_center, bar_center, bar_dim, ball_speed_i, bar_speed):
        """
        Рассчитывает новый вектор скорости шара при отражении от ракетки в засисмости от:
            - вектора скорости падения
            - относительного положения шара и ракетки
            - скорости движения ракетки
        :return: ball_speed_r = (change_x, change_y) - вектор скорости отражённого шара
        """
        bar_center_left = (
        bar_center[0] - bar_dim[0] / 2 + bar_dim[1] / 2, bar_center[1])  # центр левого полукруга ракетки
        bar_center_right = (
        bar_center[0] + bar_dim[0] / 2 - bar_dim[1] / 2, bar_center[1])  # центр правого полукруга ракетки
        """ atan всегда возвращает значение угла, лежащего в 1-й или 4-й четвертях. Поскольку угол падения всегда отрицательный,
        а нам нужен противоположный угол, то если вернулся угол отрицательный, нам надо добавить 180 град:  
        """
        angle_i = math.atan2(ball_speed_i[1], ball_speed_i[0])  # Угол, противоположный  углу падения
        if angle_i < 0:
            angle_i += math.pi  # Угол скорости всегда отрицательный при столкновении

        # Вычислим угол нормали в момент столкновения. Он зависит от точки падения шара.
        # Если он падает на ровную поверхность, то нормаль = 90 град.
        # Если падает на торец, то нормаль - это угол вектора от центра закругления ракетки к центру шара в момент столкновения.
        if ball_center[0] >= bar_center_left[0]:
            if ball_center[0] <= bar_center_right[0]:
                # Столкновение с ровной поверхностью ракетки
                angle_n = math.pi / 2
            else:  # Столкновение с правым торцем ракетки
                angle_n = math.atan2(ball_center[1] - bar_center_right[1],
                                     ball_center[0] - bar_center_right[0])
        else:  # Столкновение с левым торцем ракетки
            angle_n = math.atan2(ball_center[1] - bar_center_left[1],
                                 ball_center[0] - bar_center_left[0])
            angle_n = angle_n + (math.pi if angle_n < 0 else -math.pi)

        if math.fabs(angle_i - angle_n) < math.pi / 2: # шар упал под острым углом на поверхность отражения - отскочил!
            angle_r = 2 * angle_n - angle_i     # тогда рассчитаем угол отражения (с учётом, что angle_i - угол, _обратный_ углу падения):
            # angle_r = angle_n + (angle_n - angle_i) = 2 * angle_n - angle_i
            speed_i_modulus = (ball_speed_i[0] ** 2 + ball_speed_i[1] ** 2) ** 0.5  # Вычислим модуль скорости падения
            # А скорость отражения по абс.величине должна быть такой же.
            # Добавка "+ bar_speed / 5" - добавляет 20% скорости движения ракетки. Направление движения ракетки учитывается автоматически.
            return speed_i_modulus * math.cos(angle_r) + bar_speed / 5, speed_i_modulus * math.sin(angle_r)
        else:  # Шар упал под тупым углом к плоскости отражения - такое может быть
            # только на краях ракетки, когда он летит "вскользь". В этом случае скорость не меняется.
            return ball_speed_i[0], ball_speed_i[1]

    def on_key_press(self, symbol: int, modifiers: int):
        if self.lives_left > 0: #Игра не закончена
            if symbol == arcade.key.RIGHT and self.bar.right < SCREEN_WIDTH: # движ каретки в пределах поля
                self.bar.change_x = BAR_MOVEMENT_SPEED
            elif symbol == arcade.key.LEFT and self.bar.left > 0 :
                self.bar.change_x = -BAR_MOVEMENT_SPEED
            elif symbol in (arcade.key.LEFT, arcade.key.RIGHT):
                bar_is_moving = False

            # В начале раунда (до подачи) шарик двигается вместе с ракеткой
            if self.in_game_start:
                self.ball.change_x = self.bar.change_x

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.RIGHT or symbol == arcade.key.LEFT and self.lives_left > 0:  # останов ракетки
            self.bar.change_x = 0
            if self.in_game_start:
                self.ball.change_x = 0
        elif symbol == arcade.key.SPACE and self.in_game_start and self.lives_left > 0:  # Подача
            self.ball.change_x = INIT_BALL_SPEED_X
            self.ball.change_y = INIT_BALL_SPEED_Y
            self.in_game_start = False      # Всё, не в начале раунда
        elif symbol == arcade.key.ENTER and self.lives_left == 0:   # Начало 3-раундовой игры
            self.setup_game()   # Инициализируем игру,
            self.setup_round()  # Инициализируем раунд


if __name__ == '__main__':
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
