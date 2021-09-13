# socket module import!
import socket

# socket create and connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("123.123.123.123", 9999))

# send msg
test_msg = "안녕하세요 상대방님"
sock.send(test_msg)

# recv data
data_size = 512
data = sock.recv(data_size)

# connection close
sock.close()




import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
recv_address = ('0.0.0.0', 9999)
sock.bind(recv_address)

sock.listen(1)
 
conn, addr = sock.accept()

# recv and send loop
while 1:
    data = conn.recv(BUFFER_SIZE)
    # 받고 data를 돌려줌.
    conn.send(data)

conn.close()