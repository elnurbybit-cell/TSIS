import json
import random
from pathlib import Path

import pygame

from persistence import save_score, get_top_scores
from ui import draw_text, draw_centered_text


class RacerGame:
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    LEADERBOARD = "leaderboard"
    SETTINGS = "settings"

    def __init__(self):
        self.settings = self.load_settings()

        self.width = self.settings["width"]
        self.height = self.settings["height"]
        self.fps = self.settings["fps"]
        self.lane_count = self.settings["lane_count"]

        self.road_color = tuple(self.settings["road_color"])
        self.grass_color = tuple(self.settings["grass_color"])
        self.player_color = tuple(self.settings["player_color"])
        self.traffic_color = tuple(self.settings["traffic_color"])
        self.obstacle_color = tuple(self.settings["obstacle_color"])

        pygame.init()

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("TSIS3 Racer")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.big_font = pygame.font.SysFont("Arial", 42)

        self.running = True
        self.state = self.MENU

        self.username = ""
        self.saved_score = False

        self.reset_game()

    def load_settings(self):
        path = Path("settings.json")

        with open(path, "r") as file:
            return json.load(file)

    def save_settings(self):
        self.settings["sound_on"] = self.sound_on

        with open("settings.json", "w") as file:
            json.dump(self.settings, file, indent=4)

    def reset_game(self):
        self.road_left = 80
        self.road_right = self.width - 80
        self.road_width = self.road_right - self.road_left
        self.lane_width = self.road_width // self.lane_count

        self.player = pygame.Rect(
            self.width // 2 - 20,
            self.height - 100,
            40,
            70
        )

        self.traffic_cars = []
        self.obstacles = []
        self.powerups = []
        self.road_events = []

        self.score = 0
        self.level = 1
        self.health = 3

        self.enemy_speed = self.settings["enemy_speed"]
        self.player_speed = self.settings["player_speed"]

        self.nitro_until = 0
        self.shield = False
        self.sound_on = self.settings["sound_on"]

        self.spawn_timer = 0
        self.event_timer = 0
        self.saved_score = False

    def get_lane_x(self, lane):
        return self.road_left + lane * self.lane_width + self.lane_width // 2 - 20

    def spawn_traffic_car(self):
        lane = random.randint(0, self.lane_count - 1)
        x = self.get_lane_x(lane)

        car = pygame.Rect(x, -90, 40, 70)
        self.traffic_cars.append(car)

    def spawn_obstacle(self):
        lane = random.randint(0, self.lane_count - 1)
        x = self.get_lane_x(lane)

        obstacle = pygame.Rect(x, -60, 40, 40)
        self.obstacles.append(obstacle)

    def spawn_powerup(self):
        lane = random.randint(0, self.lane_count - 1)
        x = self.get_lane_x(lane)

        rect = pygame.Rect(x + 5, -40, 30, 30)
        kind = random.choice(["nitro", "shield", "repair"])

        self.powerups.append({
            "rect": rect,
            "kind": kind
        })

    def spawn_road_event(self):
        event = random.choice(["oil", "construction"])
        lane = random.randint(0, self.lane_count - 1)
        x = self.get_lane_x(lane)

        rect = pygame.Rect(x, -80, 45, 45)

        self.road_events.append({
            "rect": rect,
            "kind": event
        })

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == self.PLAYING:
                        self.state = self.MENU
                    else:
                        self.running = False

                if self.state == self.MENU:
                    self.handle_menu_key(event)

                elif self.state == self.PLAYING:
                    self.handle_playing_key(event)

                elif self.state == self.GAME_OVER:
                    self.handle_game_over_key(event)

                elif self.state == self.LEADERBOARD:
                    if event.key == pygame.K_b:
                        self.state = self.MENU

                elif self.state == self.SETTINGS:
                    self.handle_settings_key(event)

    def handle_menu_key(self, event):
        if event.key == pygame.K_RETURN:
            if self.username == "":
                self.username = "guest"

            self.reset_game()
            self.state = self.PLAYING

        elif event.key == pygame.K_l:
            self.state = self.LEADERBOARD

        elif event.key == pygame.K_s:
            self.state = self.SETTINGS

        elif event.key == pygame.K_q:
            self.running = False

        elif event.key == pygame.K_BACKSPACE:
            self.username = self.username[:-1]

        else:
            if event.unicode.isalnum() or event.unicode == "_":
                if len(self.username) < 15:
                    self.username += event.unicode

    def handle_playing_key(self, event):
        if event.key == pygame.K_SPACE:
            self.nitro_until = pygame.time.get_ticks() + 2000

    def handle_game_over_key(self, event):
        if event.key == pygame.K_r:
            self.reset_game()
            self.state = self.PLAYING

        elif event.key == pygame.K_m:
            self.state = self.MENU

    def handle_settings_key(self, event):
        if event.key == pygame.K_o:
            self.sound_on = not self.sound_on

        elif event.key == pygame.K_b:
            self.save_settings()
            self.state = self.MENU

    def update_player(self):
        keys = pygame.key.get_pressed()
        speed = self.player_speed

        if pygame.time.get_ticks() < self.nitro_until:
            speed += 4

        if keys[pygame.K_LEFT]:
            self.player.x -= speed

        if keys[pygame.K_RIGHT]:
            self.player.x += speed

        if keys[pygame.K_UP]:
            self.player.y -= speed

        if keys[pygame.K_DOWN]:
            self.player.y += speed

        if self.player.left < self.road_left:
            self.player.left = self.road_left

        if self.player.right > self.road_right:
            self.player.right = self.road_right

        if self.player.top < 0:
            self.player.top = 0

        if self.player.bottom > self.height:
            self.player.bottom = self.height

    def update_difficulty(self):
        self.level = self.score // 500 + 1
        self.enemy_speed = self.settings["enemy_speed"] + self.level

    def update_spawning(self):
        self.spawn_timer += 1
        self.event_timer += 1

        spawn_limit = max(25, 75 - self.level * 5)

        if self.spawn_timer >= spawn_limit:
            self.spawn_timer = 0

            choice = random.randint(1, 100)

            if choice <= 60:
                self.spawn_traffic_car()
            elif choice <= 80:
                self.spawn_obstacle()
            elif choice <= 92:
                self.spawn_powerup()
            else:
                self.spawn_road_event()

        if self.event_timer >= 450:
            self.event_timer = 0
            self.spawn_road_event()

    def update_objects(self):
        for car in self.traffic_cars:
            car.y += self.enemy_speed

        for obstacle in self.obstacles:
            obstacle.y += self.enemy_speed

        for powerup in self.powerups:
            powerup["rect"].y += self.enemy_speed

        for road_event in self.road_events:
            road_event["rect"].y += self.enemy_speed

        self.traffic_cars = [
            car for car in self.traffic_cars
            if car.y < self.height + 100
        ]

        self.obstacles = [
            obstacle for obstacle in self.obstacles
            if obstacle.y < self.height + 100
        ]

        self.powerups = [
            powerup for powerup in self.powerups
            if powerup["rect"].y < self.height + 100
        ]

        self.road_events = [
            event for event in self.road_events
            if event["rect"].y < self.height + 100
        ]

    def handle_collision_damage(self):
        if self.shield:
            self.shield = False
            return

        self.health -= 1

        if self.health <= 0:
            self.game_over()

    def check_collisions(self):
        for car in self.traffic_cars[:]:
            if self.player.colliderect(car):
                self.traffic_cars.remove(car)
                self.handle_collision_damage()

        for obstacle in self.obstacles[:]:
            if self.player.colliderect(obstacle):
                self.obstacles.remove(obstacle)
                self.handle_collision_damage()

        for road_event in self.road_events[:]:
            if self.player.colliderect(road_event["rect"]):
                self.road_events.remove(road_event)

                if road_event["kind"] == "oil":
                    self.score = max(0, self.score - 100)
                elif road_event["kind"] == "construction":
                    self.health -= 1
                    if self.health <= 0:
                        self.game_over()

        for powerup in self.powerups[:]:
            if self.player.colliderect(powerup["rect"]):
                self.powerups.remove(powerup)
                self.apply_powerup(powerup["kind"])

    def apply_powerup(self, kind):
        if kind == "nitro":
            self.nitro_until = pygame.time.get_ticks() + 3000

        elif kind == "shield":
            self.shield = True

        elif kind == "repair":
            self.health = min(3, self.health + 1)

    def update_score(self):
        self.score += 1

    def game_over(self):
        self.state = self.GAME_OVER

        if not self.saved_score:
            save_score(self.username, self.score, self.level)
            self.saved_score = True

    def update(self):
        if self.state != self.PLAYING:
            return

        self.update_player()
        self.update_spawning()
        self.update_objects()
        self.check_collisions()
        self.update_score()
        self.update_difficulty()

    def draw_road(self):
        self.screen.fill(self.grass_color)

        road = pygame.Rect(
            self.road_left,
            0,
            self.road_width,
            self.height
        )

        pygame.draw.rect(self.screen, self.road_color, road)

        for i in range(1, self.lane_count):
            x = self.road_left + i * self.lane_width
            pygame.draw.line(self.screen, (255, 255, 255), (x, 0), (x, self.height), 2)

    def draw_objects(self):
        pygame.draw.rect(self.screen, self.player_color, self.player)

        for car in self.traffic_cars:
            pygame.draw.rect(self.screen, self.traffic_color, car)

        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, self.obstacle_color, obstacle)

        for powerup in self.powerups:
            color = (255, 180, 0)

            if powerup["kind"] == "shield":
                color = (160, 0, 255)

            elif powerup["kind"] == "repair":
                color = (0, 255, 0)

            pygame.draw.rect(self.screen, color, powerup["rect"])

        for road_event in self.road_events:
            color = (0, 0, 0)

            if road_event["kind"] == "construction":
                color = (255, 130, 0)

            pygame.draw.rect(self.screen, color, road_event["rect"])

    def draw_hud(self):
        draw_text(self.screen, f"User: {self.username}", 10, 10, self.small_font)
        draw_text(self.screen, f"Score: {self.score}", 10, 35, self.small_font)
        draw_text(self.screen, f"Level: {self.level}", 10, 60, self.small_font)
        draw_text(self.screen, f"Health: {self.health}", 10, 85, self.small_font)

        if self.shield:
            draw_text(self.screen, "Shield: ON", 10, 110, self.small_font)

        if pygame.time.get_ticks() < self.nitro_until:
            draw_text(self.screen, "Nitro: ON", 10, 135, self.small_font)

    def draw_playing(self):
        self.draw_road()
        self.draw_objects()
        self.draw_hud()

    def draw_menu(self):
        self.screen.fill((15, 15, 15))

        draw_centered_text(self.screen, "TSIS3 RACER", 80, self.big_font)
        draw_centered_text(self.screen, "Type username and press ENTER", 170, self.font)
        draw_centered_text(self.screen, f"Username: {self.username or '_'}", 210, self.font)

        draw_centered_text(self.screen, "ENTER - Play", 290, self.font)
        draw_centered_text(self.screen, "L - Leaderboard", 325, self.font)
        draw_centered_text(self.screen, "S - Settings", 360, self.font)
        draw_centered_text(self.screen, "Q - Quit", 395, self.font)

    def draw_game_over(self):
        self.screen.fill((40, 0, 0))

        draw_centered_text(self.screen, "GAME OVER", 100, self.big_font)
        draw_centered_text(self.screen, f"Score: {self.score}", 190, self.font)
        draw_centered_text(self.screen, f"Level: {self.level}", 230, self.font)

        draw_centered_text(self.screen, "R - Retry", 330, self.font)
        draw_centered_text(self.screen, "M - Main Menu", 365, self.font)

    def draw_leaderboard(self):
        self.screen.fill((10, 10, 30))

        draw_centered_text(self.screen, "LEADERBOARD", 50, self.big_font)

        scores = get_top_scores()

        if not scores:
            draw_centered_text(self.screen, "No scores yet", 150, self.font)

        y = 130

        for index, item in enumerate(scores, start=1):
            line = f"{index}. {item['username']} - {item['score']} points - level {item['level']}"
            draw_text(self.screen, line, 80, y, self.small_font)
            y += 32

        draw_centered_text(self.screen, "B - Back", self.height - 70, self.font)

    def draw_settings(self):
        self.screen.fill((10, 30, 10))

        draw_centered_text(self.screen, "SETTINGS", 80, self.big_font)
        draw_centered_text(self.screen, f"O - Sound: {'ON' if self.sound_on else 'OFF'}", 180, self.font)
        draw_centered_text(self.screen, "B - Save and Back", 260, self.font)

    def draw(self):
        if self.state == self.MENU:
            self.draw_menu()

        elif self.state == self.PLAYING:
            self.draw_playing()

        elif self.state == self.GAME_OVER:
            self.draw_game_over()

        elif self.state == self.LEADERBOARD:
            self.draw_leaderboard()

        elif self.state == self.SETTINGS:
            self.draw_settings()

        pygame.display.update()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)

        pygame.quit()