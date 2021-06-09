from engine import *
import math
import time
import random


class Pacmen(GameArea):

    class Block(Object):

        def __init__(self, resolution, x_rel, y_rel, w, h):
            super().__init__(resolution, x_rel, y_rel, w, h)
            self.set_color((255, 0, 0))

        def update(self, rs):
            pass

    class Ghost(Object):

        def __init__(self, rs, x_rel, y_rel, w, h, x, y, cls, brain):
            super().__init__(rs, x_rel, y_rel, w, h)
            self.set_color((0, 255, 0))
            self.spawn_pos = (x, y)
            self.pos = (x, y)
            self.cls = cls
            self.brain, img = brain
            self.speed = w
            self.tick = 0
            self.set_image("data\\" + img + ".png", size_mode="%obj")

        def update(self, res):
            if self.tick == 10:
                self.pos = self.brain(self)[1]
                self.x_rel = self.pos[0] * self.speed
                self.y_rel = self.pos[1] * self.speed
                self.adopt(res)
                self.tick = 0
            self.tick += 1

    class Stat(Object):

        def __init__(self, res):
            super().__init__(res, 0, 0, 10, 2)
            self.set_text('0', align='left')
            self.font_scale = 100

        def update(self, rs):
            self.adopt(rs)

    class Food(Object):

        def __init__(self, res, x_rel, y_rel, w, h, x, y, cls):
            super().__init__(res, x_rel, y_rel, w, h)
            self.set_image('data\\food.png', size_mode='%obj')
            self.pos = (x, y)
            self.cls = cls

        def update(self, rs):
            if self.cls.area[self.pos[1]][self.pos[0]] == 2:
                self.cls.play_sound('pc1')
                self.cls.stat.text = str(int(self.cls.stat.text) + 100)
                self.cls.objects.remove(self)
                del self

    class MegaFood(Food):

        def __init__(self, res, x_rel, y_rel, w, h, x, y, cls):
            super().__init__(res, x_rel, y_rel, w, h, x, y, cls)
            self.set_image('data\\megafood.png', size_mode="%obj")
            self.image_index = 1
            self.adopt(res)

        def update(self, rs):
            if self.cls.area[self.pos[1]][self.pos[0]] == 2:
                self.cls.play_sound('pc1')
                self.cls.stat.text = str(int(self.cls.stat.text) + 100)
                self.cls.objects.remove(self)
                del self

    class Pacmen(RadialObject):

        def __init__(self, cls, resolution, x_rel, y_rel, x, y, r_rel):
            super().__init__(resolution, x_rel, y_rel, r_rel)
            self.set_color((255, 255, 0))
            self.set_image(['data\\pcmen1.png', 'data\\pcmen2.png', 'data\\pcmen3.png', 'data\\pcmen2.png'], size_mode='%obj')
            self.move = (0, 0)
            self.image_index = 2
            self.animation_delay_frames = 2
            self.speed = r_rel
            self.cls = cls
            self.pos = [x, y]
            self.prev_cords = (self.x, self.y)
            self.fut_cords = None
            self.frame = 0

        def border_check(self, k1=None, k2=None):
            return self.cls.area[self.pos[1] + (self.move[1] if k2 is None else k2)][self.pos[0] + (self.move[0] if k1 is None else k1)] == 1

        def on_key_down(self, key):
            self.prev_move = self.move
            if key == 'right':
                self.move = (1, 0)
            elif key == 'left':
                self.move = (-1, 0)
            elif key == 'up':
                self.move = (0, -1)
            elif key == 'down':
                self.move = (0, 1)
            self.image_animated = 1
            self.fut_cords = self.move
            if self.border_check():
                self.move = self.prev_move

        def update(self, resolution):
            if self.frame // 10:
                self.frame = 0
                self.prev_cords = (self.x, self.y)
                if self.border_check():
                    self.move = (0, 0)
                    self.image_animated = 0
                    self.image_index = 0
                    self.fut_cords = None
                if self.fut_cords and not self.border_check(*self.fut_cords):
                    self.move = self.fut_cords
                    self.fut_cords = None
                if self.move[0] or self.move[1]:
                    self.image_rotation = 180 * (0 if self.move[0] == 1 else 1) + 90 * self.move[1]
                self.pos[0] += self.move[0]
                self.pos[1] += self.move[1]
                self.x_rel += self.speed * self.move[0]
                self.y_rel += self.speed * self.move[1]
                self.cls.area[self.pos[1]][self.pos[0]] = 2
                self.adopt(resolution)

            self.frame += 1

    def find_near(self, pos):
        if pos[0] < 0 or pos[1] < 0 or pos[0] > len(self.area[0]) - 1 or pos[1] > len(self.area) - 1 or self.area[pos[1]][pos[0]] == 1:
            kx = -1 if pos[0] > len(self.area[0]) // 2 else 1
            ky = -1 if pos[1] > len(self.area) // 2 else 1
            while 1:
                if pos[0] < 0 or pos[1] < 0 or pos[0] > len(self.area[0]) - 1 or pos[1] > len(self.area) - 1 or self.area[pos[1]][pos[0]] == 1:
                    pos[0] += kx
                else:
                    return pos
                if pos[0] < 0 or pos[1] < 0 or pos[0] > len(self.area[0]) - 1 or pos[1] > len(self.area) - 1 or self.area[pos[1]][pos[0]] == 1:
                    pos[1] += ky
                else:
                    return pos
        return pos

    def find_way2(self, stpos: Tuple[int, int], fpos: Tuple[int, int]) -> Tuple:
        sy, sx = len(self.area), len(self.area[0])
        num_map = [0] * sy
        for i in range(len(num_map)):
            num_map[i] = [-1] * sx
        nums = [stpos]
        num_map[stpos[1]][stpos[0]] = 0
        d = 0
        while nums:
            new_nums = []
            d += 1
            for x, y in nums:
                for x1, y1 in (
                        (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if sx > x1 > -1 and sy > y1 > -1 and num_map[y1][
                        x1] == -1 and self.area[y1][x1]  != 1:
                        num_map[y1][x1] = d
                        new_nums.append((x1, y1))
            nums = new_nums
        way = [fpos]
        for i in range(num_map[fpos[1]][fpos[0]] - 1, -1, -1):
            x, y = way[-1]
            for x1, y1 in (
                    (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if sx > x1 > -1 and sy > y1 > -1 and num_map[y1][x1] == i:
                    way.append((x1, y1))
                    break
        if len(way) == 1:
            way = []
        return way[::-1]

    def xmode(self):
        self.mode = True
        time.sleep(30)
        self.mode = False


    def brains(self):

        def br1(gh):
            return self.find_way2(gh.pos, self.pcmen.pos)

        def br2(gh, ll=4):
            cords = self.find_near([self.pcmen.pos[0] + ll * self.pcmen.move[0], self.pcmen.pos[1] + ll * self.pcmen.move[1]])
            return self.find_way2(gh.pos, cords)

        def br3(gh):
            x, y = self.ghosts[0].pos
            xs, ys = gh.pos
            kx = 1 if (x - xs) > 0 else -1
            a, b, c = (ys - y), (x - xs) if x != xs else 1, (xs * y - ys * x)
            yf = lambda n: (-c - x * a) / b
            cords = self.find_near([x + kx * 2, round(yf(x + kx * 2))])

            way = self.find_way2(gh.pos, cords)
            return way

        def br4(gh):
            x, y = gh.pos
            x1, y1 = self.pcmen.pos
            if abs(x - x1) < 8 and abs(y - y1) < 8:
                return br3(gh)
            else:
                return br2(gh)

        yield br1, "ghost1"
        yield br3, "ghost2"
        yield br2, "ghost3"
        yield br4, "ghost4"

    def __init__(self, main, sizes, lab):
        self.stat = self.Stat(main.resolution)
        super().__init__()
        self._current_chomp = False
        self.set_sounds('.\\sounds\\pc1.wav')
        self.set_background_music('.\\sounds\\pb.wav')
        self.play_background_music(1)
        self.main = main
        k = 100 / sizes[0]
        self.area = [0] * sizes[1]
        brains = self.brains()
        self.ghosts = []
        pcman_pos = ()
        for y in range(sizes[1]):
            self.area[y] = [0] * sizes[0]
            for x in range(sizes[0]):
                if lab[y][x] == 1:
                    self.add_objects(self.Block(main.resolution, x * k, y * k, k, k))
                    self.area[y][x] = 1
                elif lab[y][x] == 2:
                    self.ghosts.append(self.Ghost(main.resolution,
                                                   x * k,
                                                   y * k,
                                                   k,
                                                   k,
                                                   x,
                                                   y,
                                                   self,
                                                   next(brains)))
                    self.area[y][x] = 6
                elif not pcman_pos:
                    pcman_pos = (x, y)
                    self.pcmen = self.Pacmen(self, main.resolution, pcman_pos[0] * k, pcman_pos[1] * k, *pcman_pos, k)
                    self.area[y][x] = 2
                else:
                    if random.random() > 0.1:
                        self.add_objects(self.Food(main.resolution, x * k, y * k, k, k, x, y, self))
                        self.area[y][x] = 3
                    else:
                        self.add_objects(self.MegaFood(main.resolution, x * k, y * k, k, k, x, y, self))
                        self.area[y][x] = 4
        # print(self.find_way2((sizes[1] - 2, sizes[0] - 2), (1, 1)))
        self.add_objects(self.pcmen)
        self.add_objects(*self.ghosts)
        self.add_objects(self.stat)

    def update(self, main):
        for obj in self.objects:
            obj.update(main.resolution)
        # self.objects[-1].update(main.resolution)

