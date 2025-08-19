from random import randint
import heapq
import time

colorsT = (color(150,100,50),color(50,50,200),color(100,50,25),color(50,200,50),color(100,100,100)) #dirt,water,dug dirt,grass,stone
StatusType = [2,3,6,2,-6]
settingColor = (color(150,100,50),color(100,100,100))
G1 = None
setting = 1
TIME =  None

grassGrowTime = 5
waterFillTime = 10
digCooldown = 30.0

class baseEnemy:
    def __init__(self,x,y,type,BSx,BSy,HP,sz):
        self.x = x
        self.y = y
        self.sz = sz
        self.type = type
        self.frontTiles = []
        self.onTiles = []
        self.baseSpeed = [-BSx,-BSy]
        self.dimensions = [-1,-1,-1,-1]
        self.hp = HP
        self.collDir = -1
        self.collMoDir = 0 
    
    def update(self,x,y,rows,cols,sz): #just draws itself
        self.updateOnTiles(x,y,cols,rows,sz)
        fill(255,0,0,50)
        stroke(255)
        strokeWeight(1)
        square(self.x+x+(sz-self.sz)/2,self.y+y+(sz-self.sz)/2,self.sz)
        circle(self.x+x,self.y+y,3)
    
    def updateOnTiles(self,x,y,cols,rows,sz):
        #print("UT")
        dimensions = [-1,-1,-1,-1]
        dimensions[0] = max(int((self.x+(sz-self.sz)/2)// sz), 0) #left
        dimensions[1] = min(int((self.x+(sz-self.sz)/2 + self.sz) // sz), cols - 1) #right
        dimensions[2] = max(int((self.y+(sz-self.sz)/2) // sz), 0) #top
        dimensions[3] = min(int((self.y+(sz-self.sz)/2 + self.sz) // sz), rows - 1) #bottom
        
        #print(dimensions)
        if (dimensions[2] != self.dimensions[2] or dimensions[3] != self.dimensions[3]): #different top or bot
            for r in range(self.dimensions[2], self.dimensions[3] + 1):
                if r >= 0:
                    G1.rowEnemyList[r].remove(self)
            for r in range(dimensions[2], dimensions[3] + 1):
                G1.rowEnemyList[r].append(self)
                
        if (self.collDir != -1):
            print(self.collDir)
            collSides = [(0,-1),
                        (-1,0),    (1,0),
                              (0,1) ]
            sides = [(0,1,2,1,0),
            (2,3,0,0,1),     (2,3,1,0,1),
                    (0,1,3,1,0)] #along one side, to another, on this side, x side?, y side?
            sideStatus = True #can walk past
            for i in range(dimensions[sides[self.collDir][0]],dimensions[sides[self.collDir][1]]+1):
                if (dimensions[sides[self.collDir][2]]*sides[self.collDir][4] < cols-1 and dimensions[sides[self.collDir][2]]*sides[self.collDir][3] < rows-1):
                    collisionTile = [i*sides[self.collDir][3]+dimensions[sides[self.collDir][2]]*sides[self.collDir][4]+collSides[self.collDir][0],
                                     i*sides[self.collDir][4]+dimensions[sides[self.collDir][2]]*sides[self.collDir][3]+collSides[self.collDir][1]]
                    if (G1.getTile(collisionTile[0],collisionTile[1]).status < 0): #if can't walk
                        sideStatus = False
                        break
            if (sideStatus):
                self.collDir = -1
                self.collMoDir = 0
        
        if (dimensions != self.dimensions):
            
            sides = [(0,1,2,1,0),
            (2,3,0,0,1),     (2,3,1,0,1),
                    (0,1,3,1,0)] #along one side, to another, on this side, x side?, y side?
            for k in range(0,4):
                for i in range(dimensions[sides[k][0]],dimensions[sides[k][1]]+1):
                    #print("D",i,i*sides[k][3],dimensions[sides[k][2]]*sides[k][4],i*sides[k][4],dimensions[sides[k][2]]*sides[k][3])
                    if (dimensions[sides[k][2]]*sides[k][4] < cols-1 and dimensions[sides[k][2]]*sides[k][3] < rows-1):
                        collisionTile = [i*sides[k][3]+dimensions[sides[k][2]]*sides[k][4],i*sides[k][4]+dimensions[sides[k][2]]*sides[k][3]]
                        if (G1.getTile(collisionTile[0],collisionTile[1]).status < 0): #if can't walk on
                            #self.baseSpeed = [0,0] #pretty much all collisions will full stop...
                            print(abs(collisionTile[0]*sz-self.x),abs(collisionTile[1]*sz-self.y))
                            if (abs(collisionTile[0]*sz-self.x) > abs(collisionTile[1]*sz-self.y)):
                                if (collisionTile[0]*sz < self.x): #right side
                                    self.collDir = 1
                                    self.collMoDir = -1 if self.baseSpeed[1]<0 else (1 if self.baseSpeed[1]>0 else randint(0,1)*2-1)
                                    self.x = collisionTile[0]*sz+(sz/2+self.sz/2)
                                else: #left side
                                    self.collDir = 2
                                    self.collMoDir = -1 if self.baseSpeed[1]<0 else (1 if self.baseSpeed[1]>0 else randint(0,1)*2-1)
                                    self.x = collisionTile[0]*sz-(sz/2+self.sz/2)
                            else: 
                                if (collisionTile[1]*sz < self.y): #bot side
                                    self.collDir = 0
                                    self.collMoDir = -1 if self.baseSpeed[0]<0 else (1 if self.baseSpeed[0]>0 else randint(0,1)*2-1)
                                    self.y = collisionTile[1]*sz+(sz/2+self.sz/2)
                                else: #top side
                                    self.collDir = 3
                                    self.collMoDir = -1 if self.baseSpeed[0]<0 else (1 if self.baseSpeed[0]>0 else randint(0,1)*2-1)
                                    self.y = collisionTile[1]*sz-(sz/2+self.sz/2)
                                    
                                    
                                
            
            self.dimensions = dimensions
            for t in self.onTiles:
                t.enemyContactNum -= 1
                t.enemyContactList.remove(self)
            self.onTiles = []
            for r in range(dimensions[2], dimensions[3] + 1):
                for c in range(dimensions[0], dimensions[1] + 1):
                    self.onTiles.append(G1.getTile(c,r))
            for t in self.onTiles:
                t.enemyContactNum += 1
                t.enemyContactList.append(self)
                #print t.enemyContactNum 
    
    def destructor(self):
        for t in self.onTiles:
            t.enemyContactNum -= 1
            t.enemyContactList.remove(self)
        self.baseSpeed = [0,0]

class Tile:
    def __init__(self,type):
        self.type = type #tile type
        self.placed = 0 #-1 means can't be placed on #0 things are not placed on it #x ID something is placed on it
        self.status = StatusType[type] #postive = things can walk on, negative = things can't #even = things can be placed on it, 0 means does not exist #mult of 3 means can't dig 
        self.enemyContactList = []
        self.enemyContactNum = 0

class PriorityQueue:
    def __init__(self):
        self._queue = []  # list of entries arranged in a heap
        self._index = 0   # tie-breaker for items with the same priority

    def push(self, item, priority):
        # Using a tuple: (priority, index, item)
        # Lower priority numbers come out first
        heapq.heappush(self._queue, (priority, self._index, item))
        self._index += 1

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from an empty priority queue")
        return heapq.heappop(self._queue)[-1]  # return only the item

    def peek(self):
        if self.is_empty():
            return None
        return self._queue[0]

    def is_empty(self):
        return len(self._queue) == 0

    def __len__(self):
        return len(self._queue)


class Game:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.cols = 0
        self.rows = 0
        self.sz = None
        self.grid = []
        self.changeQueue = PriorityQueue()
        self.T = -1
        self.digTimer = 0
        self.rowEnemyList = []
        self.allEnemies = []
    
    def makeGrid(self,wide,high,sz):
        self.sz = sz
        self.rows = floor(high/sz)
        self.cols = floor(wide/sz)
        for y in range(self.rows):
            self.rowEnemyList.append([])
        for x in range(self.cols):
            tmpGrid = []
            for y in range(self.rows):
                if x == 0:
                    tmpGrid.append(Tile(1))
                else:
                    tmpGrid.append(Tile(0))
            self.grid.append(tmpGrid)
        for x in range(self.cols):
            for y in range(self.rows):
                self.waterChecks(x,y)
    
    def update(self):
        self.T += 1
        textSize(20)
        for r in range (self.rows):
            fill(200,100,0)
            text(len(self.rowEnemyList[r]),self.x+self.cols*self.sz,self.y+r*self.sz+self.sz)
        while (not self.changeQueue.is_empty()and (self.changeQueue.peek())[0] == self.T):
            tmp = self.changeQueue.pop()
            self.grid[tmp[0]][tmp[1]].type = tmp[2]
            self.grid[tmp[0]][tmp[1]].status = StatusType[tmp[2]]
            self.waterChecks(tmp[0],tmp[1])
        for x in range(self.cols):
            for y in range(self.rows):
                if (self.grid[x][y].type != None):
                    stroke(0)
                    strokeWeight(1)
                    #if (self.grid[x][y].enemyContactNum > 0):
                    #    strokeWeight(3)
                    #    stroke(255,0,0)
                    fill(colorsT[self.grid[x][y].type])
                    square(self.x+x*self.sz,self.y+y*self.sz,self.sz)
                    stroke(255)
                    circle(self.x+x*self.sz,self.y+y*self.sz,5)
                    fill(0)
                    #text(self.grid[x][y].enemyContactNum,self.x+x*self.sz,self.y+y*self.sz+self.sz)
        
        for x in range(self.cols):
            for y in range(self.rows):
                if (self.grid[x][y].type != None):
                    if (self.grid[x][y].enemyContactNum > 0):
                        strokeWeight(1.5+self.grid[x][y].enemyContactNum)
                        stroke(255,0,0)
                        noFill()
                        square(self.x+x*self.sz,self.y+y*self.sz,self.sz)
                        fill(0)
                        text(self.grid[x][y].enemyContactNum,self.x+x*self.sz,self.y+y*self.sz+self.sz)
    
    def playerUpdates(self):
        self.digTimer -= 1
        if (self.digTimer <= 0):
            self.digTimer = 0
        if (mouseX >= self.x) and (mouseX <= self.x+self.cols*self.sz):
            if (mouseY >= self.y) and (mouseY <= self.y+self.rows*self.sz):
                
                xT = int(map(mouseX,self.x,self.x+self.cols*self.sz,0,self.cols))
                yT = int(map(mouseY,self.y,self.y+self.rows*self.sz,0,self.rows))
                stroke(255)
                strokeWeight(2)
                noFill()
                square(self.x+xT*self.sz,self.y+yT*self.sz,self.sz)
                strokeWeight(1)
                if mousePressed and self.digTimer <= 0:
                    #print("Press")
                    if setting == 1:
                        if (self.grid[xT][yT].status%3 != 0):
                            #print("Dig")
                            self.digTimer = digCooldown
                            self.grid[xT][yT].type = 2
                            self.grid[xT][yT].status = StatusType[2]
                            self.waterSelfCheck(xT,yT)
                    if setting == 2:
                        if (self.grid[xT][yT].status%3 != 0):
                            #print("Stone")
                            #self.digTimer = digCooldown
                            self.grid[xT][yT].type = 4
                            self.grid[xT][yT].status = StatusType[4]
                
                fill(0)
                strokeWeight(1)
                stroke(0)
                rect(mouseX-5,mouseY-5,10,10*(self.digTimer/digCooldown))
                
                strokeWeight(2)
                if (setting <= 2):
                    stroke(settingColor[setting-1])
                else:
                    stroke(0)
                fill(255)
                if (self.digTimer/digCooldown == 0):
                    fill(0,200,0)
                rect(mouseX-5,mouseY+5,10,-10*(1-self.digTimer/digCooldown))
        
    def waterSelfCheck(self,x,y):
        if(self.grid[x][y].type == 2):
            if(x>0):
                if(self.grid[x-1][y].type == 1):
                    self.changeQueue.push((x,y,1),priority = self.T+waterFillTime)
            if(y>0):
                if(self.grid[x][y-1].type == 1):
                    self.changeQueue.push((x,y,1),priority = self.T+waterFillTime)
            if (x<self.cols-1):
                if(self.grid[x+1][y].type == 1):
                    self.changeQueue.push((x,y,1),priority = self.T+waterFillTime)
            if (y<self.rows-1):
                if(self.grid[x][y+1].type == 1):
                    self.changeQueue.push((x,y,1),priority = self.T+waterFillTime)
    
    def waterChecks(self,x,y):
        if(self.grid[x][y].type == 1):
            directions = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1)
            ]
            cardinal_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.cols and 0 <= ny < self.rows:
                    if self.grid[nx][ny].type == 0:
                        self.changeQueue.push((nx,ny,3),priority = self.T+grassGrowTime)
            for dx, dy in cardinal_dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.cols and 0 <= ny < self.rows:
                    if self.grid[nx][ny].type == 2:
                        self.changeQueue.push((nx,ny,1),priority = self.T+waterFillTime)
    
    def updateEnemies(self):
        for enemy in self.allEnemies:
            #if (self.grid[enemy.baseSpeed[0]/abs(enemy.baseSpeed[0])][enemy.baseSpeed[1]/abs(enemy.baseSpeed[1])]):
            if enemy.collDir == -1:
                enemy.x  += enemy.baseSpeed[0]
                enemy.y  += enemy.baseSpeed[1]
            else:
                collSides = [(1,0),
                        (0,1),    (0,1),
                              (1,0) ]
                eSpeed = int(sqrt(enemy.baseSpeed[0]**2+enemy.baseSpeed[1]**2))
                enemy.x += collSides[enemy.collDir][0]*enemy.collMoDir*eSpeed
                enemy.y += collSides[enemy.collDir][1]*enemy.collMoDir*eSpeed
            enemy.update(self.x,self.y,self.rows,self.cols,self.sz)
            self.enemyDeathCheck(enemy)
    
    def spawnEnemy(self):
        #print("Spawn Enemy")
        tmpEnemy = baseEnemy(self.cols*self.sz,randint(0,self.rows-1)*self.sz,0,5,randint(0,4)//4*(randint(0,1)*2-1)/2.0,100,self.sz*randint(2,8)/4) #x,y,t,speedx,speedy,hp,sz
        self.allEnemies.append(tmpEnemy)
        #tmpEnemy = baseEnemy(randint(0,self.cols-1)*self.sz,self.rows*self.sz,0,randint(0,4)//4*(randint(0,1)*2-1)/2.0,5,100,self.sz/2) #x,y,t,speed,speedy,hp,sz
        #self.allEnemies.append(tmpEnemy)
        #tmpEnemy = baseEnemy(0,randint(0,self.rows-1)*self.sz,0,-5,randint(0,4)//4*(randint(0,1)*2-1)/2.0,100,self.sz*randint(2,8)/4) #x,y,t,speedx,speedy,hp,sz
        #self.allEnemies.append(tmpEnemy)
        
    def enemyDeathCheck(self,enemy):
        #print("EDC")
        if enemy.x < -self.sz or enemy.x > self.cols*self.sz+self.sz or enemy.y < -self.sz or enemy.y > self.rows*self.sz+self.sz or enemy.hp <= 0:
            for t in enemy.onTiles:
                t.enemyContactNum -= 1
                t.enemyContactList.remove(enemy)
            for r in range(enemy.dimensions[2], enemy.dimensions[3] + 1):
                if r >= 0:
                    self.rowEnemyList[r].remove(enemy)
            self.allEnemies.remove(enemy)
    
    def getTile(self,x,y):
        return self.grid[x][y]
        
        
def setup():
    global G1, colorsT, TIME, StatusType
    size(1600,900)
    #noStroke()
    TIME = time.time()
    print("Init Grid")
    G1 = Game(100,50) #offsets on x and y
    print("Make Grid")
    G1.makeGrid(1200,800,80) #length, width, size
    print("Type Grid")
    frameRate(30)
    print(time.time()-TIME)
    TIME = time.time()
    

def draw():
    global G1, colorsT, TIME, StatusType
    background(0)
    
    #TIME = time.time()
    textSize(20)
    fill(0,255,0)
    if (time.time()-TIME < 0.005):
        fill(255,0,0)
    text(time.time()-TIME,0,20)
    text(frameRate,0,40)
    
    G1.update()
    G1.playerUpdates()
    G1.updateEnemies()

    TIME = time.time()

def keyReleased():
    global setting
    if key == "0":
        #print("Spawn Enemy")
        G1.spawnEnemy()
    if key == "1":
        setting = 1
    if key == "2":
        setting = 2
    if key == "3":
        setting = 3
    
