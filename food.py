import random


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.type = "apple"

    def place(self, snake_body, rock_positions, palm_positions, rows, cols):
        self.type = random.choice(["apple", "banana"])
        while True:
            r = random.randint(0, rows - 1)
            c = random.randint(0, cols - 1)
            pos = (r, c)

            if pos not in [s["pos"] for s in snake_body] and \
                    pos not in rock_positions and \
                    pos not in palm_positions:
                self.position = pos
                break


class Rocks:
    def __init__(self, count):
        self.positions = []
        self.count = count

    def place(self, snake_body, rows, cols):
        self.positions = []
        attempts = 0
        while len(self.positions) < self.count and attempts < 1000:
            attempts += 1
            r = random.randint(0, rows - 1)
            c = random.randint(0, cols - 1)

            head_safe_zone = [
                (snake_body[0]["pos"][0] + i, snake_body[0]["pos"][1] + j)
                for i in range(-3, 4) for j in range(-3, 4)
            ]

            pos = (r, c)
            if pos not in [s["pos"] for s in snake_body] and \
                    pos not in self.positions and \
                    pos not in head_safe_zone:
                self.positions.append(pos)


class Palms:
    def __init__(self, count):
        self.positions = []
        self.count = count

    def place(self, snake_body, rock_positions, rows, cols):
        self.positions = []
        attempts = 0
        while len(self.positions) < self.count and attempts < 1000:
            attempts += 1
            r = random.randint(0, rows - 1)
            c = random.randint(0, cols - 1)

            head_safe_zone = [
                (snake_body[0]["pos"][0] + i, snake_body[0]["pos"][1] + j)
                for i in range(-3, 4) for j in range(-3, 4)
            ]

            pos = (r, c)
            if pos not in [s["pos"] for s in snake_body] and \
                    pos not in rock_positions and \
                    pos not in self.positions and \
                    pos not in head_safe_zone:
                self.positions.append(pos)
