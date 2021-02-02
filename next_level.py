import os
import random
import sys

import pygame
import pygame_gui
import pyglet

window_size = (640, 480)

pygame.init()
size = width, height = window_size[0], window_size[1]
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
boxes_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
fireballs_group = pygame.sprite.Group()
trap_group = pygame.sprite.Group()

idle = [load_image('idle1.png'), load_image('idle2.png'),
        load_image('idle3.png')]
runr = [load_image('runr1.png'), load_image('runr2.png'),
        load_image('runr3.png'), load_image('runr4.png'),
        load_image('runr5.png'), load_image('runr6.png')]
runl = [load_image('runl1.png'), load_image('runl2.png'),
        load_image('runl3.png'), load_image('runl4.png'),
        load_image('runl5.png'), load_image('runl6.png')]
attack_r = [load_image('attackr4.png'),
            load_image('attackr5.png'), load_image('attackr6.png')]
attack_l = [load_image('attackl4.png'),
            load_image('attackl5.png'), load_image('attackl6.png')]

enemies_images = {'slime': load_image('slime_idle1.png')}

slime_idle = [load_image('slime_idle1.png'), load_image('slime_idle2.png'),
              load_image('slime_idle3.png'), load_image('slime_idle4.png'),
              load_image('slime_idle5.png'), load_image('slime_idle6.png')]

dm_enemies = {'slime': load_image('dm_slime.png')}

tile_images = {
    'wall_v': load_image('wall_v.png'),
    'wall_h': load_image('wall.png'),
    'empty': load_image('floor.png'),
    'box': load_image('box.png'),
    'finish': load_image('finish.png'),
    'trap': load_image('spikes_0.png')
}
player_image = load_image('idle1.png')

trap_sprites = [load_image('spikes_0.png'), load_image('spikes_1.png'),
                load_image('spikes_2.png'),
                load_image('spikes_3.png'),
                load_image('spikes_4.png'), load_image('spikes_5.png'),
                load_image('spikes_6.png'),
                load_image('spikes_7.png'), load_image('spikes_8.png'),
                load_image('spikes_9.png')]

tile_width = tile_height = 50

player = None


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Journey of strange man",
                  "Версия 0.5",
                  "Правила игры",
                  "Кничтожте всех монстроов и дойдите до конца уровня",
                  "Для начала нажмите кнопку"]

    fon = pygame.transform.scale(load_image('fon.jpg'), window_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, (150, 0, 0))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, wall_type):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[wall_type]
        self.true_x = pos_x * tile_width
        self.true_y = pos_y * tile_height
        self.tile_type = tile_type
        self.w = 50
        self.h = 50
        if wall_type == 'wall_v':
            self.w = 14
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Trap(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(trap_group, all_sprites)
        self.image = pygame.transform.scale(tile_images[tile_type], (50, 50))
        self.true_x = pos_x * tile_width
        self.true_y = pos_y * tile_height
        self.tile_type = tile_type
        self.w = 50
        self.h = 50
        self.texture = 0
        self.text = 1
        self.delay = 0
        self.dm_give = False
        self.pl_stay = False
        self.dmg = 2
        active = False
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def next_texture(self):
        if self.delay == 9:
            self.image = pygame.transform.scale(trap_sprites[self.texture],
                                                (50, 50))
            self.texture += self.text
            if self.texture == 6:
                sound = pyglet.media.load('data\sounds\lv.mp3',
                                          streaming=False)
                sound.play()
            if self.texture == 10:
                self.texture = 9
                self.text = -1
            if self.texture == 0:
                self.text = 1
                self.delay = 0
        else:
            self.delay += 1
        if self.player_stay_check():
            self.pl_stay = True
        else:
            self.pl_stay = False
        if not self.pl_stay or self.texture < 6:
            self.dm_give = False
        if self.pl_stay and self.texture >= 6 and not self.dm_give:
            player.hp -= self.dmg
            self.dm_give = True
        print(self.pl_stay)

    def player_stay_check(self):
        player_pos_x = player.true_x
        player_pos_y = player.true_y
        if player_pos_x >= self.true_x - 25 and player_pos_x + player.w <= self.true_x + 50:
            if player_pos_y >= self.true_y - 25 and player_pos_y + player.h <= self.true_y + 50:
                return True
            else:
                return False
        else:
            return False


class Box(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(boxes_group, all_sprites)
        self.image = tile_images[tile_type]
        self.true_x = pos_x * 50
        self.true_y = pos_y * 50
        self.w = 25
        self.h = 25
        self.broken = False
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(50 * pos_x, tile_height * pos_y)

    def destroy(self):
        self.image = load_image('br_box.png')
        self.broken = True


class Slime(pygame.sprite.Sprite):
    def __init__(self, enemy_type, pos_x, pos_y):
        super().__init__(enemies_group, all_sprites)
        self.image = enemies_images[enemy_type]
        self.true_x = pos_x * 50
        self.true_y = pos_y * 50
        self.tile_type = None
        self.dmg_delay = 0
        self.enemy_type = enemy_type
        self.rect = self.image.get_rect().move(50 * pos_x, 50 * pos_y)
        self.texture = 0
        self.point_to_move = [0, 0]
        self.target = False
        self.hp = 2
        self.dm = 3
        self.w = 16
        self.h = 15
        self.w_dm = False

    def next_texture(self):
        if not self.w_dm:
            self.image = slime_idle[self.texture]
            self.texture += 1
            self.texture %= 6
        else:
            self.image = dm_enemies[self.enemy_type]
            self.w_dm = False

    def move(self):
        move_x = 0
        move_y = 0
        if self.point_to_move[0] != 0:
            if self.point_to_move[0] > 0:
                self.rect.x += 3
                move_x = 3
                self.true_x += 3
                self.point_to_move[0] = self.point_to_move[0] - 1
            else:
                self.rect.x -= 3
                move_x = -3
                self.true_x -= 3
                self.point_to_move[0] = self.point_to_move[0] + 1
        if self.point_to_move[1] != 0:
            if self.point_to_move[1] > 0:
                self.rect.y += 3
                move_y = 3
                self.true_y += 3
                self.point_to_move[1] = self.point_to_move[1] - 1
            else:
                self.rect.y -= 3
                move_y = -3
                self.true_y -= 3
                self.point_to_move[1] = self.point_to_move[1] + 1
        self.check_target()
        self.check_dm()
        x1 = self.true_x
        y1 = self.true_y
        for elem in all_sprites:
            if elem.tile_type == 'wall' or (
                    elem.tile_type == 'box' and not elem.broken):
                x2 = elem.true_x - 15
                y2 = elem.true_y - 7
                if (x2 < x1 < x2 + elem.w) or (x2 < x1 + 13 < x2 + elem.w):
                    if (y2 < y1 <= y2 + elem.h) or (y2 < y1 + 13 < y2 + elem.h):
                        self.point_to_move = [random.randint(-25, 25),
                                              random.randint(-25, 25)]
                        self.rect.x -= move_x
                        self.rect.y -= move_y
                        self.true_x -= move_x
                        self.true_y -= move_y
        if self.point_to_move[0] == 0 and self.point_to_move[1] == 0:
            self.point_to_move = [random.randint(-25, 25),
                                  random.randint(-25, 25)]

    def check_hp(self):
        if self.hp <= 0:
            self.kill()

    def check_target(self):
        px = player.true_x + player.w / 2
        py = player.true_y + player.h / 2
        if abs(self.true_x - px) <= 150 and abs(
                self.true_y - py) <= 150:
            self.target = True
            self.point_to_move[0] = px - self.true_x
            self.point_to_move[1] = py - self.true_y

    def check_dm(self):
        px = player.true_x + player.w / 2
        py = player.true_y + player.h / 2
        if self.dmg_delay == 5:
            if abs(self.true_x - px) <= 10 and abs(
                    self.true_y - py) <= 10:
                player.hp -= self.dm
                print(player.hp)
            self.dmg_delay = 0
        self.dmg_delay += 1


class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, true_x, true_y, nap):
        super().__init__(fireballs_group, all_sprites)
        self.true_x = true_x
        self.true_y = true_y
        self.frames = []
        self.nap = nap
        self.cut_sheet(load_image('fireballls.png'), 10, 1)
        self.texture = 0
        self.w = 10
        self.h = 25
        self.rot = 0
        self.rot = 0
        if nap[0] == 5:
            self.image = pygame.transform.rotate(self.frames[self.texture], 270)
            self.rot = 270
        elif nap[0] == -5:
            self.image = pygame.transform.rotate(self.frames[self.texture], 90)
            self.rot = 90
        elif nap[1] == 5:
            self.image = pygame.transform.rotate(self.frames[self.texture], 180)
            self.rot = 180
        else:
            self.image = self.frames[0]
        self.tile_type = 'fb'
        self.vr = False
        self.rect = self.image.get_rect().move(
            x, y)

    def next_texture(self):
        if not self.vr:
            self.image = pygame.transform.rotate(self.frames[self.texture],
                                                 self.rot)
            self.texture += 1
            self.texture %= len(self.frames)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def move(self):
        self.rect.x -= self.nap[0]
        self.rect.y -= self.nap[1]
        self.true_x -= self.nap[0]
        self.true_y -= self.nap[1]
        x1 = self.true_x
        y1 = self.true_y
        for elem in all_sprites:
            if elem.tile_type != 'empty' and elem.tile_type != 'pl':
                x2 = elem.true_x
                y2 = elem.true_y
                if (x2 < x1 < x2 + elem.w) or (
                        x2 < x1 + self.w < x2 + elem.w):
                    if (y2 < y1 <= y2 + elem.h) or (
                            y2 < y1 + self.h < y2 + elem.h):
                        if elem.tile_type == None:
                            elem.kill()
                        elif elem.tile_type == 'box':
                            elem.destroy()
                        if elem.tile_type == 'box':
                            if not elem.broken:
                                self.kill()
                        else:
                            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.true_x = pos_x * 50 + 10
        self.true_y = pos_y * 50 + 10
        self.image = player_image
        self.w = 25
        self.h = 33
        self.tile_type = 'pl'
        self.dm = 1
        self.attack_x = 0
        self.attack_y = 0
        self.fireballs_ost = 5
        self.nap = 'r'
        self.hp = 20
        self.status = 'stay'
        self.attack_end = False
        self.sound_delay = 0
        self.texture = 0
        self.rect = self.image.get_rect().move(
            50 * pos_x + 10, 50 * pos_y + 10)

    def update(self, px, py):
        if px != 0 or py != 0:
            moving = True
        else:
            moving = False
        if self.status != 'attack' or (
                self.attack_end and self.status == 'attack'):
            if px != 0 or py != 0:
                self.status = 'move'
                if px > 0:
                    self.nap = 'r'
                elif px < 0:
                    self.nap = 'l'
            else:
                self.status = 'stay'
            self.rect.x += px
            self.rect.y += py
            self.true_y += py
            self.true_x += px
            move_y = py
            move_x = px
            x1 = self.true_x
            y1 = self.true_y
            for elem in all_sprites:
                if elem.tile_type == 'wall' or (
                        elem.tile_type == 'box' and not elem.broken):
                    x2 = elem.true_x - 15
                    y2 = elem.true_y - 7
                    if (x2 < x1 < x2 + elem.w) or (
                            x2 < x1 + self.w < x2 + elem.w):
                        if (y2 < y1 <= y2 + elem.h) or (
                                y2 < y1 + self.h < y2 + elem.h):
                            self.true_y -= move_y
                            self.true_x -= move_x
                            self.rect.x -= move_x
                            self.rect.y -= move_y
                            px = 0
                            py = 0
            if self.sound_delay == 20 and moving:
                sound = pyglet.media.load('data\sounds\eg.mp3',
                                          streaming=False)
                sound.play()
                self.sound_delay = 0
            elif moving:
                self.sound_delay += 1

    def next_texture(self):
        if self.status == 'stay':
            self.texture %= 3
            self.image = idle[self.texture]
            self.texture += 1
            self.texture %= 3
        elif self.status == 'move':
            if self.nap == 'r':
                self.image = runr[self.texture]
            elif self.nap == 'l':
                self.image = runl[self.texture]
            self.texture += 1
            self.texture %= 6
        elif self.status == 'attack':
            self.texture %= 3
            if self.nap == 'r':
                self.image = attack_r[self.texture]
            else:
                self.image = attack_l[self.texture]
            self.texture += 1
            self.texture %= 3
            if self.texture == 0:
                self.attack_end = True

    def finish_check(self):
        for elem in tiles_group:
            if elem.tile_type == 'finish':
                x2 = elem.true_x - 17
                y2 = elem.true_y - 7
                x1 = self.true_x
                y1 = self.true_y
                if (x2 < x1 < x2 + elem.w) or (
                        x2 < x1 + self.w < x2 + elem.w):
                    if (y2 < y1 <= y2 + elem.h) or (
                            y2 < y1 + self.h < y2 + elem.h):
                        return True


def death_screen(screen):
    screen.fill((0, 0, 0))
    all_sprites = pygame.sprite.Group()
    pygame.display.flip()
    sprite = pygame.sprite.Sprite(all_sprites)
    sprite.image = load_image("gameover.jpg")
    sprite.rect = sprite.image.get_rect()
    sprite.rect = (0, 1000)
    all_sprites.add(sprite)
    fps = 20
    clock = pygame.time.Clock()
    running = True
    r = True
    while running:
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        if sprite.rect[1] != 0:
            sprite.rect = (0, sprite.rect[1] - 20)
        if sprite.rect[1] == 0:
            break
        pygame.display.flip()
        clock.tick(fps)
    main_menu(screen)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y, 'empty')
            elif level[y][x] == '-':
                Tile('empty', x, y, 'empty')
                Tile('wall', x, y, 'wall_h')
            elif level[y][x] == '|':
                Tile('empty', x, y, 'empty')
                Tile('wall', x, y, 'wall_v')
            elif level[y][x] == 'T':
                Trap('trap', x, y)
            elif level[y][x] == 'b':
                Tile('empty', x, y, 'empty')
                Box('box', x, y)
                Box('box', x + 0.5, y)
                Box('box', x, y + 0.5)
                Box('box', x + 0.5, y + 0.5)
            elif level[y][x] == 's':
                Tile('empty', x, y, 'empty')
                Slime('slime', x, y)
            elif level[y][x] == 'f':
                Tile('empty', x, y, 'empty')
                Tile('finish', x, y, 'finish')
            elif level[y][x] == '@':
                Tile('empty', x, y, 'empty')
                new_player = Player(x, y)
    return new_player, x, y


def draw_hp(screen):
    font = pygame.font.Font(None, 50)
    text1 = font.render('hp: ' + str(player.hp), True, (100, 0, 0))
    text2 = font.render('Мана: ' + str(player.fireballs_ost), True, (0, 0, 100))
    screen.blit(text1, (0, 0))
    screen.blit(text2, (150, 0))


start_screen()


def main_menu(screen):
    global window_size
    screen.fill((100, 100, 100))
    manager = pygame_gui.UIManager(window_size)
    clock = pygame.time.Clock()

    start_game_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(
            (window_size[0] // 19, window_size[1] // 3.63),
            (window_size[0] // 4.75, window_size[1] // 10)),
        text='Start game',
        manager=manager
    )
    leave_game_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(
            (window_size[0] // 19, window_size[1] // 3.63 + 125),
            (window_size[0] // 4.75, window_size[1] // 10)),
        text='Leave game',
        manager=manager
    )
    fon = pygame.transform.scale(load_image('menu_fon.jpg'), window_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == start_game_btn:
                        running = False
                        break
                    elif event.ui_element == leave_game_btn:
                        exit(0)
            manager.process_events(event)
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()


main_menu(screen)

# sound = pyglet.media.load('data\music.mp3', streaming=True)
# sound.play()

maps = ['map.txt', 'map2.txt']
level = 1
game_end = False

while not game_end:
    player, level_x, level_y = generate_level(load_level(maps[level - 1]))

    running = True
    camera = Camera()
    moving = False
    tick_move = 0
    px = 0
    br_box = load_image('br_box.png')
    py = 0
    mana_reload = 0
    win = False
    exit_g = False
    fps = 60
    tick_texture = 0
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                py = -2
                player.attack_y = -40
                player.attack_x = 0

            elif event.type == pygame.KEYUP and event.key == pygame.K_w:
                py = 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                py = 2
                player.attack_y = 40
                player.attack_x = 0
            elif event.type == pygame.KEYUP and event.key == pygame.K_s:
                py = 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                px = 2
                player.attack_x = 40
                player.attack_y = 0
            elif event.type == pygame.KEYUP and event.key == pygame.K_d:
                px = 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                px = -2
                player.attack_x = -40
                player.attack_y = 0
            elif event.type == pygame.KEYUP and event.key == pygame.K_a:
                px = 0
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                sound = pyglet.media.load('data\sounds\sword.mp3',
                                          streaming=False)
                sound.play()
                player.status = 'attack'
                player.attack_end = False
                player.texture = 0
                x1 = player.true_x
                y1 = player.true_y
                if player.attack_x > 0:
                    w = player.w + player.attack_x
                    x1 = player.true_x
                else:
                    x1 = player.true_x - abs(player.attack_x)
                    w = player.w + abs(player.attack_x)
                if player.attack_y > 0:
                    h = player.h + player.attack_y
                    y1 = player.true_y
                else:
                    h = player.h + abs(player.attack_y)
                    y1 = player.true_y - abs(player.attack_y)
                print(player.attack_y)
                for box in boxes_group:
                    x2 = box.true_x
                    y2 = box.true_y
                    if (x2 <= x1 <= x2 + 25) or (x2 <= x1 + w <= x2 + 25):
                        if (y2 <= y1 <= y2 + 25) or (y2 <= y1 + h <= y2 + 25):
                            box.destroy()
                    if (x1 <= x2 <= x1 + player.w) or (
                            x1 <= x2 + box.w <= x1 + player.w):
                        if (y1 <= y2 <= y1 + player.h) or (
                                y1 <= y2 + box.h <= y1 + player.h):
                            box.destroy()
                            sound = pyglet.media.load('data\sounds\polomka.mp3',
                                                      streaming=False)
                            sound.play()
                for enemy in enemies_group:
                    x2 = enemy.true_x
                    y2 = enemy.true_y
                    if (x2 <= x1 <= x2 + 20) or (x2 <= x1 + w <= x2 + 20):
                        if (y2 <= y1 <= y2 + 20) or (y2 <= y1 + h <= y2 + 20):
                            enemy.hp -= player.dm
                            enemy.image = dm_enemies[enemy.enemy_type]
                            enemy.check_hp()
                            enemy.w_dm = True
                            sound = pyglet.media.load('data\sounds\slime.mp3',
                                                      streaming=False)
                            sound.play()
                    if (x1 <= x2 <= x1 + player.w) or (
                            x1 <= x2 + enemy.w <= x1 + player.w):
                        if (y1 <= y2 <= y1 + player.h) or (
                                y1 <= y2 + enemy.h <= y1 + player.h):
                            enemy.hp -= player.dm
                            enemy.image = dm_enemies[enemy.enemy_type]
                            enemy.check_hp()
                            enemy.w_dm = True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if player.fireballs_ost > 0:
                    sound = pyglet.media.load('data\sounds\magic.mp3',
                                              streaming=False)
                    sound.play()
                if player.attack_x > 0:
                    nap_x = -5
                elif player.attack_x < 0:
                    nap_x = 5
                else:
                    nap_x = 0
                if player.attack_y < 0:
                    nap_y = 5
                elif player.attack_y > 0:
                    nap_y = -5
                else:
                    nap_y = 0
                if player.fireballs_ost != 0:
                    Fireball(player.rect.x + player.w / 2,
                             player.rect.y + player.h / 2,
                             player.true_x + player.w / 2,
                             player.true_y + player.h / 2, (nap_x, nap_y))
                    player.fireballs_ost -= 1
        player.update(px, py)

        for fireball in fireballs_group:
            fireball.move()
        if tick_texture == 4:
            player.next_texture()
            for enemy in enemies_group:
                enemy.next_texture()
                enemy.move()
            for fireball in fireballs_group:
                fireball.next_texture()
            for elem in trap_group:
                elem.next_texture()
            tick_texture = 0
        if mana_reload == 500:
            if player.fireballs_ost < 5:
                player.fireballs_ost += 1
            mana_reload = 0
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        screen.fill((100, 100, 100))
        tiles_group.draw(screen)
        boxes_group.draw(screen)
        trap_group.draw(screen)
        enemies_group.draw(screen)
        player_group.draw(screen)
        fireballs_group.draw(screen)
        draw_hp(screen)
        pygame.display.flip()
        mana_reload += 1
        tick_texture += 0.5
        clock.tick(fps)
        if player.finish_check():
            win = True
            break
        if player.hp <= 0:
            win = False
            break


    def level_end_screen():
        if win:
            intro_text = ["Поздравляю!",
                          "Вы прошли уровень :)",
                          "Удачи в дальнейшем прохождении.",
                          "Она вам понадобитца..."]
        elif exit_g:
            intro_text = ["Зачем закрывать игру не доиграв :("]
        else:
            intro_text = ["Ничего страшного",
                          "Получится в другой раз"]
        fon = pygame.transform.scale(load_image('fon.jpg'), window_size)
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, True, (150, 0, 0))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return
            pygame.display.flip()


    for spr in all_sprites:
        spr.kill()
    if win:
        level += 1
        if level > len(maps):
            break
        level_end_screen()
    else:
        sound = pyglet.media.load('data\sounds\death.mp3', streaming=False)
        sound.play()
        death_screen(screen)
        level = 1


def finish_screen():
    intro_text = ["Поздравляю!",
                  "Вы нашли выход из подземелья",
                  "Теперь вы можете поменять карты под себя и пройти их",
                  "До скорых встреч в загадочных подземельях"]

    fon = pygame.transform.scale(load_image('finish.jpg'), window_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, (150, 0, 0))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


finish_screen()
