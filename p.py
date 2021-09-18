import socket

IP = "172.30.1.42"
portnum = 9999

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((IP, portnum))

socket.send('POSTECH$1234/'.encode("utf-16"))

while True:
    data = socket.recv(10240).decode("utf-16")
    print("server message : ", data)

    payload = ""

    if data=="GameStart/":
        payload = "Init$0,1$1,1$2,1$/"
    if data=="TurnStart/":
        # payload = "Move$0$R/Move$1$R/Move$2$R/"
        payload = "asdfasdfasdfsa"
    
    if data=="GameOver":
        print("Game Over.")
        break
    
    if payload:
        socket.send(payload.encode("utf-16"))

socket.close()

