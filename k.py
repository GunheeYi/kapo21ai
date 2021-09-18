import socket
from board import *
from newAI import *

POSTECH = False

FRIEND = A if POSTECH else B
ENEMY = other(FRIEND)
PROFILE = 'POSTECH$1234/' if POSTECH else 'KAIST$5678/'

IP = "172.30.1.42"
portnum = 9999

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((IP, portnum))

socket.send(PROFILE.encode("utf-16"))

player = LeftHanded()

waiting = True

while True: 
    data = socket.recv(10240).decode("utf-16")
    print("server message : ", data)

    payload = ""

    if "GameStart" in data:
        payload = "Init$36,29$36,27$38,27$/"
    if "TurnStart" in data and waiting:
        payload = "Move$0$L/Move$1$L/Move$2$L/"
        waiting = False
    if any(info in data for info in ["Friendly_Unit", "Enemy_Unit", "Friendly_Line", "Enemy_Line", "Friendly_Area", "Enemy_Area"]):
        board = Board()
        infos = data.split("/")
        infos = list(map(lambda a: a.split("$"), infos))
        for info in infos:
            infoType = info[0]
            content = list(map(lambda a: a.split(','), info[1:]))
            if infoType in ["Friendly_Unit", "Enemy_Unit"]:
                friendly = infoType=="Friendly_Unit"
                for id, c in enumerate(content):
                    if c and len(c)==3: board.pieces.set(Piece(FRIEND if friendly else ENEMY, id + (0 if friendly else 1), XY(int(c[1]),int(c[2])), c[0]=='D'))
            elif infoType in ["Friendly_Line", "Enemy_Line"]:
                team = FRIEND if infoType=="Friendly_Line" else ENEMY
                contentt = []
                for c in content:
                    if len(c)>=2:
                        contentt += [XY(int(c[0]),int(c[1]))]
                if contentt:
                    board.set(Dot(team,contentt[0]), contentt[0])
                    for i, xy1 in enumerate(contentt[:-2]):
                        xy2 = contentt[i+1]
                        if xy1.x == xy2.x:
                            small = min([xy1.y, xy2.y])
                            big = max([xy1.y, xy2.y])
                            for y in range(small, big+1):
                                board.set(Dot(team, id), XY(xy1.x, y))
                        elif xy1.y == xy2.y:
                            small = min([xy1.x, xy2.x])
                            big = max([xy1.x, xy2.x])
                            for x in range(small, big+1):
                                board.set(Dot(team, id), XY(x, xy1.y))
            elif infoType in ["Friendly_Area", "Enemy_Area"]:
                for c in content:
                    if len(c)>=2: board.set(Camp(FRIEND if infoType=="Friendly_Area" else ENEMY), XY(int(c[0]),int(c[1])))
            payload = player.call(board)

    if data in "TurnTimeOut":
        waiting = True
    
    if "GameOver" in data:
        print("Game Over.")
        break
    
    if payload:
        socket.send(payload.encode("utf-16"))
        print("Sent message: " + payload)

socket.close()

