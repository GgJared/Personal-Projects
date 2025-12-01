from collections import deque
from random import randint
import heapq

"""
touch the end tile or be directly on the tile? Probably Touch end tiles
"""
sz = 40
maxDirs = 8 
UpPace = 10 #how many frames before new pace
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
set1Remove = set()
set2Remove = set()
paused = False
setting = 1
t = 0

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
        elif y == height/sz-1:
            self.borderNeighborNum += (8+16+32)
        if x == 0: 
            self.borderNeighborNum += ~self.borderNeighborNum & (32+64+128)
        elif x == width/sz-1:
            self.borderNeighborNum += ~self.borderNeighborNum & (2+4+8)
        #print(x,y,self.borderNeighborNum)
        #"""
        if type == 0:
            #self.rtgrStat += 2+8+32+128
            self.rtgrStat += 1+4+16+64
            endNodes.append((x,y))
    
    def update(self):
        colorMode(RGB)
        stroke(0)
        strokeWeight(1)
        fill(colTypes[self.type])
        square(self.x*sz,self.y*sz,sz)
        """
        if (self.neighborNum != 4096):
            fill(255,255,255)
            textSize(sz/4)
            text(self.neighborNum,self.x*sz,self.y*sz+sz/2)"""

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
                tmpGrid.append(Tile(x,y,randint(0,4)//4 + 1))
                #tmpGrid.append(Tile(x,y,1))
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
                    #print(i,x,y,x+dirs8List[i][0],y+dirs8List[i][1],grid[x][y].borderNeighborNum,(1<<i))
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
                #print(tmpNumDir,(neighborNum & tmpNumDir) , ((neighborNum & tmpNumDir*2)) , (not(neighborNum & tmpNumDir/2)))
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

    
def rowConnectedRemove(dir,x,y):
    leftNumDir = tileRotate(dir,-2)
    rightNumDir = tileRotate(dir,2)
    backNumDir = tileRotate(dir,4)
    left = [x,y]
    neighborNumLeft = neighborIntCheck(x,y)
    right = [x,y]
    neighborNumRight = neighborIntCheck(x,y)
    leftDone = False
    rightDone = False
    altConnection = False
    while (not altConnection and (not leftDone or not rightDone)):
        if (grid[right[0]][right[1]].type == 0):
            altConnection = True
            return
        if (grid[left[0]][left[1]].type == 0):
            altConnection = True
            return
        if (neighborNumRight&(1<<rightNumDir)):
            if (grid[right[0]+dirs8List[rightNumDir][0]][right[1]+dirs8List[rightNumDir][1]].rtgrStat&(1<<dir)):
                right[0] += dirs8List[rightNumDir][0]
                right[1] += dirs8List[rightNumDir][1]
                neighborNumRight = neighborIntCheck(right[0],right[1])
                if (neighborNumRight&(1<<backNumDir)):
                    if (grid[right[0]+dirs8List[backNumDir][0]][right[1]+dirs8List[backNumDir][1]].rtgrStat&(1<<dir)):
                        altConnection = True
                        return
            else:
                rightDone = True
        else:
            rightDone = True
        if (neighborNumLeft&(1<<leftNumDir)):
            if (grid[left[0]+dirs8List[leftNumDir][0]][left[1]+dirs8List[leftNumDir][1]].rtgrStat&(1<<dir)):
                left[0] += dirs8List[leftNumDir][0]
                left[1] += dirs8List[leftNumDir][1]
                neighborNumLeft = neighborIntCheck(left[0],left[1])
                if (neighborNumLeft&(1<<backNumDir)):
                    if (grid[left[0]+dirs8List[backNumDir][0]][left[1]+dirs8List[backNumDir][1]].rtgrStat&(1<<dir)):
                        altConnection = True
                        return
            else:
                leftDone = True
        else:
            leftDone = True
    
    if (grid[right[0]][right[1]].type == 0):
        altConnection = True
        return
    if (grid[left[0]][left[1]].type == 0):
        altConnection = True
        return
    
    if (altConnection == False):
        #print("Alt Connections False",left,right)
        for xT in range(min(left[0],right[0]),max(left[0],right[0])+1):
            for yT in range(min(left[1],right[1]),max(left[1],right[1])+1):
                #print("Test", dir,xT,yT,1<<dir)
                if (grid[xT][yT].rtgrStat&(1<<dir)):
                    #print("Remove", dir,xT,yT,1<<dir)
                    grid[xT][yT].rtgrStat -= 1<<dir
                    if (neighborIntCheck(xT,yT)&(1<<dir)):
                        if(grid[xT+dirs8List[dir][0]][yT+dirs8List[dir][1]].rtgrStat&(1<<dir)):
                            set2Remove.add((xT+dirs8List[dir][0],yT+dirs8List[dir][1]))
    else:
        #print("Alt Connections True",left,right)
        pass
            
        
def RTGRAnalysisTileRemove(x,y):#
    neighborNum = neighborIntCheck(x,y)
    for i in range(maxDirs):
        if (i%2 == 0):#cardinal
            if ((grid[x][y].rtgrStat>>(i))&1): 
                if (neighborNum&tileRotateInt(i,4)):
                    if (grid[x+dirs8List[tileRotate(i,4)][0]][y+dirs8List[tileRotate(i,4)][1]].type == 1):
                        if (not grid[x+dirs8List[tileRotate(i,4)][0]][y+dirs8List[tileRotate(i,4)][1]].rtgrStat&(1<<i)):
                            if (grid[x][y].rtgrStat&(1<<i) and grid[x][y].type != 0):
                                #print("Remove Only Me", i,x,y,1<<i)
                                grid[x][y].rtgrStat -= 1<<i
                                if (neighborNum&tileRotateInt(i,-2)):
                                    if(grid[x+dirs8List[tileRotate(i,-2)][0]][y+dirs8List[tileRotate(i,-2)][1]].rtgrStat&(1<<i)):
                                        set2Remove.add((x+dirs8List[tileRotate(i,-2)][0],y+dirs8List[tileRotate(i,-2)][1]))
                                if (neighborNum&tileRotateInt(i,2)):
                                    if(grid[x+dirs8List[tileRotate(i,2)][0]][y+dirs8List[tileRotate(i,2)][1]].rtgrStat&(1<<i)):
                                        set2Remove.add((x+dirs8List[tileRotate(i,2)][0],y+dirs8List[tileRotate(i,2)][1]))
                                if (neighborNum&(1<<i)):
                                    if(grid[x+dirs8List[i][0]][y+dirs8List[i][1]].rtgrStat&(1<<i)):
                                        set2Remove.add((x+dirs8List[i][0],y+dirs8List[i][1]))
                    else:
                        rowConnectedRemove(i,x,y)
                else:
                    rowConnectedRemove(i,x,y)
        else:#diagonals
            if ((grid[x][y].rtgrStat>>(i))&1):
                #print(neighborNum,tileRotateInt(i,-3),i,x,y)
                if (not neighborNum&tileRotateInt(i,4)):
                    if(neighborNum&tileRotateInt(i,-3)):
                        if(grid[x+dirs8List[tileRotate(i,-3)][0]][y+dirs8List[tileRotate(i,-3)][1]].rtgrStat&(1<<i)):
                            continue
                    if(neighborNum&tileRotateInt(i,3)):
                        if(grid[x+dirs8List[tileRotate(i,3)][0]][y+dirs8List[tileRotate(i,3)][1]].rtgrStat&(1<<i)):
                            continue
                if (grid[x][y].type == 0):
                    continue
                if ((not neighborNum&tileRotateInt(i,3)) and neighborNum&tileRotateInt(i,-3)):
                    if(grid[x+dirs8List[tileRotate(i,-3)][0]][y+dirs8List[tileRotate(i,-3)][1]].rtgrStat&(1<<i)):
                        continue
                        
                if ((not neighborNum&tileRotateInt(i,-3)) and neighborNum&tileRotateInt(i,3)):
                    if(grid[x+dirs8List[tileRotate(i,3)][0]][y+dirs8List[tileRotate(i,3)][1]].rtgrStat&(1<<i)):
                        continue
                
                if (neighborNum&tileRotateInt(i,-3) and neighborNum&tileRotateInt(i,3) and neighborNum&tileRotateInt(i,4)):
                    if(grid[x+dirs8List[tileRotate(i,4)][0]][y+dirs8List[tileRotate(i,4)][1]].rtgrStat&(1<<i)):
                        continue
                if (grid[x][y].rtgrStat&(1<<i)):
                    grid[x][y].rtgrStat -= 1<<i
                    if (neighborNum&tileRotateInt(i,1)):
                        if(grid[x+dirs8List[tileRotate(i,1)][0]][y+dirs8List[tileRotate(i,1)][1]].rtgrStat&(1<<i)):
                            set2Remove.add((x+dirs8List[tileRotate(i,1)][0],y+dirs8List[tileRotate(i,1)][1]))
                    if (neighborNum&tileRotateInt(i,-1)):
                        if(grid[x+dirs8List[tileRotate(i,-1)][0]][y+dirs8List[tileRotate(i,-1)][1]].rtgrStat&(1<<i)):
                            set2Remove.add((x+dirs8List[tileRotate(i,-1)][0],y+dirs8List[tileRotate(i,-1)][1]))
                    if (neighborNum&(1<<i)):
                        if(grid[x+dirs8List[i][0]][y+dirs8List[i][1]].rtgrStat&(1<<i)):
                            set2Remove.add((x+dirs8List[i][0],y+dirs8List[i][1]))
                    
                        
            
"""
def RTGRAnalysis(): #kind of like BFS with more complex rules
    queueTiles = deque()
    for t in endNodes:
        queueTiles.append(t)
    while(not queueTiles):
        currentTile = queueTiles.popleft()
        RTGRAnalysisTile(currentTile[0],currentTile[1])
"""

def RTGRAnalysis_SingleSetStep():
    global set2, set2Remove
    set1 = set2
    set1Remove = set2Remove
    if (len(set1) != 0 or len(set1Remove) != 0):
        print
    if (len(set1) != 0):
        print"--RTGR-AL SSS", set1
    if (len(set1Remove) != 0):
        print"-RTGR-AL-RM SSS", set1Remove
    set2 = set()
    set2Remove = set()
    for tile in set1Remove:
        RTGRAnalysisTileRemove(tile[0],tile[1])
    for tile in set1:
        RTGRAnalysisTile(tile[0],tile[1])

def setup():
    global Grid,set1,set2
    size(800,800)
    genGrid()
    for tile in endNodes:
        set2.add((tile[0],tile[1]))
    frameRate(30)


def draw():
    global t
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
    if (not paused):
        if (t%UpPace == 0):
            RTGRAnalysis_SingleSetStep()
    else:
        noStroke()
        fill(255,0,0,75)
        circle(sz,sz,sz*2)
    for x,y in set2Remove:
        colorMode(RGB)
        stroke(0)
        strokeWeight(1)
        fill(255,0,0,50)
        square(x*sz,y*sz,sz)
    for x,y in set2:
        colorMode(RGB)
        stroke(0)
        strokeWeight(1)
        fill(255,255,0,50)
        square(x*sz,y*sz,sz)
    for R in grid:
        for T in R:
            if T.rtgrStat != 0:
                arrows(T.x,T.y,sz,sz/4,T.rtgrStat,50)
    fill(colTypes[setting],75)
    square(mouseX-5,mouseY-5,sz/2)
    t += 1

#def mouseMoved():

def mouseReleased():
    xT = int(map(mouseX,0,width,0,width/sz))
    yT = int(map(mouseY,0,height,0,height/sz))
    grid[xT][yT].type = setting
    grid[xT][yT].rtgrStat = 0
    if (grid[xT][yT].borderNeighborNum): #if it is on the border
        for i in range(maxDirs):
            if (not 1<<i & grid[xT][yT].borderNeighborNum):
                if (grid[xT+dirs8List[i][0]][yT+dirs8List[i][1]].rtgrStat != 0):
                    set2.add((xT+dirs8List[i][0],yT+dirs8List[i][1]))
                    set2Remove.add((xT+dirs8List[i][0],yT+dirs8List[i][1]))
                if (grid[xT+dirs8List[i][0]][yT+dirs8List[i][1]].neighborNum != 4096):
                    if (setting == 2):
                        if (grid[xT+dirs8List[i][0]][yT+dirs8List[i][1]].neighborNum & tileRotateInt(i,4)):
                            grid[xT+dirs8List[i][0]][yT+dirs8List[i][1]].neighborNum -= tileRotateInt(i,4)
                    else:
                        if (not grid[xT+dirs8List[i][0]][yT+dirs8List[i][1]].neighborNum & tileRotateInt(i,4)):
                            grid[xT+dirs8List[i][0]][yT+dirs8List[i][1]].neighborNum += tileRotateInt(i,4)
    else:
        for i in range(maxDirs):
            if (grid[xT+dirs8List[i][0]][yT+dirs8List[i][1]].rtgrStat != 0):
                set2.add((xT+dirs8List[i][0],yT+dirs8List[i][1]))
                set2Remove.add((xT+dirs8List[i][0],yT+dirs8List[i][1]))
            if (grid[xT+dirs8List[i][0]][yT+dirs8List[i][1]].neighborNum != 4096):
                if (setting == 2):
                    if (grid[xT+dirs8List[i][0]][yT+dirs8List[i][1]].neighborNum & tileRotateInt(i,4)):
                        grid[xT+dirs8List[i][0]][yT+dirs8List[i][1]].neighborNum -= tileRotateInt(i,4)
                else:
                    if (not grid[xT+dirs8List[i][0]][yT+dirs8List[i][1]].neighborNum & tileRotateInt(i,4)):
                        grid[xT+dirs8List[i][0]][yT+dirs8List[i][1]].neighborNum += tileRotateInt(i,4)
        
            
                
    
def keyReleased():
    global paused, setting
    if key == " ":
        paused = not paused
    if key == "1":
        setting = 1
    if key == "2":
        setting = 2
    if key == "0":
        setting = 0
