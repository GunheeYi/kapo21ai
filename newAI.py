from board import *
from random import sample

def turnLeft(dir):
    if dir==Dir.left: return Dir.down
    elif dir==Dir.down: return Dir.right
    elif dir==Dir.right: return Dir.up
    elif dir==Dir.up: return Dir.left

LIMIT = 10

class LeftHanded:
    def __init__(self, team=B):
        self.dir = [Dir.left, Dir.down, Dir.down]
        self.limit = [LIMIT, LIMIT, LIMIT]
        self.team = team
    
    def call(self, board):
        deads = []
        data = ""
        for id in range(3):
            if not board.pieces.get(Entity(self.team, id)).dead:
                xy = board.pieces.get(Entity(self.team, id)).xy

                dirSet = False
                for dirr in Dir:
                    newxy = xy + dirr.value
                    if inBoard(newxy) and isinstance(d:=board.get(newxy), Dot) and d.team!=self.team:
                        self.dir[id] = dirr
                        dirSet = True
                        break
                if dirSet: continue

                newxy = xy + self.dir[id].value
                
                if not inBoard(newxy) or (isinstance(d:=board.get(newxy), Dot) and d.team==self.team ) or self.limit[id]<=0:
                    self.limit[id] = 3
                    self.dir[id] = turnLeft(self.dir[id])
                    continue
                else: 
                    self.limit[id] -= 1
                    self.dir[id] = self.dir[id]
                    continue
                
                # if isinstance(c:=board.get(newxy), Camp) and c.team==self.team:
            else: 
                deads += [id]
        
        for id in range(3):
            if id not in deads:
                data += "Move${}${}/".format(str(id), xy2str(self.dir[id].value))

        if deads:
            borderXYs = []
            for xy, e in board:
                if isinstance(e, Camp) and e.team==self.team:
                    campNext = emptyNext = False
                    for dir in Dir:
                        if not inBoard(xy+dir.value): continue
                        eNext = board.get(xy + dir.value)
                        if isinstance(eNext, Camp) and eNext.team==self.team:
                            campNext = True
                        elif isinstance(eNext, Empty):
                            emptyNext = True
                    if campNext and emptyNext:
                        borderXYs += [xy]
            
            xys = list(map(lambda i: borderXYs[i], sample(range(0, len(borderXYs)), len(deads))))
            for xy in xys:
                id = deads.pop()
                data += "Respawn${}${},{}/".format(str(id), str(xy.x), str(xy.y))
        
        return data