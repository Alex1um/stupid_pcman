import random
import pickle


def gen_lab_1(width, height):
    width += 1 if not width % 2 else 0
    height += 1 if not height % 2 else 0
    area = [1] * height
    zeros = []
    for i in range(len(area)):
        area[i] = [1] * width
    for i in range(1, len(area) - 1):
        for j in range(1, len(area[0]) - 1):
            if j % 2 and i % 2:
                area[i][j] = 0
                zeros.append((j, i))

    ghosts = set()
    base = random.choice(zeros)
    zeros.remove(base)
    ghosts.add(base)
    area[base[1]][base[0]] = 2
    kx = -1 if base[0] > width // 2 else 1
    zeros.remove((base[0] + 2 * kx, base[1]))
    ghosts.add((base[0] + 2 * kx, base[1]))
    area[base[1]][base[0] + kx] = 2
    area[base[1]][base[0] + 2 * kx] = 2
    ky = -1 if base[1] > height // 2 else 1
    # zeros.remove((base[0], base[1] + 2 * ky))
    area[base[1] + ky][base[0]] = 2

    # now = random.choice(zeros)
    now = (base[0], base[1] + 2 * ky)
    was = [now]
    zeros.remove(now)
    stack = []
    while zeros:
        neigh = tuple((x, y) for x, y in ((now[0] + 2, now[1]), (now[0] - 2, now[1]), (now[0], now[1] + 2), (now[0], now[1] - 2)) if 0 < x < width - 1 and 0 < y < height - 1)
        new_neigh = tuple(i for i in neigh if i in zeros or random.random() > 0.9 and i not in ghosts)
        if new_neigh:
            stack.append(now)
            new = random.choice(new_neigh)
            if new in zeros:
                zeros.remove(new)

            if now[0] != new[0]:
                x, y = now[0] + int((now[0] - new[0]) * -0.5), now[1]
                area[y][x] = 0
            elif now[1] != new[1]:
                y, x = now[1] + int((now[1] - new[1]) * -0.5), now[0]
                area[y][x] = 0

            now = new

        elif stack:
            now = stack.pop()
        else:
            now = random.choice(zeros)
            if now in zeros:
                zeros.remove(now)

    return area


def printf(matrix):
    print(*matrix, sep='\n')


# printf(gen_lab_1(10, 10))
with open('.\\labs\\test2.lab', 'wb') as f:
    pickle.dump(gen_lab_1(50, 50), f)