# A small planet simulation

import pygame
import math

# None of these scales have any impact on the values used to calculate the physical interactions of the simulation
DISTANCE_SCALE = 1/1000000 # Scale for the distances between objects
PLANET_RADIUS_SCALE = 1/200000 # Scale for the objects' sizes, to make the simulation more practical visually
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900

DT = 900
TRAIL_DURATION = 172800
G = 6.674e-11

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

run = True

class Planet :
    def __init__(self, radius = None, mass = None, color = None, initPosX = None, initPosY = None, initVelX = None, initVelY = None) :
        self.radius = radius # Meters
        self.mass = mass # Kilograms
        self.color = color
        self.posX = initPosX
        self.posY = initPosY
        self.velX = initVelX
        self.velY = initVelY
        self.trail = [] # Stores the 100 previous positions of the object to draw its trail
    
    def calcForce(self, otherPlanet) :
        distX = otherPlanet.posX - self.posX
        distY = otherPlanet.posY - self.posY
        dist = (distX**2 + distY**2)**0.5

        if dist == 0 : return 0, 0

        force = G * self.mass * otherPlanet.mass / dist**2

        forceX = force * distX / dist
        forceY = force * distY / dist

        return forceX, forceY

    def updatePos(self, forceX, forceY, dt) :
        accelX = forceX / self.mass
        accelY = forceY / self.mass

        self.velX += accelX * dt
        self.velY += accelY * dt

        self.posX += self.velX * dt
        self.posY += self.velY * dt

def getOrbitalVelocity(planetA, planetB) :
    distX = planetB.posX - planetA.posX
    distY = planetB.posY - planetA.posY
    dist = math.sqrt(distX**2 + distY**2)

    if dist == 0 : return 0

    vel = math.sqrt((G * planetA.mass) / dist)
    return vel

def getClosestPlanet(mousePos, planets, referencial) : # Searches the closest object to the mouse position
    mouseX, mouseY = mousePos
    closestPlanet = None
    minDist = float('inf') # Starting the search with an infinite threshold

    for planet in planets :
        screenX = SCREEN_WIDTH / 2 + (planet.posX - referencial.posX) * DISTANCE_SCALE
        screenY = SCREEN_HEIGHT / 2 - (planet.posY - referencial.posY) * DISTANCE_SCALE

        dist = math.sqrt((mouseX - screenX)**2 + (mouseY - screenY)**2)

        if dist < minDist :
            minDist = dist
            closestPlanet = planet
        
    if minDist < closestPlanet.radius * PLANET_RADIUS_SCALE + 20 :
        return closestPlanet
    else :
        return None

planets = [
    Planet(6.378137e6, 5.9736e24, (25, 25, 245), 0, 0, 0, 0),
    Planet(1.7374e6, 7.35e22, (100, 100, 100), 3.84400e8, 0, 0, 1018.4025564134593)
]

print(getOrbitalVelocity(planets[0], planets[1]))

referencial = Planet(initPosX=0, initPosY=0)
maxTrailPoints = max(2, int(TRAIL_DURATION / DT))

while run :
    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            run = False
        
        if event.type == pygame.MOUSEBUTTONDOWN :
            if event.button == 1 : # Checks for a left click
                # Changes the referencial of the animation to the selected planet, which is now fixed at the center of the screen
                selectedPlanet = getClosestPlanet(event.pos, planets, referencial)
                referencial = selectedPlanet if selectedPlanet else Planet(initPosX=0, initPosY=0)
                for planet in planets :
                    planet.trail = []
            

    # Setting a black background
    screen.fill((0,0,0))

    forces = []
    for focusPlanet in planets :
        totalForcesX = 0
        totalForcesY = 0

        for planet in planets :
            if planet == focusPlanet :
                continue
            forceX, forceY = focusPlanet.calcForce(planet)
            totalForcesX += forceX
            totalForcesY += forceY
        
        forces.append((totalForcesX, totalForcesY))

    for i in range(len(planets)) :
        forceX, forceY = forces[i]
        planets[i].updatePos(forceX, forceY, DT)

    temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    for planet in planets :
        pygame.draw.circle( screen,
                            planet.color,
                            (SCREEN_WIDTH / 2 + (planet.posX - referencial.posX) * DISTANCE_SCALE,
                            SCREEN_HEIGHT / 2 - (planet.posY - referencial.posY) * DISTANCE_SCALE),
                            planet.radius * PLANET_RADIUS_SCALE)
        planet.trail.append((int(SCREEN_WIDTH / 2 + (planet.posX - referencial.posX) * DISTANCE_SCALE), int(SCREEN_HEIGHT / 2 - (planet.posY - referencial.posY) * DISTANCE_SCALE)))

        if len(planet.trail) == maxTrailPoints :
            planet.trail.pop(0)
        if len(planet.trail) > 1:
            for i in range(len(planet.trail) - 1):
                alpha = int(255 * (i / len(planet.trail)))
                
                segmentColor = (planet.color[0], planet.color[1], planet.color[2], alpha)

                pygame.draw.line(surface=temp_surface, color=segmentColor, start_pos=planet.trail[i], end_pos=planet.trail[i+1], width=2)
        
    screen.blit(temp_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()