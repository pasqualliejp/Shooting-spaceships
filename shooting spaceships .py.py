import pygame
import os
import random

pygame.font.init()

# Pygame window
WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader")

# Load images
RED_ENEMY = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
BLUE_ENEMY = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
GREEN_ENEMY = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
YELLOW_PLAYER = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Scaling bg to fit window
BG = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT)
)


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    # Move up for player and down for enemy
    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return self.y >= height and self.y <= 0

    def collison(self, obj):
        return collide(self, obj)


class Ship:
    # Half sec cooldown between laser shots
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cooldown_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        # Draw laser if any
        for laser in self.lasers:
            laser.draw(window)

    # Collison of player and enemy laser
    def move_laser(self, vel, player_obj):
        # Wait for cooldown period
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            # Remove laser if off the screen or hits the player
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collison(player_obj):
                player_obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def shoot(self):
        if self.cooldown_counter == 0:
            # Add laser whenever player shoots
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            # Start cooldown counter
            self.cooldown_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_PLAYER
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    # Overriding base class method
    # Collison of enemies and player laser
    def move_laser(self, vel, enemy_objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for enemy_obj in enemy_objs:
                    # Check for collison with all the enemies
                    if laser.collison(enemy_obj):
                        enemy_objs.remove(enemy_obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    # Overriding base class method
    # Drawing the healthbar of player
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        # Static red rectangle
        pygame.draw.rect(
            window,
            (255, 0, 0),
            (
                self.x,
                (self.y + self.ship_img.get_height() + 10),
                self.ship_img.get_width(),
                10,
            ),
        )
        # Dynamic green rectangle
        pygame.draw.rect(
            window,
            (0, 255, 0),
            (
                self.x,
                (self.y + self.ship_img.get_height() + 10),
                self.ship_img.get_width() * (self.health / self.max_health),
                10,
            ),
        )


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_ENEMY, RED_LASER),
        "blue": (BLUE_ENEMY, BLUE_LASER),
        "green": (GREEN_ENEMY, GREEN_LASER),
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        # Create enemy based on color passed
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    # Overriding base class method
    # Offsetting lasers x position
    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1

    def move(self, vel):
        self.y += vel


# Check if the two objects collide based on their mask
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    # Variables
    run = True
    FPS = 60

    level = 0
    lives = 5

    enemies = []
    wave_length = 5

    # Velocities
    enemy_vel = 1
    player_vel = 3
    laser_vel = 4

    lost = False
    lost_count = 0

    clock = pygame.time.Clock()

    # Fonts
    main_font = pygame.font.SysFont("Nunito", 30)
    lost_font = pygame.font.SysFont("Nunito", 50)

    player = Player(250, 450)

    def redraw_window():
        # Draw bg, level and lives
        WIN.blit(BG, (0, 0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # Draw enemies and player
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        # Draw Game over screen
        if lost:
            lost_label = lost_font.render("Game Over", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 280))

        pygame.display.update()

    # Game loop
    while run:
        # Setting the FPS and redrawing the window 60 times per sec
        clock.tick(FPS)
        redraw_window()

        # Game over condition
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        # Show Game over screen for 3 sec
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        # Increase the level after each wave
        if len(enemies) == 0:
            level += 1
            wave_length += 2
            for i in range(wave_length):
                # Initializing random enemy at random pos
                enemy = Enemy(
                    random.randrange(50, WIDTH - 100),
                    random.randrange(-1200, -100),
                    random.choice(["red", "blue", "green"]),
                )
                enemies.append(enemy)

        # Quit the function and return to main menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Key events
        keys = pygame.key.get_pressed()
        # Player movements
        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if (
            keys[pygame.K_s]
            and player.y + player_vel + player.get_height() + 15 < HEIGHT
        ):
            player.y += player_vel
        # Player shoots
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            # Move each enemy and their laser
            enemy.move(enemy_vel)
            enemy.move_laser(laser_vel, player)
            # Enemy shoots at random inverval
            if random.randrange(0, 10 * FPS) == 1:
                enemy.shoot()

            # Remove enemy if off screen or collided with player
            if collide(enemy, player):
                player.health -= 20
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        # Move player laser with -ve velocity
        player.move_laser(-laser_vel, enemies)


def main_menu():
    instr_font = pygame.font.SysFont("Nunito", 50)
    run = True

    while run:
        # Draw main menu
        WIN.blit(BG, (0, 0))
        instr_label = instr_font.render("Press Enter to Begin", 1, (255, 255, 255))
        WIN.blit(instr_label, (WIDTH / 2 - instr_label.get_width() / 2, 280))
        pygame.display.update()

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                main()

    pygame.quit()


main_menu()
