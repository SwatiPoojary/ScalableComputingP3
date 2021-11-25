#!/usr/bin/env python3

import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()
selClient = selectors.DefaultSelector()
# messages = [b"Message 1 from client.", b"Message 2 from client."]
messages = [b"I am Client."]

clientPorts = 0
HOST = '10.35.70.19'
# HOST = '10.6.43.151'
PORT = 34000
Client_Port = 34001

def start_connections(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, Client_Port))
    sock.listen()
    print('Listening on', (HOST, Client_Port))
    sock.setblocking(False)
    sel.register(sock, events=selectors.EVENT_READ, data=None)

    server_addr = (host, port)
    print("starting connection", "to", server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(
        connid=1,
        msg_total=sum(len(m) for m in messages),
        recv_total=0,
        messages=list(messages),
        outb=b"",
    )
    sel.register(sock, events, data=data)
    clientPorts = sock.getsockname()[1]




def service_connection(key, mask):
    sock = key.fileobj

    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print("received", repr(recv_data), "from connection", data.connid)
            data.recv_total += len(recv_data)
        # if not recv_data or data.recv_total == data.msg_total:
        #     print("closing connection", data.connid)
        #     sel.unregister(sock)
        #     sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print("sending", repr(data.outb), "to connection", data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


start_connections(HOST, PORT)

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()

