import socket
import json
import threading
import time

client = socket.socket()


def connect(server_ip, server_port):
    client.connect((server_ip, int(server_port)))
    threading.Thread(target=recv_thread).start()


wait_call = None
use_wait = False


def send_msg(msg, wait=False):
    global wait_call, use_wait
    if (wait):
        wait_call = None
        use_wait = True
    msg = (json.dumps(msg)).encode("utf-8")
    client.sendall(len(msg).to_bytes(4, "big")+(msg[::-1]))
    if (wait):
        while wait_call is None:
            time.sleep(0.01)
        return wait_call


def recv_thread():
    global wait_call, use_wait
    try:
        while 1:
            resp_len = int.from_bytes(client.recv(4), "big")
            response = client.recv(resp_len)[::-1].decode('utf-8')
            if (response is None):
                break
            if (use_wait):
                wait_call = json.loads(response)
                use_wait = False
    finally:
        client.close()
