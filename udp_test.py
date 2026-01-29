import socket
import time

SERVER_IP = "192.168.3.40"  # ← A 机 IP
SERVER_PORT = 8001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(3)

def send(msg):
    print("->", msg)
    sock.sendto(msg.encode("utf-8"), (SERVER_IP, SERVER_PORT))

    try:
        while True:
            data, addr = sock.recvfrom(4096)
            print("<-", data.decode("utf-8"), "from", addr)
    except socket.timeout:
        pass

send("PING")
time.sleep(0.5)
send("RUN")
time.sleep(5)
send("RUN")   # 如果 exe 还在跑，应该 BUSY
time.sleep(10)
send("RUN")   # 如果 exe 还在跑，应该 BUSY
time.sleep(30)
send("RUN")   # 如果 exe 还在跑，应该 BUSY
time.sleep(10)
send("RUN")   # 如果 exe 还在跑，应该 BUSY
time.sleep(0.5)
send("RUN")   # 如果 exe 还在跑，应该 BUSY

sock.close()
