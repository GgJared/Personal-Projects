from collections import deque
from random import randint
import heapq

"""
touch the end tile or be directly on the tile? Probably Touch end tiles
"""
sz = 20
maxDirs = 8 
colTypes = (color(50,200,50),color(200,200,200),color(10,10,10)) #RGB
dirs8List = [
                 (0,-1),
                 (1,-1),(1,0),(1,1),
                 (0,1),
                 (-1,1),(-1,0),(-1,-1)]

grid = []
endNodes = []
set1 = set()
set2 = set()

class Tile:
    def __init__(self,x,y,type):
        self.x = x
        self.y = y
        self.sz = sz
        self.type = type
        self.rtgrStat = 0
        self.borderNeighborNum = 0
        self.neighborNum = 4096
        #"""
        if y == 0: 
            self.borderNeighborNum += (1+2+128)
        elif y == width/sz-1:
            self.borderNeighborNum += (8+16+32)
        if x == 0: 
            self.borderNeighborNum += ~self.borderNeighborNum & (32+64+128)
        elif x == height/sz-1:
            self.borderNeighborNum += ~self.borderNeighborNum & (2+4+8)
        print(x,y,self.borderNeighborNum)
        #"""
        if type == 0:
            self.rtgrStat = 255
            endNodes.append((x,y))
    
    def update(self):
        colorMode(RGB)
        stroke(0)
        strokeWeight(1)
        fill(colTypes[self.type])
        square(self.x*sz,self.y*sz,sz)

def genGrid():
    #4 loops?
    
    for x in range(height/sz):
        tmpGrid = []
        for y in range(width/sz):
            #if x == width/sz/2 and abs(y-height/sz/2) == 0:
            #    tmpGrid.append(Tile(x,y,0))
            if x == width/sz/2 and abs(y-height/sz/2)+5 <= 10:
                tmpGrid.append(Tile(x,y,0))
            else:
                tmpGrid.append(Tile(x,y,randint(0,4)//4+1))
        grid.append(tmpGrid)

def arrows(x,y,inSZ,arrowSZ,dirs,ALP): #inefficient, decode is better
    colorMode(HSB,255,255,255,100)
    #ALP = 70
    strokeWeight(2)
    for i in range(maxDirs):
        #print(i, dirs)
        if ((dirs>>i) &1):
            stroke(i*(255//maxDirs),255,255,ALP)
            fill(i*(255//maxDirs),255,255,ALP)
            line(sz/2+x*inSZ,inSZ/2+y*inSZ,inSZ/2+x*inSZ+arrowSZ*dirs8List[i][0],inSZ/2+y*inSZ+arrowSZ*dirs8List[i][1])
            stroke(i*(255//maxDirs),255,255,ALP)
            circle(inSZ/2+x*inSZ+arrowSZ*dirs8List[i][0],inSZ/2+y*inSZ+arrowSZ*dirs8List[i][1],4)

def neighborIntCheck(x,y):#might be less efficient than just having specific rules for each direction #outputs 255 if all neighbors are empty
    neighborNum = 0
    if (grid[x][y].neighborNum == 4096): #if the current grid value already has one
        for i in range(maxDirs):
            #print(i,neighborNum,tmpTile.type)
            if (grid[x][y].borderNeighborNum): #if it is on the border
                if (not((1<<i) & grid[x][y].borderNeighborNum)):
                    print(i,x,y,x+dirs8List[i][0],y+dirs8List[i][1],grid[x][y].borderNeighborNum,(1<<i))
                    tmpTile = grid[x+dirs8List[i][0]][y+dirs8List[i][1]]
                    if (tmpTile.type != 2):
                        neighborNum += (1<<i)
            else:
                tmpTile = grid[x+dirs8List[i][0]][y+dirs8List[i][1]]
                if (tmpTile.type != 2): #if it is empty
                    neighborNum += (1<<i)
        grid[x][y].neighborNum = neighborNum
        return neighborNum
    return grid[x][y].neighborNum

def tileRotate(current,rotation): #takes in one of the 8 cardinal directions from 0 to 7 the rotated one from 0 to 7
    return (current+rotation)%maxDirs
def tileRotateInt(current,rotation): #takes in one of the 8 cardinal directions from 0 to 7 and outputs the rotated one from 0 to 255
    return 1<<((current+rotation)%maxDirs)

def RTGRAnalysisTile(x,y):#
    #print(x,y, "RTGR-AT")
    neighborNum = neighborIntCheck(x,y)
    for i in range(maxDirs):
        if (i%2 == 0):#cardinal
            if ((grid[x][y].rtgrStat>>(i))&1): 
                #print(i, "CD")
                tmpNumDir = 1<<(i)
                if (neighborNum & tmpNumDir): #front
                    currTile = grid[x+dirs8List[i][0]][y+dirs8List[i][1]]
                    if (not currTile.rtgrStat & tmpNumDir):
                        #print(i,"ADD-RTGR F")
                        currTile.rtgrStat += tmpNumDir
                        set2.add((currTile.x,currTile.y))
                        #...
                if (not neighborNum & tileRotateInt(i,3)):#sides
                    currTileOffset = tileRotate(i,2)
                    currTile = grid[x+dirs8List[currTileOffset][0]][y+dirs8List[currTileOffset][1]]
                    if (neighborNum & 1<<currTileOffset):
                        if (not currTile.rtgrStat & tmpNumDir):
                            #print(i,"ADD-RTGR S")
                            currTile.rtgrStat += tmpNumDir
                            set2.add((currTile.x,currTile.y))
                            #...
                if (not neighborNum & tileRotateInt(i,-3)):#sides
                    currTileOffset = tileRotate(i,-2)
                    currTile = grid[x+dirs8List[currTileOffset][0]][y+dirs8List[currTileOffset][1]]
                    if (neighborNum & 1<<currTileOffset):
                        if (not currTile.rtgrStat & tmpNumDir):
                            #print(i,"ADD-RTGR S")
                            currTile.rtgrStat += tmpNumDir
                            set2.add((currTile.x,currTile.y))
                            #...
                            
        else:
            if ((grid[x][y].rtgrStat>>(i))&1): 
                tmpNumDir = 1<<(i)
                #which diagonal
                print(tmpNumDir,(neighborNum & tmpNumDir) , ((neighborNum & tmpNumDir*2)) , (not(neighborNum & tmpNumDir/2)))
                if ((neighborNum & tmpNumDir) and (neighborNum & tileRotateInt(i,1)) and (neighborNum & tileRotateInt(i,-1))):#corner
                    currTileOffset = (i)%maxDirs
                    currTile = grid[x+dirs8List[currTileOffset][0]][y+dirs8List[currTileOffset][1]]
                    if (not currTile.rtgrStat & tmpNumDir):
                        #print(i,"ADD-RTGR S")
                        currTile.rtgrStat += tmpNumDir
                        set2.add((currTile.x,currTile.y))
                if ((neighborNum & tileRotateInt(i,1)) and (not neighborNum & tileRotateInt(i,2) or not neighborNum & tileRotateInt(i,3))):#side clockwise
                    currTileOffset = tileRotate(i,1)
                    currTile = grid[x+dirs8List[currTileOffset][0]][y+dirs8List[currTileOffset][1]]
                    if (not currTile.rtgrStat & tmpNumDir):
                        #print(i,"ADD-RTGR S")
                        currTile.rtgrStat += tmpNumDir
                        set2.add((currTile.x,currTile.y))
                        #...
                if ((neighborNum & tileRotateInt(i,-1)) and (not neighborNum & tileRotateInt(i,-2) or not neighborNum & tileRotateInt(i,-3))):#side counterclockwise
                    currTileOffset = tileRotate(i,-1)
                    currTile = grid[x+dirs8List[currTileOffset][0]][y+dirs8List[currTileOffset][1]]
                    if (not currTile.rtgrStat & tmpNumDir):
                        #print(i,"ADD-RTGR S")
                        currTile.rtgrStat += tmpNumDir
                        set2.add((currTile.x,currTile.y))
                        #...
            

    
    #3 ifs in cardinal directions
    #2 ifs in diaginal directions
            
        
def RTGRAnalysis(): #kind of like BFS with more complex rules
    queueTiles = deque()
    for t in endNodes:
        queueTiles.append(t)
    while(not queueTiles):
        currentTile = queueTiles.popleft()
        RTGRAnalysisTile(currentTile[0],currentTile[1])


def RTGRAnalysis_SingleSetStep():
    global set2
    set1 = set2
    print("RTGR-AL SSS", set1)
    set2 = set()
    for t in set1:
        RTGRAnalysisTile(t[0],t[1])

def setup():
    global Grid,set1,set2
    size(800,800)
    genGrid()
    for t in endNodes:
        set2.add((t[0],t[1]))
    frameRate(2)


def draw():
    background(255)
    for R in grid:
        for T in R:
            T.update()
    #print(neighborIntCheck(width/sz/2,height/sz/2))
    #RTGAnalysisTiles(width/sz/2,height/sz/2)
    #for R in grid:
    #    for T in R:
    #        if T.type == 0:
    #            arrows(T.x,T.y,sz,sz,T.neighborNum,10)
    RTGRAnalysis_SingleSetStep()
    for R in grid:
        for T in R:
            if T.rtgrStat != 0:
                arrows(T.x,T.y,sz,sz/4,T.rtgrStat,50)
    #noLoop()
    
