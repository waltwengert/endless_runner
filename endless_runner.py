import tkinter as tk
import time
from random import randrange

#window dimensions
WWIDTH = 600
WHEIGHT = 400

#game properties
GHEIGHT = WHEIGHT - (WHEIGHT/5) #game frame gets 4/5, rest for controls
FPS = 60 #how many times per second the game loops
SPEEDINT = 250 #the loop number interval that will increase speed
STARTLIVES = 3
LANES = 4
LHEIGHT = GHEIGHT / LANES #lanes are equal height portions of game frame

#player/object properties
CSIDE = 40 #square so just need one side
OSIDE = 30
PICKUPVAL = 1000 #amount of score added with each pickup
NUMENTS = 4 #number of non-player entities in the game

#Game object that manages general game properties including main window
##addScore(x), addSpeed(x), addLives(x) methods modify the game properties
##createRect(...), moveRect(...) are support methods for managing Entitys' rect
##suspend(), resume() control whether the game loop is running or not
##start() begins a game, close() stops the game loop then closes the window
##flash("x") sets Game background colour (used for visual feedback)
##loop() handles any changes needed to Game each time the game loops
class Game:
    def __init__(self, lives):
        self.lives = lives
        self.score = 1
        self.speed = 1
        self.loopNo = 0
        self.running = True
        self.quit = False

        #setup a window with given dimensions that cannot be resized
        self.window = tk.Tk()
        self.window.title("Endless Runner")
        self.window.geometry("%dx%d" % (WWIDTH, WHEIGHT))
        self.window.configure(background="grey")
        self.window.resizable(0, 0)
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        #game gets 4/5 of screen vertically, 1/5 reserved for controls
        self.gameCanv = tk.Canvas(self.window, width=WWIDTH, height=GHEIGHT)
        self.controls = tk.Frame(self.window, width=WWIDTH, height=WHEIGHT/5,
                                 background="grey")
        self.gameCanv.pack()
        self.controls.pack()
        
        #to allow for empty buffer columns
        self.controls.grid_columnconfigure(2, minsize=100) 

        #the score label that will be updated each game loop
        self.scoreStr = tk.StringVar()
        self.scoreLbl = tk.Label(self.controls, textvariable=self.scoreStr,
                                 font=("Arial", 14), width=int(WWIDTH/36))
        self.scoreLbl.grid(row=0, column=0)

        #the lives remaining label
        self.livesStr = tk.StringVar()
        self.livesLbl = tk.Label(self.controls, textvariable=self.livesStr,
                                 font=("Arial", 14), width=int(WWIDTH/36))
        self.livesLbl.grid(row=1, column=0)

    def addScore(self, incr):
        self.score += incr

    def addSpeed(self, incr):
        self.speed += incr

    def addLives(self, incr):
        self.lives += incr

    def createRect(self, X, Y, width, height, fill):
        rect = self.gameCanv.create_rectangle(X, Y, X+width, Y+height,
                                              fill=fill)
        return rect

    def moveRect(self, rect, incrX, incrY):
        self.gameCanv.move(rect, incrX, incrY)
        self.gameCanv.update()

    def suspend(self):
        self.running = False

    def resume(self):
        self.running = True

    def start(self):
        self.score = 0
        self.speed = 1
        self.lives = STARTLIVES
        self.loopNo = 0
        self.running = True

    def close(self):
        self.quit = True

    def flash(self, colour):
        self.gameCanv.config(background=colour)

    def loop(self):
        if self.running:
            self.loopNo += 1
            self.addScore(1)
        self.window.update()
        self.scoreStr.set("Score: %s" % game.score)
        self.livesStr.set("Lives remaining: %s" % game.lives)
        self.flash("white")

#Entity objects for any game entities (player, enemies, pickups)
#addY(x) and addX(x) methods to modify the entity's dimensions
#when initialised the Entity object creates its own rectangle on gameCanv
class Entity:
    def __init__(self, category, game, width, height, X, Y, lane):
        #entities need access to game instance to move rects on canvas
        self.game = game
        
        rectColour = "black" #default if category set incorrectly
        if category == 0: #player 
            rectColour = "green"
        elif category == 1: #pickup
            rectColour = "yellow"
        elif category == 2: #obstacle 
            rectColour = "red"

        #initialise the entity rect with given dimensions
        rect = game.createRect(X, Y, width, height, rectColour)

        self.rect = rect
        self.category = category
        self.height = height
        self.width = width
        self.X = X
        self.Y = Y
        self.lane = lane 
        self.isJump = 0

    def addY(self, incr):
        self.Y += -incr
        game.moveRect(self.rect, 0, -incr) #inverse; screenspace vs gamespace

    def addX (self, incr):
        self.X += incr
        game.moveRect(self.rect, incr, 0) #no need to inverse X-axis

    def reset (self):
        #make entity randomly a pickup or obstacle
        newC = randrange(3) + 1 #2/3 obstacle (2,3), 1/3 pickup (1)
        newFill = "yellow" #default pickup
        
        if newC > 1: #obstacle
            newFill = "red"
            newC = 2 #so that if newC == 3 it's still obstacle
            
        game.gameCanv.itemconfig(self.rect, fill=newFill)
        self.category = newC
        
        rOffset = randrange(80) + 20 #min 20, max 100
        self.addX(WWIDTH + rOffset) #offset ensures reset is off screen

        rLane = randrange(4)
        self.addY((rLane - self.lane) * LHEIGHT)
        self.lane = rLane

    def collidesWith(self, entity):
        if (self.X < entity.X + entity.width and self.X + self.width >
            entity.X and self.lane == entity.lane):
            return True

    def move(self, incr):
        #only if going up and not max lane/going down and not 0
        if not ((incr > 0 and self.lane == LANES-1) or
            (incr < 0 and self.lane == 0)):
            self.lane += incr
            self.addY(incr*LHEIGHT)

def startGame():
    #game loop
    while True:
        if game.running: #check that the game is not over/paused
            #handle game speed increases    
            if game.loopNo % SPEEDINT == 0:
                game.addSpeed(1)

            #handle non-player Entity movement
            for ent in entities:
                ent.addX(-game.speed)

                if ent.X <= 0 - OSIDE:
                    ent.reset()

                if player.collidesWith(ent):
                    if ent.category == 1: #pickup, add score
                        game.flash("yellow")
                        game.addScore(PICKUPVAL)
                    elif ent.category == 2: #obstacle, take life
                        game.flash("red")
                        game.addLives(-1)
                    ent.reset()
                    
            if game.lives <= 0: #if there are no lives remaining, game over
                game.livesStr.set("Game Over")
                game.suspend()
                break

        if game.quit: #if the game has been quit through closing window
            game.window.destroy()
            break

        #general loop events
        game.loop()            
        time.sleep(1/FPS)
    print("game loop terminated")

#initialise Game object
game = Game(STARTLIVES)

#initialise Entity objects
pY = (40 + ((LANES - 1 - 1) * 80)) - (CSIDE / 2)
player = Entity(0, game, CSIDE, CSIDE, CSIDE, pY, 1)

entities = []

for i in range(NUMENTS):
    c = randrange(2) + 1 #category; if 1 then pickup if 2 then obstacle
    l = randrange(LANES) #lane number
    x = 250 + (i * 150)
    y = (40 + ((LANES - 1 - l) * 80)) - (OSIDE / 2)
    
    ent = Entity(c, game, OSIDE, OSIDE, x, y, l)
    entities.append(ent)

#buttons to move player up/down a row
up = tk.Button(game.controls, text=" \u2191 ", font=("Arial", 14),
               command = lambda : player.move(1))
down = tk.Button(game.controls, text=" \u2193 ", font=("Arial", 14),
                 command = lambda : player.move(-1))
up.grid(row=0, column=2)
down.grid(row=1, column=2)

#reset and quit buttons
reset = tk.Button(game.controls, text="Reset", font=("Arial", 12),
                  command = lambda : reset())
reset.grid(row=0, column=4)

def reset():
    game.suspend()
    game.start()

    for ent in entities:
        ent.reset()
    
    startGame()

#pause/resume button
pauseBtn = tk.Button(game.controls, text="Pause", font=("Arial", 12),
                  command = lambda : pause())
resumeBtn = tk.Button(game.controls, text="Resume", font=("Arial", 12),
                   command = lambda : resume())
pauseBtn.grid(row=1, column=4)
resumeBtn.grid(row=1, column=4)
resumeBtn.grid_remove()

def pause():
    game.suspend()
    pauseBtn.grid_remove()
    resumeBtn.grid()

def resume():
    game.resume()
    pauseBtn.grid()
    resumeBtn.grid_remove()

startGame()
game.window.mainloop()
