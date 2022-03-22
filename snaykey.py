import random, pygame, sys, socket, threading, json
from pygame.locals import *

FPS = 2
flag = 0
flag2 = True
flag3 = 1
width1 = 640
height1 = 480
cell_size = 20
assert width1 % cell_size == 0, "Window width must be a multiple of cell size."
assert height1 % cell_size == 0, "Window height must be a multiple of cell size."
cell_width = int(width1 / cell_size)
cell_height = int(height1 / cell_size)
block = threading.Lock()
apple = {'x': 11, 'y': 11}
host = 'xxx.xxx.xxx.xxx' # host's IP-adress
port = xxx # host's port

server = (host, port)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


#         R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY  = (40, 40, 40)
DARKORANGE = (255, 79, 0)
ORANGE = (255, 146, 24)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head
worm2Coords = [] # coordinates of the player 2's snake

def receiving():
    global worm2Coords, apple, flag2
    
    while True:
        if flag2:
            data2, adr = s.recvfrom(1024)
            data2 = data2.decode('utf-8')
            data3 = json.loads(data2)
            apple = data3[0]
            worm2Coords = data3[1]

rt = threading.Thread(target = receiving, args = [])

def main():
    
    global FPSCLOCK, displaysurf, basicfont

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    displaysurf = pygame.display.set_mode((width1, height1))
    basicfont = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Snaykey')

    showStartScreen()
    
    while True:
        runGame()
        showGameOverScreen()

def runGame():
    # Set a random start point
    global flag, apple, flag2, worm2Coords
    startx = random.randint(5, cell_width - 6)
    starty = random.randint(5, cell_height - 6)
    
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]

    direction = RIGHT
    
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

        # check if the worm has hit itself or the edge
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == cell_width or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == cell_height:
            return # game over
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return # game over
        for worm2Body in worm2Coords:
            if wormCoords[HEAD]['x'] == worm2Body['x'] and wormCoords[HEAD]['y'] == worm2Body['y']:
                return #game over

        # check if worm has eaten an apply
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            apple = {'x': -1, 'y': -1} # send a request for the new apple
            print ('[Apple Collision] -> [Sending request]'+str(apple))
            flag2 = False
        else:
            del wormCoords[-1] # remove worm's tail segment

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}

        #update the screen
        wormCoords.insert(0, newHead)
        displaysurf.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawApple(apple)
        drawScore(len(wormCoords) - 3)
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        spisok = [apple, flag2, wormCoords]

        # data basically consists of:
            # Apple position
            # Worm Coordinates
            # And a Flag, that is supposed to determine if the apple was eaten
        data = json.dumps(spisok)
        s.sendto(data.encode('utf-8'), server)

        flag2 = True

        # start the receiving thread after one iteration of the apple cycle
        if flag == 0:
            rt.start()
            flag = 1

# menu - start check
def drawPressKeyMsg():
    pressKeySurf = basicfont.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (width1 - 200, height1 - 30)
    displaysurf.blit(pressKeySurf, pressKeyRect)

def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()
    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

# the menu itself
def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Snaykey!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Snaykey!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        displaysurf.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (width1 / 2, height1 / 2)
        displaysurf.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (width1 / 2, height1 / 2)
        displaysurf.blit(rotatedSurf2, rotatedRect2)

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

#exit screen
def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Конец', True, WHITE)
    overSurf = gameOverFont.render('Игры', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (width1 / 2, 10)
    overRect.midtop = (width1 / 2, gameRect.height + 10 + 25)

    displaysurf.blit(gameSurf, gameRect)
    displaysurf.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore(score):
    scoreSurf = basicfont.render('Ваш счет: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (width1 - 120, 10)
    displaysurf.blit(scoreSurf, scoreRect)

def drawWorm(wormCoords):
    global worm2Coords

    #drawing the coordinates of both worms

    for coord in wormCoords:
        x = coord['x'] * cell_size
        y = coord['y'] * cell_size
        wormSegmentRect = pygame.Rect(x, y, cell_size, cell_size)
        pygame.draw.rect(displaysurf, DARKORANGE, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, cell_size - 8, cell_size - 8)
        pygame.draw.rect(displaysurf, ORANGE, wormInnerSegmentRect)
        
    for coord2 in worm2Coords:
        x2 = coord2['x'] * cell_size
        y2 = coord2['y'] * cell_size
        worm2SegmentRect = pygame.Rect(x2, y2, cell_size, cell_size)
        pygame.draw.rect(displaysurf, DARKGREEN, worm2SegmentRect)
        worm2InnerSegmentRect = pygame.Rect(x2 + 4, y2 + 4, cell_size - 8, cell_size - 8)
        pygame.draw.rect(displaysurf, GREEN, worm2InnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * cell_size
    y = coord['y'] * cell_size
    appleRect = pygame.Rect(x, y, cell_size, cell_size)
    pygame.draw.rect(displaysurf, RED, appleRect)


def drawGrid():
    for x in range(0, width1, cell_size): # draw vertical lines
        pygame.draw.line(displaysurf, DARKGRAY, (x, 0), (x, height1))
    for y in range(0, height1, cell_size): # draw horizontal lines
        pygame.draw.line(displaysurf, DARKGRAY, (0, y), (width1, y))
        
        
if __name__ == '__main__':
    main()