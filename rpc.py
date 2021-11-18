import socket
from typing import Callable


def add(a: int, b: int) -> int:
    return a + b


def sub(a: int, b: int) -> int:
    return a - b


def upper(s: str) -> str:
    return s.upper()


class ServerHandler:
    def __init__(self) -> None:
        pass

    def register_function(self, func: Callable) -> None:
        pass

    def handle_connection(self, conn: socket.socket) -> None:
        pass


def start_server(host: str, port: int, handler: ServerHandler) -> None:
    pass


if __name__ == "__main__":
    hdl = ServerHandler()
    hdl.register_function(add)
    hdl.register_function(sub)
    hdl.register_function(upper)

    start_server(host="127.0.0.1", port=8000, handler=hdl)
