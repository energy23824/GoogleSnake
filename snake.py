import random

import pygame
from settings import *
from food import Food, Rocks, Palms


class Snake:
    def __init__(self, difficulty_settings, sound_enabled=True):
        self.high_score = 0
        self.sound_enabled = sound_enabled

        self.cell_size = difficulty_settings["cell"]
        self.rock_count = difficulty_settings["rocks"]
        self.palm_count = difficulty_settings["palms"]

        self.rows = WINDOW_H // self.cell_size
        self.cols = WINDOW_W // self.cell_size

        self.snd_eat = pygame.mixer.Sound("assets/sounds/apple_eat.wav")
        self.snd_lose = pygame.mixer.Sound("assets/sounds/lose.wav")
        self.snd_eat.set_volume(0.5)
        self.snd_lose.set_volume(0.5)

        self.img_head = pygame.image.load("assets/images/head.png").convert_alpha()
        self.img_body = pygame.image.load("assets/images/body.png").convert_alpha()
        self.img_tail = pygame.image.load("assets/images/tail.png").convert_alpha()
        self.img_apple = pygame.image.load("assets/images/apple.png").convert_alpha()
        self.img_banana = pygame.image.load("assets/images/banana.png").convert_alpha()
        self.img_rock = pygame.image.load("assets/images/rock.png").convert_alpha()
        self.img_palma = pygame.image.load("assets/images/palma.png").convert_alpha()

        self.turn_images = {
            "turn_ul": pygame.image.load("assets/images/turn_ul.png").convert_alpha(),
            "turn_ur": pygame.image.load("assets/images/turn_ur.png").convert_alpha(),
            "turn_dl": pygame.image.load("assets/images/turn_dl.png").convert_alpha(),
            "turn_dr": pygame.image.load("assets/images/turn_dr.png").convert_alpha(),
        }

        self.food = Food()
        self.rocks = Rocks(self.rock_count)
        self.palms = Palms(self.palm_count)

        self.reset()

    def reset(self):
        mid_r = self.rows // 2
        mid_c = self.cols // 2

        self.body = [
            {"pos": (mid_r, mid_c), "type": "straight"},
            {"pos": (mid_r, mid_c - 1), "type": "straight"},
            {"pos": (mid_r, mid_c - 2), "type": "straight"},
        ]

        self.dir = (0, 1)
        self.next_dir = (0, 1)
        self.score = 0
        self.game_over = False

        self.is_diving = False
        self.oxygen_max = BASE_FPS * 5
        self.oxygen = self.oxygen_max

        self.rocks.place(self.body, self.rows, self.cols)
        self.palms.place(self.body, self.rocks.positions, self.rows, self.cols)
        self.food.place(self.body, self.rocks.positions,self.palms.positions, self.rows, self.cols)

    def toggle_dive(self):
        if self.is_diving:
            self.is_diving = False
        else:
            if self.oxygen > self.oxygen_max * 0.1:
                self.is_diving = True

    def game_over_logic(self):
        if not self.game_over and self.snd_lose and self.sound_enabled:
            self.snd_lose.play()

        self.game_over = True
        if self.score > self.high_score:
            self.high_score = self.score

    def update(self):
        if self.game_over:
            return

        if self.is_diving:
            self.oxygen -= 3
            if self.oxygen <= 0:
                self.oxygen = 0
                self.is_diving = False
                self.game_over_logic()
        else:
            if self.oxygen < self.oxygen_max:
                self.oxygen += 1

        if self.next_dir != (-self.dir[0], -self.dir[1]):
            prev = self.dir
            self.dir = self.next_dir
            turn = self.get_turn_type(prev, self.dir)
            if turn:
                self.body[0]["type"] = turn

        head_r, head_c = self.body[0]["pos"]
        dr, dc = self.dir
        new_head = (head_r + dr, head_c + dc)

        if not (0 <= new_head[0] < self.rows and 0 <= new_head[1] < self.cols):
            self.game_over_logic()
            return

        if self.is_diving:
            if new_head in self.palms.positions:
                self.game_over_logic()
                return
        else:
            if new_head in [s["pos"] for s in self.body] or \
                    new_head in self.rocks.positions or \
                    new_head in self.palms.positions:
                self.game_over_logic()
                return

        self.body.insert(0, {"pos": new_head, "type": "straight"})

        #Їжа
        if new_head == self.food.position:
            if self.food.type == "apple":
                self.score += 1
            elif self.food.type == "banana":
                self.score += 2
            if self.snd_eat and self.sound_enabled:
                self.snd_eat.play()
            self.food.place(self.body, self.rocks.positions, self.palms.positions, self.rows, self.cols)
        else:
            self.body.pop()

        if self.body[-1]["type"].startswith("turn"):
            self.body[-1]["type"] = "straight"

    def get_turn_type(self, prev, new):
        mapping = {
            ((-1, 0), (0, -1)): "turn_ul", ((-1, 0), (0, 1)): "turn_ur",
            ((1, 0), (0, -1)): "turn_dl", ((1, 0), (0, 1)): "turn_dr",
            ((0, -1), (-1, 0)): "turn_dr", ((0, -1), (1, 0)): "turn_ur",
            ((0, 1), (-1, 0)): "turn_dl", ((0, 1), (1, 0)): "turn_ul",
        }
        return mapping.get((prev, new), None)

    def rotate(self, img, direction):
        dr, dc = direction
        if (dr, dc) == (0, 1):
            angle = -90
        elif (dr, dc) == (1, 0):
            angle = 180
        elif (dr, dc) == (0, -1):
            angle = 90
        elif (dr, dc) == (-1, 0):
            angle = 0
        else:
            angle = 0
        return pygame.transform.rotate(img, angle)

    def draw_grid(self, surf):
        for r in range(self.rows):
            for c in range(self.cols):
                color = GREEN if (r + c) % 2 == 0 else LIGHT_GREEN
                pygame.draw.rect(surf, color, (c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size))

    def draw_snake(self, surf):
        alpha = 100 if self.is_diving else 255
        cell = self.cell_size

        for i, seg in enumerate(self.body):
            r, c = seg["pos"]
            x, y = c * cell, r * cell

            img = None
            if i == 0:
                img = self.rotate(self.img_head, self.dir)
            elif i == len(self.body) - 1:
                prev = self.body[i - 1]["pos"]
                dr = prev[0] - r
                dc = prev[1] - c
                img = self.rotate(self.img_tail, (dr, dc))
            elif seg["type"].startswith("turn"):
                img = self.turn_images[seg["type"]]
            else:
                prev = self.body[i - 1]["pos"]
                nxt = self.body[i + 1]["pos"]
                if prev[1] == c and nxt[1] == c:
                    img = pygame.transform.rotate(self.img_body, 90)
                else:
                    img = self.img_body

            img_copy = img.copy()
            img_copy.set_alpha(alpha)
            img_copy = pygame.transform.scale(img_copy, (cell, cell))
            surf.blit(img_copy, (x, y))

    def draw_apple(self, surf):
        r, c = self.food.position
        cell = self.cell_size
        img = pygame.transform.scale(self.img_apple, (cell, cell))
        surf.blit(img, (c * cell, r * cell))

    def draw_banana(self, surf):
        r, c = self.food.position
        cell = self.cell_size
        img = pygame.transform.scale(self.img_banana, (cell, cell))
        surf.blit(img, (c * cell, r * cell))

    def draw_rocks(self, surf):
        cell = self.cell_size
        for pos in self.rocks.positions:
            r, c = pos
            img = pygame.transform.scale(self.img_rock, (cell, cell))
            surf.blit(img, (c * cell, r * cell))

    def draw_palms(self, surf):
        cell = self.cell_size
        for pos in self.palms.positions:
            r, c = pos
            img = pygame.transform.scale(self.img_palma, (cell, cell))
            surf.blit(img, (c * cell, r * cell))

    def draw_ui(self, surf):
        bar_width = 200
        bar_height = 20
        x = WINDOW_W - bar_width - 10
        y = 10

        pygame.draw.rect(surf, (50, 50, 50), (x, y, bar_width, bar_height))

        oxygen_ratio = self.oxygen / self.oxygen_max
        if oxygen_ratio < 0: oxygen_ratio = 0
        fill_width = int(bar_width * oxygen_ratio)

        color = BLUE if oxygen_ratio > 0.25 else RED
        pygame.draw.rect(surf, color, (x, y, fill_width, bar_height))
        pygame.draw.rect(surf, WHITE, (x, y, bar_width, bar_height), 2)

        font = pygame.font.SysFont("arial", 14, True)
        text = font.render("Кисень", True, WHITE)
        surf.blit(text, (x + 70, y + 2))

    def draw_death_screen(self, surf):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill(DARK_OVERLAY)
        surf.blit(overlay, (0, 0))

        font_big = pygame.font.SysFont("arial", 50, True)
        font_small = pygame.font.SysFont("arial", 30, True)
        font_mini = pygame.font.SysFont("arial", 20, True)

        text_game_over = font_big.render("Ти програв!", True, RED)
        text_score = font_small.render(f"Рахунок: {self.score}", True, WHITE)
        text_high = font_small.render(f"Рекорд: {self.high_score}", True, WHITE)
        text_restart = font_small.render("Натисни SPACE для рестату", True, WHITE)
        text_menu = font_mini.render("Натисни ESC для переходу в меню", True, WHITE)

        rect_go = text_game_over.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 - 60))
        rect_sc = text_score.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2))
        rect_hi = text_high.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 + 40))
        rect_rs = text_restart.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 + 100))
        rect_mn = text_menu.get_rect(center=(WINDOW_W // 2, WINDOW_H // 2 + 140))

        surf.blit(text_game_over, rect_go)
        surf.blit(text_score, rect_sc)
        surf.blit(text_high, rect_hi)
        surf.blit(text_restart, rect_rs)
        surf.blit(text_menu, rect_mn)

    def draw(self, surf):
        self.draw_grid(surf)
        self.draw_rocks(surf)
        self.draw_palms(surf)
        if self.food.type == "apple":
            self.draw_apple(surf)
        else:
            self.draw_banana(surf)
        self.draw_snake(surf)
        if not self.game_over:
            self.draw_ui(surf)
        if self.game_over:
            self.draw_death_screen(surf)
