# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
import time

from pygame.locals import *

FPS = 10 # PROMENA: namaluvanje od 15 na 10
WINDOWWIDTH = 800 # PROMENA: zgolemuvanje od 640 na 800
WINDOWHEIGHT = 600 # PROMENA: zgolemuvanje od 480 na 600
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
# PROMENA: dodadena boja YELLOW
YELLOW    = (255, 255,   0)
# PROMENA: dodadena boja BLUE
BLUE      = (  0,   0, 255)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head

# PROMENA: dodadena promenliva YELLOWAPPLEFREQUENCY vo koja se cuva kolku sekundi treba da pominat za da se pojavi zoltoto jabolko
YELLOWAPPLEFREQUENCY = 10
# PROMENA: dodadena promenliva YELLOWAPPLEDURATION vo koja se cuva kolku sekundi treba da stoi zoltoto jabolko
YELLOWAPPLEDURATION = 3
# PROMENA: dodadena promenliva YELLOWAPPLE koja kazuva dali na ekranot ima zolto jabolko
YELLOWAPPLE = False

# PROMENA: dodadena promenliva BLUEAPPLEFREQUENCY vo koja se cuva kolku sekundi treba da pominat za da se pojavi sinoto jabolko
BLUEAPPLEFREQUENCY = 40
# PROMENA: dodadena promenliva BLUEAPPLEDURATION vo koja se cuva kolku sekundi treba da stoi sinoto jabolko
BLUEAPPLEDURATION = 5
# PROMENA: dodadena promenliva BLUEAPPLE koja kazuva dali na ekranot ima sino jabolko
BLUEAPPLE = False

# PROMENA: dodadena promenliva SPEEDUPEVENT koja pretstavuva nastan koj ke ja zabrza igrata
SPEEDUPEVENT = pygame.USEREVENT + 1
# PROMENA: dodadena promenliva SPEEDUPEVENTFREQUENCY vo koja se cuva brojot na milisekundi megju zabrzuvanjata
SPEEDUPEVENTFREQUENCY = 30000

# PROMENA: dodadena promenliva PREVIOUSSPEED vo koja se cuva prethodnata vrednost na brzinata
PREVIOUSSPEED = FPS

# dodadena promenliva WORMCOLOR vo koja se cuva bojata na crvot
WORMCOLOR = GREEN

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    # PROMENA: referenciranje na globalnite promenlivi FPS, PREVIOUSSPEED, YELLOWAPPLE, BLUEAPPLE i WORMCOLOR
    global FPS, PREVIOUSSPEED, YELLOWAPPLE, BLUEAPPLE, WORMCOLOR

    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    # Start the apple in a random place.
    apple = getRandomLocation()

    # PROMENA: odreduvanje na koordinatite na zoltoto jabolko i zacuvuvanje na vremeto na negovo pojavuvanje
    # (dokolku ima isti koordinati so crvenoto jabolko, se zemaat drugi)
    yellowApple = getRandomLocation()
    while yellowApple == apple:
        yellowApple = getRandomLocation()
    yellowAppleTime = time.time()

    # PROMENA: odreduvanje na koordinatite na sinoto jabolko i zacuvuvanje na vremeto na negovo pojavuvanje
    # (dokolku ima isti koordinati so crvenoto ili zoltoto jabolko, se zemaat drugi)
    blueApple = getRandomLocation()
    while blueApple == apple or blueApple == yellowApple:
        blueApple = getRandomLocation()
    blueAppleTime = time.time()

    # PROMENA: nastanot SPEEDUPEVENT ke se slucuva na sekoi SPEEDUPEVENTFREQUENCY milisekundi
    pygame.time.set_timer(SPEEDUPEVENT, SPEEDUPEVENTFREQUENCY)

    # PROMENA: dodadena promenliva score vo koja se cuvaat poenite
    # score ne zavisi direktno od dolzinata na crvot, tuku pretstavuva broj na crveni jabolka koi gi izel crvot
    # zoltite i sinite jabolka ne vlijaat na score
    score = 0

    # print("Score: " + str(score))

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()
            # PROMENA: nastanot SPEEDUPEVENT go zacuvuva FPS vo PREVIOUSSPEED i predizvikuva zgolemuvanje na FPS za 5
            elif event.type == SPEEDUPEVENT:
                PREVIOUSSPEED = FPS
                FPS += 5
                # PROMENA: WORMCOLOR dobiva random vrednost koga se zgolemuva brzinata
                WORMCOLOR = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # check if the worm has hit itself or the edge
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
            return # game over
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return # game over

        # check if worm has eaten an apply
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            apple = getRandomLocation() # set a new apple somewhere
            # PROMENA: zgolemuvanje na poenite za 1 koga crvot ke izede crveno jabolko
            score += 1
            # print("Wormy ate a red apple!")
            # print("Score: " + str(score))
        else:
            del wormCoords[-1] # remove worm's tail segment

        # PROMENA: proverka dali crvot izel zolto jabolko
        if wormCoords[HEAD]['x'] == yellowApple['x'] and wormCoords[HEAD]['y'] == yellowApple['y'] and YELLOWAPPLE:
            # print("Wormy ate a yellow apple!")
            # print("Score: " + str(score))
            YELLOWAPPLE = False
            # zemanje novi koordinati za zoltoto jabolko i zacuvuvanje na vremeto
            yellowApple = getRandomLocation()
            while yellowApple == apple:
                yellowApple = getRandomLocation()
            yellowAppleTime = time.time()
            # namaluvanje na dolzinata na crvot za 1 (dokolku dolzinata e pogolema ili ednakva na 3)
            if len(wormCoords) >= 3:
                del wormCoords[-2]

        # PROMENA: proverka dali crvot izel sino jabolko
        if wormCoords[HEAD]['x'] == blueApple['x'] and wormCoords[HEAD]['y'] == blueApple['y'] and BLUEAPPLE:
            # print("Wormy ate a blue apple!")
            # print("Score: " + str(score))
            BLUEAPPLE = False
            # zemanje novi koordinati za sinoto jabolko i zacuvuvanje na vremeto
            blueApple = getRandomLocation()
            while blueApple == apple or blueApple == yellowApple:
                blueApple = getRandomLocation()
            blueAppleTime = time.time()
            # namaluvanje na brzinata na nejzinata prethodna vrednost
            FPS = PREVIOUSSPEED
            # PROMENA: WORMCOLOR dobiva random vrednost koga se namaluva brzinata
            WORMCOLOR = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)

        # PROMENA: na sekoi YELLOWAPPLEFREQUENCY sekundi se pojavuva zoltoto jabolko
        if time.time() - yellowAppleTime > YELLOWAPPLEFREQUENCY:
            YELLOWAPPLE = True
            drawApple(yellowApple, YELLOW)
            if yellowApple == {'x': 999, 'y': 999}:
                YELLOWAPPLE = False
                yellowApple = getRandomLocation()
                while yellowApple == apple:
                    yellowApple = getRandomLocation()
                yellowAppleTime = time.time()

        # PROMENA: YELLOWAPPLEDURATION sekundi posle pojavuvanjeto na zoltoto jabolko toa isceznuva
        if time.time() - yellowAppleTime > YELLOWAPPLEFREQUENCY + YELLOWAPPLEDURATION:
            YELLOWAPPLE = False
            yellowApple = {'x': 999, 'y': 999}
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawWorm(wormCoords)

        # PROMENA: na sekoi BLUEAPPLEFREQUENCY sekundi se pojavuva sinoto jabolko
        if time.time() - blueAppleTime > BLUEAPPLEFREQUENCY:
            BLUEAPPLE = True
            drawApple(blueApple, BLUE)
            if blueApple == {'x': 999, 'y': 999}:
                BLUEAPPLE = False
                blueApple = getRandomLocation()
                while blueApple == apple or blueApple == yellowApple:
                    blueApple = getRandomLocation()
                blueAppleTime = time.time()

        # PROMENA: BLUEAPPLEDURATION sekundi posle pojavuvanjeto na sinoto jabolko toa isceznuva
        if time.time() - blueAppleTime > BLUEAPPLEFREQUENCY + BLUEAPPLEDURATION:
            BLUEAPPLE = False
            blueApple = {'x': 999, 'y': 999}
            DISPLAYSURF.fill(BGCOLOR)
            drawGrid()
            drawWorm(wormCoords)

        drawApple(apple)
        drawScore(score) # PROMENA: len(wormCoords) - 3 e zameneto so score
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


# PROMENA: GREEN e zameneto so WORMCOLOR
def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, WORMCOLOR, wormInnerSegmentRect)


# PROMENA: dodaden parametar color so default vrednost RED
def drawApple(coord, color=RED):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, color, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()