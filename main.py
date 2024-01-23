import random
import pygame
import pyganim
from pygame import *
import sys
import os

# Объявляем переменные
WIN_WIDTH = 800  # Ширина создаваемого окна
WIN_HEIGHT = 640  # Высота
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)  # Группируем ширину и высоту в одну переменную
BACKGROUND_COLOR = "#CCCCFF"

MOVE_SPEED = 6
SLOW_DOWN = 3.5  # замедленное падение
EXTRA_JUMP = 9
WIDTH = 21.5
HEIGHT = 30.5
COLOR = "#CCCCFF"
JUMP_POWER = 10
GRAVITY = 0.35  # Сила, которая будет тянуть нас вниз
ANIMATION_DELAY = 0.1  # скорость смены кадров
ANIMATION_SUPER_SPEED_DELAY = 0.05  # скорость смены кадров при ускорении

ANIMATION_RIGHT = [('data/r1.png'),
                   ('data/r2.png'),
                   ('data/r3.png'),
                   ('data/r4.png'),
                   ('data/r5.png')]
ANIMATION_LEFT = [('data/l1.png'),
                  ('data/l2.png'),
                  ('data/l3.png'),
                  ('data/l4.png'),
                  ('data/l5.png')]
ANIMATION_JUMP_LEFT = [('data/jl.png', 0.1)]
ANIMATION_JUMP_RIGHT = [('data/jr.png', 0.1)]
ANIMATION_STAY_LEFT = [('data/l1.png', 0.1)]
ANIMATION_STAY_RIGHT = [('data/r1.png', 0.1)]

MONSTER_WIDTH = 32
MONSTER_HEIGHT = 32
MONSTER_COLOR = "#2110FF"

ANIMATION_MONSTERHORYSONTAL = [('data/monstr1.png'),
                               ('data/monstr2.png')]

PLATFORM_WIDTH = 32
PLATFORM_HEIGHT = 32
PLATFORM_COLOR = "#000000"

ANIMATION_BLOCKTELEPORT = [
    ('data/portal2.png'),
    ('data/portal1.png')]


class Platform(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.image = Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image.fill(Color(PLATFORM_COLOR))
        self.image = image.load("data/metal.png")
        self.image.set_colorkey(Color(PLATFORM_COLOR))
        self.rect = Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


class BlockDie(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = image.load("data/spike.png")


class BlockTeleport(Platform):
    def __init__(self, x, y, goX, goY):
        Platform.__init__(self, x, y)
        self.goX = goX  # координаты назначения перемещения
        self.goY = goY  # координаты назначения перемещения
        boltAnim = []
        for anim in ANIMATION_BLOCKTELEPORT:
            boltAnim.append((anim, 0.3))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.play()

    def update(self):
        self.image.fill(Color(PLATFORM_COLOR))
        self.boltAnim.blit(self.image, (0, 0))


class Door(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = image.load("data/door.png")


class Monster(sprite.Sprite):
    def __init__(self, x, y, left, up, maxLengthLeft, maxLengthUp):
        sprite.Sprite.__init__(self)
        self.image = Surface((MONSTER_WIDTH, MONSTER_HEIGHT))
        self.image.fill(Color(MONSTER_COLOR))
        self.rect = Rect(x, y, MONSTER_WIDTH, MONSTER_HEIGHT)
        self.image.set_colorkey(Color(MONSTER_COLOR))
        self.startX = x  # начальные координаты
        self.startY = y
        self.maxLengthLeft = maxLengthLeft  # максимальное расстояние, которое может пройти в одну сторону
        self.maxLengthUp = maxLengthUp  # максимальное расстояние, которое может пройти в одну сторону, вертикаль
        self.xvel = left  # cкорость передвижения по горизонтали, 0 - стоит на месте
        self.yvel = up  # скорость движения по вертикали, 0 - не двигается
        boltAnim = []
        for anim in ANIMATION_MONSTERHORYSONTAL:
            boltAnim.append((anim, 0.6))
        self.boltAnim = pyganim.PygAnimation(boltAnim)
        self.boltAnim.play()

    def update(self, platforms):  # по принципу героя

        self.image.fill(Color(MONSTER_COLOR))
        self.boltAnim.blit(self.image, (0, 0))

        self.rect.y += self.yvel
        self.rect.x += self.xvel

        self.collide(platforms)

        if (abs(self.startX - self.rect.x) > self.maxLengthLeft):
            self.xvel = -self.xvel  # если прошли максимальное растояние, то идеи в обратную сторону
        if (abs(self.startY - self.rect.y) > self.maxLengthUp):
            self.yvel = -self.yvel  # если прошли максимальное растояние, то идеи в обратную сторону, вертикаль

    def collide(self, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p) and self != p:  # если с чем-то или кем-то столкнулись
                self.xvel = - self.xvel  # то поворачиваем в обратную сторону
                self.yvel = - self.yvel


class Player(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.xvel = 0  # скорость перемещения. 0 - стоять на месте
        self.startX = x  # Начальная позиция Х, пригодится когда будем переигрывать уровень
        self.startY = y
        self.yvel = 0  # скорость вертикального перемещения
        self.onGround = False  # На земле ли я?
        self.image = Surface((WIDTH, HEIGHT))
        self.image.fill(Color(COLOR))
        self.rect = Rect(x, y, WIDTH, HEIGHT)  # прямоугольный объект
        self.image.set_colorkey(Color(COLOR))  # делаем фон прозрачным
        self.side = 'right'
        self.charge = False
        #        Анимация движения вправо
        boltAnim = []
        boltAnimSuperSpeed = []
        for anim in ANIMATION_RIGHT:
            boltAnim.append((anim, ANIMATION_DELAY))
            boltAnimSuperSpeed.append((anim, ANIMATION_SUPER_SPEED_DELAY))
        self.boltAnimRight = pyganim.PygAnimation(boltAnim)
        self.boltAnimRight.play()
        self.boltAnimRightSuperSpeed = pyganim.PygAnimation(boltAnimSuperSpeed)
        self.boltAnimRightSuperSpeed.play()
        #        Анимация движения влево
        boltAnim = []
        boltAnimSuperSpeed = []
        for anim in ANIMATION_LEFT:
            boltAnim.append((anim, ANIMATION_DELAY))
            boltAnimSuperSpeed.append((anim, ANIMATION_SUPER_SPEED_DELAY))
        self.boltAnimLeft = pyganim.PygAnimation(boltAnim)
        self.boltAnimLeft.play()
        self.boltAnimLeftSuperSpeed = pyganim.PygAnimation(boltAnimSuperSpeed)
        self.boltAnimLeftSuperSpeed.play()

        self.boltAnimStayLeft = pyganim.PygAnimation(ANIMATION_STAY_LEFT)
        self.boltAnimStayLeft.play()
        self.boltAnimStayLeft.blit(self.image, (0, 0))  # По-умолчанию, стоим

        self.boltAnimStayRight = pyganim.PygAnimation(ANIMATION_STAY_RIGHT)
        self.boltAnimStayRight.play()
        self.boltAnimStayRight.blit(self.image, (0, 0))  # По-умолчанию, стоим

        self.boltAnimJumpLeft = pyganim.PygAnimation(ANIMATION_JUMP_LEFT)
        self.boltAnimJumpLeft.play()

        self.boltAnimJumpRight = pyganim.PygAnimation(ANIMATION_JUMP_RIGHT)
        self.boltAnimJumpRight.play()

        self.winner = False

    def update(self, left, right, up, flying, platforms):

        if up:
            if self.onGround:  # прыгаем, только когда можем оттолкнуться от земли
                self.yvel = -JUMP_POWER
                self.image.fill(Color(COLOR))
                if self.side == 'left':
                    self.boltAnimJumpLeft.blit(self.image, (0, 0))
                else:
                    self.boltAnimJumpRight.blit(self.image, (0, 0))

        if left:
            self.xvel = -MOVE_SPEED  # Лево = x- n
            self.image.fill(Color(COLOR))
            self.side = 'left'
            if up or flying:  # если же прыгаем
                self.boltAnimJumpLeft.blit(self.image, (0, 0))  # отображаем анимацию прыжка
            elif not up:  # не прыгаем
                self.boltAnimLeft.blit(self.image, (0, 0))  # отображаем анимацию движения

        if right:
            self.xvel = MOVE_SPEED  # Право = x + n
            self.image.fill(Color(COLOR))
            self.side = 'right'
            if up or flying:
                self.boltAnimJumpRight.blit(self.image, (0, 0))
            elif not up:
                self.boltAnimRight.blit(self.image, (0, 0))

        if not (left or right):  # стоим, когда нет указаний идти
            self.xvel = 0
            if not (up or flying):
                self.image.fill(Color(COLOR))
                if self.side == 'left':
                    self.boltAnimStayLeft.blit(self.image, (0, 0))
                else:
                    self.boltAnimStayRight.blit(self.image, (0, 0))

        if self.onGround:
            self.charge = True

        if not self.onGround:
            if flying and self.charge:
                self.yvel = 0
                self.yvel -= EXTRA_JUMP
                self.charge = False
            elif flying and self.yvel > 3.4:
                self.yvel = SLOW_DOWN
            else:
                self.yvel += GRAVITY

        self.onGround = False;  # Мы не знаем, когда мы на земле((
        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms)

        self.rect.x += self.xvel  # переносим свои положение на xvel
        self.collide(self.xvel, 0, platforms)

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p):  # если есть пересечение платформы с игроком
                if isinstance(p, BlockDie) or isinstance(p,
                                                         Monster):  # если пересакаемый блок blocks.BlockDie или Monster
                    self.die()  # умираем
                elif isinstance(p, BlockTeleport):
                    self.teleporting(p.goX, p.goY)
                elif isinstance(p, Door):  # если коснулись принцессы
                    self.winner = True  # победили!!!
                else:
                    if xvel > 0:  # если движется вправо
                        self.rect.right = p.rect.left  # то не движется вправо

                    if xvel < 0:  # если движется влево
                        self.rect.left = p.rect.right  # то не движется влево

                    if yvel > 0:  # если падает вниз
                        self.rect.bottom = p.rect.top  # то не падает вниз
                        self.onGround = True  # и становится на что-то твердое
                        self.yvel = 0  # и энергия падения пропадает

                    if yvel < 0:  # если движется вверх
                        self.rect.top = p.rect.bottom  # то не движется вверх
                        self.yvel = 0  # и энергия прыжка пропадает

    def teleporting(self, goX, goY):
        self.rect.x = goX
        self.rect.y = goY

    def die(self):
        time.wait(500)
        self.teleporting(self.startX, self.startY)  # перемещаемся в начальные координаты


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WIN_WIDTH / 2, -t + WIN_HEIGHT / 2

    l = min(0, l)  # Не движемся дальше левой границы
    l = max(-(camera.width - WIN_WIDTH), l)  # Не движемся дальше правой границы
    t = max(-(camera.height - WIN_HEIGHT), t)  # Не движемся дальше нижней границы
    t = min(0, t)  # Не движемся дальше верхней границы

    return Rect(l, t, w, h)


def loadLevel(lvl):
    global playerX, playerY  # объявляем глобальные переменные, это координаты героя

    levelFile = open('levels/' + lvl)
    line = " "
    commands = []
    while line[0] != "/":  # пока не нашли символ завершения файла
        line = levelFile.readline()  # считываем построчно
        if line[0] == "[":  # если нашли символ начала уровня
            while line[0] != "]":  # то, пока не нашли символ конца уровня
                line = levelFile.readline()  # считываем построчно уровень
                if line[0] != "]":  # и если нет символа конца уровня
                    endLine = line.find("|")  # то ищем символ конца строки
                    level.append(line[0: endLine])  # и добавляем в уровень строку от начала до символа "|"

        if line[0] != "":  # если строка не пустая
            commands = line.split()  # разбиваем ее на отдельные команды
            if len(commands) > 1:  # если количество команд > 1, то ищем эти команды
                if commands[0] == "player":  # если первая команда - player
                    playerX = int(commands[1])  # то записываем координаты героя
                    playerY = int(commands[2])
                if commands[0] == "portal":  # если первая команда portal, то создаем портал
                    tp = BlockTeleport(int(commands[1]), int(commands[2]), int(commands[3]), int(commands[4]))
                    entities.add(tp)
                    platforms.append(tp)
                    animatedEntities.add(tp)
                if commands[0] == "monster":  # если первая команда monster, то создаем монстра
                    mn = Monster(int(commands[1]), int(commands[2]), int(commands[3]), int(commands[4]),
                                 int(commands[5]), int(commands[6]))
                    entities.add(mn)
                    platforms.append(mn)
                    monsters.add(mn)


def terminate():
    pygame.quit()
    sys.exit


pygame.init()
screen_size = (WIN_WIDTH, WIN_HEIGHT)
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
FPS = 50


def start_screen():  # Начальный экран
    intro_text = ["                 Платформер", "",
                  "",
                  "Чтобы выбрать уровень нажмите:",
                  "                     1,   2,   3"]

    image = pygame.image.load('data/intro.png')
    image.set_colorkey(COLOR)

    fon = pygame.transform.scale(image, (WIN_WIDTH, WIN_HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 190
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 250
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == K_1:
                main('1.txt')
                return
            elif event.type == pygame.KEYDOWN and event.key == K_2:
                main('2.txt')
                return
            elif event.type == pygame.KEYDOWN and event.key == K_3:
                main('3.txt')
                return
        pygame.display.flip()
        clock.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit


pygame.init()
screen_size = (WIN_WIDTH, WIN_HEIGHT)
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
FPS = 50


def gameover_screen():  # Экран победы
    intro_text = ["Конец игры!"]

    image = pygame.image.load('data/fin.jpg')
    image.set_colorkey(COLOR)

    fon = pygame.transform.scale(image, (WIN_WIDTH, WIN_HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = 245
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 300
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
                return
        pygame.display.flip()
        clock.tick(FPS)


def main(lvl):
    loadLevel(lvl)
    mscs = ['mischievous_robot.mp3', 'gestation.mp3', 'quiet.mp3']
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()  # Инициация PyGame, обязательная строчка
    pygame.mixer.init()
    pygame.mixer.music.load('sounds/' + random.choice(mscs))
    pygame.mixer.music.play(-1)
    vol = 0.5
    pygame.mixer.music.set_volume(vol)
    screen = pygame.display.set_mode(DISPLAY)  # Создаем окошко
    pygame.display.set_caption("Super Mario Boy")  # Пишем в шапку
    bg = Surface((WIN_WIDTH, WIN_HEIGHT))  # Создание видимой поверхности
    # будем использовать как фон
    bg.fill(Color(BACKGROUND_COLOR))  # Заливаем поверхность сплошным цветом

    left = right = False  # по умолчанию - стоим
    up = False
    flying = False

    hero = Player(playerX, playerY)  # создаем героя по (x,y) координатам
    entities.add(hero)

    timer = pygame.time.Clock()
    x = y = 0  # координаты
    for row in level:  # вся строка
        for col in row:  # каждый символ
            if col == "-":
                pf = Platform(x, y)
                entities.add(pf)
                platforms.append(pf)
            if col == "*":
                bd = BlockDie(x, y)
                entities.add(bd)
                platforms.append(bd)
            if col == "P":
                pr = Door(x, y)
                entities.add(pr)
                platforms.append(pr)
                animatedEntities.add(pr)

            x += PLATFORM_WIDTH  # блоки платформы ставятся на ширине блоков
        y += PLATFORM_HEIGHT  # то же самое и с высотой
        x = 0  # на каждой новой строчке начинаем с нуля

    total_level_width = len(level[0]) * PLATFORM_WIDTH  # Высчитываем фактическую ширину уровня
    total_level_height = len(level) * PLATFORM_HEIGHT  # высоту

    camera = Camera(camera_configure, total_level_width, total_level_height)

    while not hero.winner:  # Основной цикл программы
        timer.tick(60)
        for e in pygame.event.get():  # Обрабатываем события
            if e.type == QUIT:
                pygame.quit()
                quit()
            if e.type == KEYDOWN and e.key == K_o:
                vol -= 0.1
                pygame.mixer.music.set_volume(vol)
            if e.type == KEYDOWN and e.key == K_p:
                vol += 0.1
                pygame.mixer.music.set_volume(vol)
            if e.type == KEYDOWN and e.key == K_UP:
                up = True
            if e.type == KEYDOWN and e.key == K_LEFT:
                left = True
            if e.type == KEYDOWN and e.key == K_RIGHT:
                right = True
            if e.type == KEYDOWN and e.key == K_LSHIFT:
                flying = True

            if e.type == KEYUP and e.key == K_UP:
                up = False
            if e.type == KEYUP and e.key == K_RIGHT:
                right = False
            if e.type == KEYUP and e.key == K_LEFT:
                left = False
            if e.type == KEYUP and e.key == K_LSHIFT:
                flying = False

        screen.blit(bg, (0, 0))  # Каждую итерацию необходимо всё перерисовывать

        animatedEntities.update()  # показываеaм анимацию
        monsters.update(platforms)  # передвигаем всех монстров
        camera.update(hero)  # центризируем камеру относительно персонажа
        hero.update(left, right, up, flying, platforms)  # передвижение
        for e in entities:
            screen.blit(e.image, camera.apply(e))
        pygame.display.update()  # обновление и вывод всех изменений на экран
    pygame.mixer.music.stop()
    gameover_screen()


level = []
entities = pygame.sprite.Group()  # Все объекты
animatedEntities = pygame.sprite.Group()  # все анимированные объекты, за исключением героя
monsters = pygame.sprite.Group()  # Все передвигающиеся объекты
platforms = []  # то, во что мы будем врезаться или опираться
if __name__ == "__main__":
    start_screen()
