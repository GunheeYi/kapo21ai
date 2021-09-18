# ! Python 3.8 or upper required

from enum import Enum
from random import randint, choice
from time import sleep
from itertools import zip_longest

INTERVAL = 0
DEBUG = False
DRAW = False
TRAINMODE = False

"●○◦⬤◯〇⦿·○〇〇◯ ⃝ ⬤ 🔴🔵〇●○"

class CType(Enum):
    wait = 0
    move = 1
    respawn = 2

class XY:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, xy):
        return self.x==xy.x and self.y==xy.y
    def __add__(self, xy):
        return XY(self.x+xy.x, self.y+xy.y)
    def __sub__(self, xy):
        return XY(self.x-xy.x, self.y-xy.y)
    def __str__(self):
        return "({}, {})".format(str(self.x), str(self.y))

class Dir(Enum):
    up = XY(0, 1)
    down = XY(0, -1)
    left = XY(-1, 0)
    right = XY(1, 0)

def val2xy(val):
    if val == 0: return Dir.up.value
    elif val == 1: return Dir.down.value
    elif val == 2: return Dir.left.value
    elif val == 3: return Dir.right.value
    else: raise ValueError

def xy2str(dir):
    if dir == Dir.up.value: return 'U'
    elif dir == Dir.down.value: return 'D'
    elif dir == Dir.left.value: return 'L'
    elif dir == Dir.right.value: return 'R'
    else: raise ValueError

class Color(Enum):
    black = 30
    red = 31
    green = 32
    yellow = 33
    blue = 34
    magenta = 35
    cyan = 36
    white = 37
    blackk = 90
    redd = 91
    greenn = 92
    yelloww = 93
    bluee = 94
    magentaa = 95
    cyann = 96
    whitee = 97

TEAMS = 2
PLAYERS = 1 if TRAINMODE else 3
LIVES = 1 if TRAINMODE else 4
XLENGTH = 15 if TRAINMODE else 40
YLENGTH = 17 if TRAINMODE else 30
AREA = XLENGTH * YLENGTH
MAXTURN = 300 if TRAINMODE else 600
A = 0
B = 1
COLORA = Color.redd
COLORB = Color.bluee

def norm(a):
    if a > 0: return 1
    elif a < 0: return -1
    elif a == 0: return 0

def name(team):
    if team==A: return 'A'
    elif team==B: return 'B'

def inBoard(xy):
    return xy.x >= 0 and xy.x < XLENGTH and xy.y >= 0 and xy.y < YLENGTH

def other(team):
    if team==A: return B
    elif team==B: return A

def mirror(xy):
    return XY(XLENGTH-xy.x-1, YLENGTH-xy.y-1)

def color(s, c=Color.white, b=Color.white):

    if c==A: c = COLORA
    elif c==B: c = COLORB
    if b==A: b = COLORA
    elif b==B: b = COLORB

    fore = '\033[{}m'.format(str(c.value))
    back = '\033[{}m'.format(str(b.value+10))
    
    return fore + back + s + '\033[0m'

class Map():
    def __init__(self, generator):
        self.map = [[generator() for _ in range(YLENGTH)] for _ in range(XLENGTH)]
    def __iter__(self):
        for x in range(XLENGTH):
            for y in range(YLENGTH):
                yield XY(x, y), self.get(XY(x, y))
    def __str__(self):
        # return '\n'.join(reversed(list(map(lambda line: ''.join(list(map(lambda _: str(_),line))), self.map))))
        return '\n'.join(list(map(lambda line: ''.join(list(map(lambda _: str(_),line))), self.map)))
        # return str(self.map)
    def set(self, a, xy):
        self.map[xy.x][xy.y] = a
    def get(self, xy):
        return self.map[xy.x][xy.y]

class Empty:
    def __str__(self):
        return color(" ")

class Entity:
    def __init__(self, team, id):
        self.team = team
        self.id = id
    def __str__(self):
        return name(self.team)+str(self.id)
    def __repr__(self):
        return self.__str__()

class Piece:
    def __init__(self, team, id, xy=None, dead=False, lives=LIVES):
        self.team = team
        self.id = id
        self.dead = dead
        self.lives = lives
        self.xy = xy
        # self.lastMove = XY((1 if team==A else -1), 0)
    
    def kill(self):
        if self.dead: raise Exception('Piece dead already.')
        self.dead = True
        self.lives -= 1
        self.xy = None
    
    def respawn(self, xy):
        if not self.dead: raise Exception('Piece alive already.')
        if self.lives==0: 
            if DEBUG: print("Invalid action: tried to respawn piece {}{} with no lives left.".format(name(self.team), str(self.id)))
            return
        self.dead = False
        self.xy = xy

    def __eq__(self, p):
        return self.team==p.team and self.id==p.id
    def __ne__(self, p):
        return not self.__eq__(self,p)
    def __lt__(self, p):
        return self.team < p.team or (self.team==p.team and self.id<p.id)
    def __gt__(self, p):
        return self.__ne__(self, p) and not self.__lt__(self, p)

    def __str__(self):
        return color("0", self.team) if self.id else color("O", self.team)

class Dot:
    def __init__(self, team, id):
        self.team = team
        self.id = id

    def __str__(self):
        return color("o", self.team) if self.id else color(".", self.team)

class Camp:
    def __init__(self, team):
        self.team = team

    def __str__(self):
        return color(" ", self.team, self.team)

class Command:
    def __init__(self, team, id, type, xy=None):
        self.team = team
        self.id = id
        self.type = type
        self.xy = (xy.value if isinstance(xy, Dir) else xy)

class Things:
    def __init__(self, cList=[]):
        self.things = [[None for i in range(PLAYERS)] for j in range(TEAMS)]
        for c in cList:
            self.set(c)
    def get(self, thing):
        return self.things[thing.team][thing.id]
    def set(self, thing):
        if thing is None: return
        self.things[thing.team][thing.id] = thing
    def __iter__(self):
        for team in range(TEAMS):
            for id in range(PLAYERS):
                if thing:=self.get(Entity(team, id)):
                    yield thing

class Board:
    def __init__(self):
        self.turn = 0
        self.map = Map(Empty)
        for i in range(4):
            for j in range(3):
                self.set(Camp(A), XY(i,j))
                self.set(Camp(B), mirror(XY(i,j)))
        
        self.pieces = Things([
            Piece(A, 0, XY(3, 2)),
            Piece(B, 0, mirror(XY(3, 2)))
        ]) \
        if TRAINMODE else \
        Things([
            Piece(A, 0, XY(3, 0)),
            Piece(A, 1, XY(2, 2)),
            Piece(A, 2, XY(3, 2)),
            Piece(B, 0, mirror(XY(3, 0))),
            Piece(B, 1, mirror(XY(2, 2))),
            Piece(B, 2, mirror(XY(3, 2)))
        ])

        self.statistics = {
            'died': { A: 0, B: 0 },
            'taken': { A: 0, B: 0 },
            'stepped': {A: 0, B: 0}
        }
    
    def __iter__(self):
        return self.map.__iter__()

    def __str__(self):
        lines = []
        for i in range(XLENGTH):
            line = []
            for j in range(YLENGTH):
                # s += str(i) + ", " +  str(j)
                line += [str(self.get(XY(i,j)))]
            lines += [line]

        for p in self.pieces:
            if not p.dead:
                lines[p.xy.x][p.xy.y] = str(p)

        return '\n'+'\n'.join(list(map(lambda line: ''.join(line), lines)))
    
    def progress(self):
        origin = MAXTURN - 50
        return max(0, (self.turn-origin) / (MAXTURN - origin))

    def set(self, a, xy):
        self.map.set(a, xy)
    
    def get(self, xy):
        return self.map.get(xy)

    def move(self, commands):
        self.turn += 1
        self.reward = [[0 for _ in range(PLAYERS)] for _ in range(TEAMS)]
        # Move and respawn pieces
        for c in commands:
            p = self.pieces.get(c)
            if c.type==CType.wait:
                continue
            if p.dead:
                if c.type==CType.respawn and isinstance(camp:=self.get(c.xy), Camp) and camp.team==p.team:
                    p.respawn(c.xy)
            else:
                if c.type==CType.move:
                    if not isinstance(self.get(p.xy), Camp):
                        self.set(Dot(p.team, p.id), p.xy)
                        self.statistics['stepped'][p.team] += 1
                    p.xy += c.xy
                else:
                    enemyCamp = XY(0,0)
                    if p.team==A: enemyCamp = mirror(enemyCamp)
                    d = enemyCamp - p.xy
                    p.xy += (XY(norm(d.x), 0) if abs(d.x) > abs(d.y) else XY(0, norm(d.y)))
                
        # Detect collisions
        toDie = []
        for p1 in self.pieces:
            if not p1.dead:
                if not inBoard(p1.xy):
                    if DEBUG: print("Adding {} to toDie because it's out of board.".format(str(p1)))
                    toDie += [Entity(p1.team, p1.id)]
                elif isinstance(c:=self.get(p1.xy), Camp):
                    if c.team!=p1.team:
                        toDie += [Entity(p1.team, p1.id)]
                        if DEBUG: print("Adding {} to toDie because it stepped enemy's camp.".format(str(p1)))
                    
                elif isinstance(d:=self.get(p1.xy), Dot):
                    if DEBUG: print("Adding {} to toDie because its dot got stepped.".format(str(p1)))
                    if DEBUG: print("Dot stepped: {}".format(str(p1.xy)))
                    toDie += [Entity(d.team, d.id)]
                    self.statistics['taken'][p1.team] += 1 if p1.team!=d.team else -1
                    self.reward[p1.team][p1.id] += 10 if p1.team!=d.team else -10
                elif isinstance(e:=self.get(p1.xy), Empty):
                    self.reward[p1.team][p1.id] += 3
                    
                
                for p2 in self.pieces:
                    if p1 < p2 and not p2.dead and p1.xy==p2.xy:
                        if DEBUG: print("{}{} and {}{} are in the same position").format(str(p1.team), str(p1.id), str(p2.team), str(p2.id))
                        toDie += [Entity(p1.team, p1.id), Entity(p2.team, p2.id)]
        
        if DEBUG: print(toDie)
        died = []
        for td in toDie:
            if td not in died:
                died += [td]
                self.reward[td.team][td.id] -= 10
                self.pieces.get(td).kill()
                for xy, d in self:
                    if isinstance(d, Dot) and d.team==td.team and d.id==td.id:
                        self.set(Empty(), xy)        
        
        # Make new camps
        for p in self.pieces:
            if not p.dead:
                if isinstance(camp:=self.get(p.xy),Camp):
                    if not camp.team==p.team: raise Exception("Piece is on camp but their teams do not match.")
                    self.fill(p)                
                    
    def fill(self, p):
        self.walls = Map(lambda: False)
        self.checkeds = Map(lambda: False)
        for xy, thing in self:
            if isinstance(thing, Camp) and p.team==thing.team:
                self.walls.set(True, xy)
                self.checkeds.set(True, xy)
            if isinstance(thing, Dot) and p.team==thing.team and p.id==thing.id:
                self.set(Camp(p.team), xy)
                self.walls.set(True, xy)
                self.checkeds.set(True, xy)
        
        for xy, checked in self.checkeds:
            if not checked:
                valid, area = self.expandFrom(xy)
                for newxy in area:
                    # self.checkeds.set(True, newxy)
                    if valid:
                        self.set(Camp(p.team), newxy)
                        self.reward[p.team][p.id] += 5

    def expandFrom(self, xy):
        valid = True
        area = [xy]
        q = [xy]
        while q:
            l = r = q.pop(0)
            if self.checkeds.get(l): continue

            while True: # expand to left
                l += Dir.left.value
                if not inBoard(l):
                    valid = False
                    l -= Dir.left.value
                    break
                if self.walls.get(l):
                    l -= Dir.left.value
                    break
            while True: # expand to right
                r += Dir.right.value
                if not inBoard(r):
                    valid = False
                    r -= Dir.right.value
                    break
                if self.walls.get(r):
                    r -= Dir.right.value
                    break
            
            for x in range(l.x, r.x+1):
                newxy = XY(x, l.y)
                self.checkeds.set(True, newxy)
                area += [XY(x, l.y)]
                
                for dir in [Dir.up, Dir.down]:
                    u = newxy + dir.value
                    if not inBoard(u):
                        valid=False
                        break
                    if not self.walls.get(u):
                        q.append(u)
        
        return valid, area
    
    def winner(self):
        camps = { A:0, B:0 }

        for i in range(XLENGTH):
            for j in range(YLENGTH):
                if isinstance(c:=self.get(XY(i,j)), Camp):
                    camps[c.team] += 1
        diff = abs(camps[A]-camps[B])/AREA

        # print(self.turn, camps)

        for team, count in camps.items():
            if count >= AREA/2: return (team, diff)
        
        alive = { A:False, B: False }
        for p in self.pieces:
            if p.lives > 0:
                alive[p.team] = True
        if not alive[A]: return (B, 0.25)
        if not alive[B]: return (A, 0.25)
        
        if self.turn >= MAXTURN:
            return (A, diff) if camps[A] > camps[B] else (B, diff)

        return None




# board = Board()

# commands = Things([
#     Command(A, 0, Dir.up),
#     Command(A, 1, Dir.up),
#     Command(A, 2, Dir.up),
#     Command(B, 0, Dir.up),
#     Command(B, 1, Dir.up),
#     Command(B, 2, Dir.up)
# ])



# # commandsList = [
#         #         Things([Command(A, 2, CType.move, XY(1,0))]),
#         #         Things([Command(A, 2, CType.move, XY(1,0))]),
#         #         Things([Command(A, 2, CType.move, XY(0,1))]),
#         #         Things([Command(A, 2, CType.move, XY(0,1))]),
#         #         Things([Command(A, 2, CType.move, XY(-1,0))]),
#         #         Things([Command(A, 2, CType.move, XY(-1,0))]),
#         #         Things([Command(A, 2, CType.move, XY(0,-1))]),
#         #         Things([Command(A, 2, CType.move, XY(-1,0))]),
#         #         Things([Command(A, 2, CType.move, XY(-1,0))]),
#         # ]

#         # commandsList = \
#         #     [Things([Command(A, 2, CType.move, XY(1,0))])]*32 \
#         #     + [Things([Command(A, 2, CType.move, XY(0,1))])]*28 \
#         #     + [Things([Command(A, 2, CType.move, XY(-1,0))])]*32 \
#         #     + [Things([Command(A, 2, CType.move, XY(0,-1))])]*28 \
        
#         a0 = \
#             [Command(A, 0, CType.move, XY(1,0))]*35 \
                
#         a1 = \
#             [Command(A, 1, CType.move, XY(0,1))]*23 \
#             + [Command(A, 1, CType.move, XY(-1,0))]*2 \
#             + [Command(A, 1, CType.move, XY(0,-1))]*20 \

#         a2 = \
#             [Command(A, 2, CType.move, XY(1,0))]*27 \
#             + [Command(A, 2, CType.move, XY(0,1))]*24 \
#             + [Command(A, 2, CType.move, XY(-1,0))]*27 \
#             + [Command(A, 2, CType.move, XY(0,-1))]*24 \
        
#         b0 = \
#             [Command(B, 0, CType.move, XY(-1,0))]*34 \
#             + [Command(B, 0, CType.move, XY(0,-1))]*27 \

#         b1 = \
#             [Command(B, 1, CType.move, XY(0,-1))]*10 \
#             + [Command(B, 1, CType.move, XY(-1,0))]*5 \
#             + [Command(B, 1, CType.move, XY(0,-1))]*20 \
        
#         b2 = []
#         # b2 = \
#         #     [Things([Command(B, 2, CType.move, XY(1,0))])]*32 \
#         #     + [Things([Command(B, 2, CType.move, XY(0,1))])]*28 \
#         #     + [Things([Command(B, 2, CType.move, XY(-1,0))])]*32 \
#         #     + [Things([Command(B, 2, CType.move, XY(0,-1))])]*28 \

# commandsList = list(map(Things, zip_longest(a0, a1, a2, b0, b1, b2)))


        # if draw: print(self)
        # for commands in commandsList:
        #     if commands is not None:
        #         if interval: sleep(interval)
        #         if debug: print("Turn {}".format(str(self.turn)))
        #         self.move(commands)
        #         if draw: print(self)
        #         winner = self.winner()
        #         if self.winner() is not None:
        #             if debug: print("Team {} won!".format(name(winner)))
        #             break