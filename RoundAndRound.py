import pygame
from pygame.locals import *
import random
import math
import sys

XSIZE = 800
YSIZE = 700
XTIMERPOS = 20
YTIMERPOS = 20
ACCELERATIONRATE = 0.2
BREAKRATE = 0.1
SFLINEPOS = XSIZE/2, YSIZE/5
CPPOS = XSIZE/2, YSIZE * 3/4
WALLCOLOUR = 100,0,0
WALLTHICKNESS = 10
SPAWNPOS = XSIZE/2 - 100, YSIZE/5
CARHITBOXSIZE = 12

def TupleAdd(a, b):
    c = (a[0] + b[0], a[1] + b[1])
    return c

def TupleSub(a, b):
    c = (a[0] - b[0], a[1] - b[1])
    return c

def TupleAverage(a, b):
    y = (a[0] + b[0])/2
    z = (a[1] + b[1])/2
    return (y,z)

def fTupToI(a):
    return (int(a[0]), int(a[1]))

def CheckTounching(pos1, pos2, size):
    if ((pos1[0] >= pos2[0] and pos1[0] <= pos2[0] + size[0]) and (pos1[1] >= pos2[1] and pos1[1] <= pos2[1] + size[1])):
        return True
    else:
        return False

class Car:
    def __init__(self, pos):
        self.pos = pos
        self.momentum = (0,0)
        self.rotation = 90
    
    def Move(self):
        self.pos = TupleAdd(self.pos, self.momentum)
    
    def Tick(self):
        #Turn momentum towards rotation
        speed = math.sqrt(self.momentum[0] ** 2 + self.momentum[1] ** 2)
        x = speed * math.sin(math.radians(self.rotation))
        y = speed * math.cos(math.radians(self.rotation))
        self.momentum = TupleAverage(self.momentum, (x,y))
        self.Move()

    def TurnLeft(self):
        self.rotation += 3

    def TurnRight(self):
        self.rotation -= 3

    def SpeedUp(self):
        x = math.sin(math.radians(self.rotation))
        y = math.cos(math.radians(self.rotation))
        self.momentum = TupleAdd(self.momentum, (x * ACCELERATIONRATE, y * ACCELERATIONRATE))

    def Break(self):
        self.momentum = TupleSub(self.momentum, (self.momentum[0] * BREAKRATE, self.momentum[1] * BREAKRATE))

class RoundAndRound:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Round And Round")
                
        self.clock = pygame.time.Clock()

        #Load assets
        self.carImg = pygame.image.load('Assets/car.png')
        self.sfLine = pygame.image.load('Assets/SFLine.png')
        self.checkpoint = pygame.image.load('Assets/Checkpoint.png')

        self.screen = pygame.display.set_mode((XSIZE, YSIZE))

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((200,200,200))

        if pygame.font:
            self.font = pygame.font.Font(None, 32)

        self.car = Car(SPAWNPOS)

        self.barriers = []
        self.lines = []

        self.lapInProgress = False
        self.passedCheckpoint = False
        self.bestLap = None

        self.isDrawing = False

        self.running = True

    def Run(self):
        self.finished = False

        while not self.finished:
            #Handle input
            self.HandleInput()

            #Draw screen
            self.Draw()

            self.car.Tick()

            self.HandleTiming()

            self.clock.tick(60)
        
        pygame.quit()
        return True

    def HandleInput(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if event.button == 1:
                    #Left click, add to wall points
                    self.barriers.append(pos)
                    if self.isDrawing:
                        self.lines.append(True)
                    else:
                        self.lines.append(False)
                        self.isDrawing = True
                elif event.button == 3:
                    #Right click
                    self.isDrawing = False
        
        if pygame.key.get_pressed()[K_LEFT]:
            self.car.TurnLeft()

        if pygame.key.get_pressed()[K_RIGHT]:
            self.car.TurnRight()

        if pygame.key.get_pressed()[K_UP]:
            self.car.SpeedUp()

        if pygame.key.get_pressed()[K_DOWN]:
            self.car.Break()
        
        if pygame.key.get_pressed()[K_r]:
            self.ResetCar()
            self.barriers = []
            self.lines = []
            self.bestLap = None

    def Draw(self):
        #clear screen
        self.screen.blit(self.background, (0,0))

        #Draw border
        pygame.draw.lines(self.screen, WALLCOLOUR, True, ((0,0), (XSIZE,0), (XSIZE, YSIZE), (0, YSIZE)), 30)

        #Draw SF line
        self.screen.blit(self.sfLine, SFLINEPOS)
        #Draw checkpoint
        self.screen.blit(self.checkpoint, CPPOS)

        #Draw walls
        if len(self.barriers) > 1:
            for i in range(0, len(self.barriers) - 1):
                if (self.lines[i + 1] == True):
                    pygame.draw.line(self.screen, WALLCOLOUR, self.barriers[i], self.barriers[i + 1], WALLTHICKNESS)
        if (self.isDrawing):
            pos = pygame.mouse.get_pos()
            pygame.draw.line(self.screen, WALLCOLOUR, self.barriers[len(self.barriers) - 1], pos, WALLTHICKNESS)

        #Draw car
        carOrigin = (self.carImg.get_size()[0]/2, self.carImg.get_size()[1]/2)
        carRect = self.carImg.get_rect(topleft = (self.car.pos[0] - carOrigin[0], self.car.pos[1] - carOrigin[1]))
        offsetCenterToPivot = pygame.math.Vector2(self.car.pos) - carRect.center
        rotatedOffset = offsetCenterToPivot.rotate(self.car.rotation)
        rotatedImageCenter = (self.car.pos[0] - rotatedOffset.x, self.car.pos[1] - rotatedOffset.y)
        rotatedCar = pygame.transform.rotate(self.carImg, self.car.rotation)
        rotatedImageRect = rotatedCar.get_rect(center = rotatedImageCenter)

        self.screen.blit(rotatedCar, rotatedImageRect)

        #Draw Timer
        if self.lapInProgress == False:
            timerStr = "Current: 0.0"
        else:
            timerStr = "Current: " + str((pygame.time.get_ticks() - self.startTime)/1000)
        timerTxt = self.font.render(timerStr, True, (10,10,10))
        self.screen.blit (timerTxt, (XTIMERPOS,YTIMERPOS))
        if self.bestLap != None:
            bestStr = "Best: " + str(self.bestLap/1000)
            bestTxt = self.font.render(bestStr, True, (10,10,10))
            displayPos = (XTIMERPOS, YTIMERPOS + timerTxt.get_size()[1])
            self.screen.blit(bestTxt, displayPos)

        #Refresh the screen
        pygame.display.flip()
    
    def HandleTiming(self):
        carOrigin = (self.carImg.get_size()[0]/2, self.carImg.get_size()[1]/2)
        carRect = self.carImg.get_rect(topleft = (self.car.pos[0] - carOrigin[0], self.car.pos[1] - carOrigin[1]))
        offsetCenterToPivot = pygame.math.Vector2(self.car.pos) - carRect.center
        rotatedOffset = offsetCenterToPivot.rotate(self.car.rotation)
        rotatedImageCenter = (self.car.pos[0] - rotatedOffset.x, self.car.pos[1] - rotatedOffset.y)

        if (CheckTounching(rotatedImageCenter, SFLINEPOS, self.sfLine.get_size())):
            if self.lapInProgress == False:
                self.lapInProgress = True
                self.startTime = pygame.time.get_ticks()
            elif self.passedCheckpoint == True:
                lapTime = pygame.time.get_ticks() - self.startTime
                if (self.bestLap == None or self.bestLap > lapTime):
                    self.bestLap = lapTime
                self.startTime = pygame.time.get_ticks()
            self.passedCheckpoint = False
        
        if (CheckTounching(rotatedImageCenter, CPPOS, self.checkpoint.get_size())):
            if self.passedCheckpoint == False:
                self.passedCheckpoint = True
            
        carOrigin = (self.carImg.get_size()[0]/2, self.carImg.get_size()[1]/2)
        carRect = self.carImg.get_rect(topleft = (self.car.pos[0] - carOrigin[0], self.car.pos[1] - carOrigin[1]))
        offsetCenterToPivot = pygame.math.Vector2(self.car.pos) - carRect.center
        rotatedOffset = offsetCenterToPivot.rotate(self.car.rotation)
        rotatedImageCenter = (self.car.pos[0] - rotatedOffset.x, self.car.pos[1] - rotatedOffset.y)
        col = []
        col.append(self.screen.get_at(fTupToI(rotatedImageCenter)))
        col.append(self.screen.get_at(fTupToI(TupleAdd(self.car.pos, (0, CARHITBOXSIZE)))))
        col.append(self.screen.get_at(fTupToI(TupleAdd(self.car.pos, (0, -CARHITBOXSIZE)))))
        col.append(self.screen.get_at(fTupToI(TupleAdd(self.car.pos, (CARHITBOXSIZE, 0)))))
        col.append(self.screen.get_at(fTupToI(TupleAdd(self.car.pos, (-CARHITBOXSIZE, 0)))))
        for c in col:
            if c == WALLCOLOUR:
                self.ResetCar()

    def ResetCar(self):
        self.car.__init__(SPAWNPOS)
        self.lapInProgress = False


game = RoundAndRound()
game.Run()