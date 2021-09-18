from os import PathLike
from board import *
from random import sample

import torch
import torch.nn as nn
import torch.nn.functional as F

cuda_ok = torch.cuda.is_available()
test = not __file__ in ['ai1.py', 'ai2.py'] and __name__ == "__main__"

DEVICE = 'cpu'
RANGE = 10
E2E = RANGE*2 + 1

def around(a):
    return list(range(a-RANGE, a+RANGE+1))

class KaPo21Net(nn.Module):
    # input: teamCamp, myPath, team, teamPath, enemyCamp, enemy, enemyPath, outBoard, turn
    def __init__(self, size=E2E):
        self.size = size
        
        super(KaPo21Net, self).__init__()
        self.conv1a = nn.Conv2d(9, 8, kernel_size=3, padding=1, bias=False)
        self.conv1b = nn.Conv2d(9, 4, kernel_size=5, padding=2, bias=False)
        self.conv1c = nn.Conv2d(9, 2, kernel_size=7, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(16)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(16, 3, kernel_size=1, bias=False)
        self.bn2 = nn.BatchNorm2d(3)
        self.lnr = nn.Linear(3*self.size*self.size, 4)
        
    def forward(self, x):
        x = x.view(-1, 9, self.size, self.size)
        xa = self.relu(self.conv1a(x))
        xb = self.relu(self.conv1b(x))
        xc = self.relu(self.conv1b(x))
        x = torch.cat((xa, xb, xc), dim=1)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu(x)
        x = x.view(-1, 3*self.size*self.size)
        x = self.lnr(x)
        
        return F.softmax(x, dim=1)

class Player():
    def __init__(self, team, net, use_gpu=False):
        self.team = team
        self.net = net
        self.gpu = use_gpu
        if self.gpu:
            self.net.cuda()
        self.net.eval()

    def call(self, board:Board):
        pieces = []
        deads = []
        for p in board.pieces:
            if p.team == self.team:
                if p.dead:
                    if p.lives > 0: deads += [p]
                else:
                    pieces += [p]
        commands = []
        for p in pieces:
            turn = [[board.progress()] * E2E] * E2E
            teamCamp = [[0 for _ in range(E2E)] for _ in range(E2E)]
            myPath = [[0 for _ in range(E2E)] for _ in range(E2E)]
            team = [[0 for _ in range(E2E)] for _ in range(E2E)]
            teamPath = [[0 for _ in range(E2E)] for _ in range(E2E)]
            enemyCamp = [[0 for _ in range(E2E)] for _ in range(E2E)]
            enemy = [[0 for _ in range(E2E)] for _ in range(E2E)]
            enemyPath = [[0 for _ in range(E2E)] for _ in range(E2E)]
            outBoard = [[0 for _ in range(E2E)] for _ in range(E2E)]
            for x in around(p.xy.x):
                for y in around(p.xy.y):
                    origin = p.xy - XY(RANGE,RANGE)
                    raw = XY(x,y)
                    trans = raw - origin
                    # print("Origin: {}, raw: {}, trans: {}".format(str(origin), str(raw), str(trans)))
                    if inBoard(raw):
                        e = board.get(raw)
                        if isinstance(e, Camp):
                            if e.team == p.team:
                                teamCamp[trans.x][trans.y] = 1
                            else:
                                enemyCamp[trans.x][trans.y] = 1
                        elif isinstance(e, Piece):
                            if e.team == p.team:
                                team[trans.x][trans.y] = 1
                            else:
                                enemy[trans.x][trans.y] = 1
                        elif isinstance(e, Dot):
                            if e.team == p.team:
                                if e.id == p.id:
                                    myPath[trans.x][trans.y] = 1
                                    teamCamp[trans.x][trans.y] = 1
                                else:
                                    teamPath[trans.x][trans.y] = 1
                            else:
                                enemyPath[trans.x][trans.y] = 1

                    else:
                        outBoard[trans.x][trans.y] = 1
            inputt = torch.tensor([teamCamp, myPath, team, teamPath, enemyCamp, enemy, enemyPath, outBoard, turn], dtype=torch.float)
            if self.gpu:
                inputt = inputt.to('cuda')
            with torch.no_grad():
                probs = self.net(inputt)
            if self.gpu:
                probs = probs.cpu()
            dirXY = val2xy(torch.argmax(probs))
            commands += [Command(p.team, p.id, CType.move, dirXY)]
        
        if deads:
            borderXYs = []
            for xy, e in board:
                if isinstance(e, Camp) and e.team==self.team:
                    campNext = emptyNext = False
                    for dir in Dir:
                        eNext = board.get(xy + dir.value)
                        if isinstance(eNext, Camp) and eNext.team==self.team:
                            campNext = True
                        elif isinstance(eNext, Empty):
                            emptyNext = True
                    if campNext and emptyNext:
                        borderXYs += [xy]
            

            for d in deads:
                if not borderXYs: break
            
            xys = list(map(lambda i: borderXYs[i], sample(range(0, len(borderXYs)), len(deads))))
            for xy in xys:
                d = deads.pop()
                commands += [Command(d.team, d.id, CType.respawn, xy)]
                        
        return commands
    