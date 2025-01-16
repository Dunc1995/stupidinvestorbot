"""Client using the threading API."""

from websockets.sync.client import connect


def send_message():
    with connect("ws://localhost:8765") as websocket:
        websocket.send("Hello world!")
        message = websocket.recv()
        print(message)
