import math
import asyncio
import pygame
import random


pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()

#
class Asteroid:
    def __init__(self, x, y, dx, dy, r):
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(dx, dy)
        self.radius = r
        self.mass = r ** 2
        self.color = (255, 255, 255)

    def move(self):
        self.pos += self.velocity

    def bounce(self):
        if self.pos.x - self.radius < 0 or self.pos.x + self.radius > 600:
            self.velocity.x = -self.velocity.x
            self.pos.x = max(self.radius, min(self.pos.x, 600 - self.radius))

        if self.pos.y - self.radius < 0 or self.pos.y + self.radius > 400:
            self.velocity.y = -self.velocity.y
            self.pos.y = max(self.radius, min(self.pos.y, 400 - self.radius))

    def draw(self):
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.pos.x), int(self.pos.y)),
            self.radius,
        )

class Ship:
    missles = []
    MISSLE_SPEED = 5
    MISSLE_COLOR = (255, 0, 0)
    MISSLE_SIZE = 5
    
    def __init__(self, x, y, angle):
        self.pos = pygame.math.Vector2(x, y)
        self.angle = angle
        self.color = (0, 255, 0)
        self.size = 20

    def shoot(self):
        direction = pygame.math.Vector2(math.cos(-self.angle), math.sin(-self.angle))
        missle_velocity = direction * self.MISSLE_SPEED
        missle_pos = self.pos + direction * self.size
        self.missles.append((missle_pos, missle_velocity))
    

    def draw(self):
        for missle in self.missles:
            missle_pos, missle_velocity = missle
            pygame.draw.circle(
                screen,
                self.MISSLE_COLOR,
                (int(missle_pos.x), int(missle_pos.y)),
                self.MISSLE_SIZE,
            )
            missle_pos += missle_velocity
            self.hit(missle, asteroids)
            if missle_pos.x < 0 or missle_pos.x > 600 or missle_pos.y < 0 or missle_pos.y > 400:
                self.missles.remove(missle)
        direction = pygame.math.Vector2(math.cos(-self.angle), math.sin(-self.angle))
        pygame.draw.polygon(
            screen,
            self.color,
            [
                (self.pos + self.size * direction.rotate(-140)),
                (self.pos + self.size * direction.rotate(140)),
                (self.pos + self.size * direction),
            ],
        )
        if self.pos.x < 0:
            self.pos.x = 0
        elif self.pos.x > 600:
            self.pos.x = 600
        if self.pos.y < 0:
            self.pos.y = 0
        elif self.pos.y > 400:
            self.pos.y = 400
    def hit(self,missle, asteroids):
        for asteroid in asteroids:
            distance = pygame.math.Vector2(asteroid.pos - missle[0])
            if distance.length() < asteroid.radius + self.MISSLE_SIZE:
                asteroids.remove(asteroid)
                self.missles.remove(missle)
        
class enemy:
    def __init__(self, x, y, speed, direction):
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(speed * math.cos(direction), speed * math.sin(direction))
        self.direction = pygame.math.Vector2(math.cos(direction), math.sin(direction))
        self.size = 20
        self.state = 'PATROL'
        self.color = (255, 0, 0)

    def move(self):
        if self.state == 'PATROL':
            self.pos += self.velocity
            
        elif self.state == 'CHASE':
            self.pos += self.direction * self.velocity.length()

    def bounce(self):
        if self.pos.x - self.size < 0 or self.pos.x + self.size > 600:
            self.velocity.x = -self.velocity.x
            self.pos.x = max(self.size, min(self.pos.x, 600 - self.size))

        if self.pos.y - self.size < 0 or self.pos.y + self.size > 400:
            self.velocity.y = -self.velocity.y
            self.pos.y = max(self.size, min(self.pos.y, 400 - self.size))

    def vision(self, ship):
        distance = pygame.math.Vector2(ship.pos - self.pos)
        dot = self.direction.dot(distance.normalize())
        if dot > 0.5 and distance.length() < 200:
            self.state = 'CHASE'
            self.direction = distance.normalize()
            if distance.length() < 20:
                print("Game Over")
                pygame.quit()
                exit()
        else:
            self.state = 'PATROL'
            self.direction = self.velocity.normalize()
        
    def draw(self):
        pygame.draw.rect(
            screen,
            self.color,
            pygame.Rect((int(self.pos.x), int(self.pos.y)), (self.size, self.size))
        )
        pygame.draw.line(
            screen,
            (0, 255, 0),
            (int(self.pos.x + self.size / 2), int(self.pos.y + self.size / 2)),
            (int(self.pos.x + self.size / 2 + self.direction.x * 20), int(self.pos.y + self.size / 2 + self.direction.y * 20)),
            2
        )
def random_asteroid(num):
    asteroids = []
    for _ in range(num):
        x = random.randint(50, 550)
        y = random.randint(50, 350)
        dx = random.randint(-3, 3)
        dy = random.randint(-3, 3)
        r = random.randint(10, 30)
        asteroids.append(Asteroid(x, y, dx, dy, r))
    return asteroids




def collision_check():
    for i in range(len(asteroids)):
        for j in range(i + 1, len(asteroids)):
            a1 = asteroids[i]
            a2 = asteroids[j]
            distance = pygame.math.Vector2(a1.pos - a2.pos)
            if distance.length() < a1.radius + a2.radius:
                
                normal = distance.normalize()
                relative_velocity = a1.velocity - a2.velocity
                velocity_along_normal = relative_velocity.dot(normal)

                if velocity_along_normal > 0:
                    continue

                
                impulse_magnitude = -2 * velocity_along_normal
                impulse_magnitude /= (1 / a1.mass + 1 / a2.mass)

                impulse = impulse_magnitude * normal
                a1.velocity += impulse / a1.mass
                a2.velocity -= impulse / a2.mass
async def main():
    global running, asteroids, Ship, enemy, velocity
    running = True
    asteroids = random_asteroid(10)
    Ship = Ship(300, 200, 0)
    enemy = enemy(100, 100, 1, math.radians(45))
    velocity = pygame.math.Vector2(0, 0)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                target = pygame.Vector2(event.pos)
                Ship.shoot()
        keys = pygame.key.get_pressed()
        
        acceleration = -.03*velocity

        if keys[pygame.K_LEFT]:
            Ship.angle += math.radians(3)

        if keys[pygame.K_RIGHT]:
            Ship.angle -= math.radians(3)

        if keys[pygame.K_UP]:
            acceleration = pygame.math.Vector2(math.cos(-Ship.angle), math.sin(-Ship.angle)) * .06

        velocity += acceleration
        Ship.pos += velocity
        for asteroid in asteroids:
            asteroid.move()
            asteroid.bounce()

        enemy.move()
        enemy.bounce()
        enemy.vision(Ship)

        collision_check()
        screen.fill((20, 24, 40))
        for asteroid in asteroids:
            asteroid.draw()

        Ship.draw()
        enemy.draw()
        pygame.display.flip()

        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
