import logging
import socket
import threading
from typing import List, Dict, Callable, Any

from pydantic import BaseModel, ValidationError

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def add(a: int, b: int) -> int:
    return a + b


def sub(a: int, b: int) -> int:
    return a - b


def upper(s: str) -> str:
    return s.upper()


class Model(BaseModel):
    def bytes(self) -> bytes:
        return self.json().encode("utf-8")


class RPCRequest(Model):
    method: str
    args: list = None
    kwargs: dict = None


class RPCResponse(Model):
    result: Any


class RPCError(Model):
    message: List[Dict[str, Any]]


class ServerHandler:
    def __init__(self) -> None:
        self._functions = {}

    def register_function(self, func: Callable) -> None:
        self._functions[func.__name__] = func

    def handle_connection(self, conn: socket.socket) -> None:
        while True:
            payload = conn.recv(1024)
            if not payload:
                break

            try:
                request = RPCRequest.parse_raw(payload)
            except ValidationError as err:
                self._send(conn, RPCError(message=err.errors()))
                continue

            if request.method not in self._functions:
                err = RPCError(
                    message=[{
                        "method": request.method,
                        "msg": "unknown method to call",
                    }]
                )
                self._send(conn, err)
                continue

            args, kwargs = tuple(), {}
            if request.args:
                args = request.args
            if request.kwargs:
                kwargs = request.kwargs

            try:
                result = self._functions[request.method](*args, **kwargs)
            except Exception as exc:
                logging.exception(exc)

                err = RPCError(message=[{"msg": str(exc)}])
                self._send(conn, err)
                continue

            self._send(conn, RPCResponse(result=result))

        conn.close()

    @staticmethod
    def _send(conn: socket.socket, model: Model) -> None:
        payload = model.bytes() + b"\r\n"
        conn.sendall(payload)


def start_server(host: str, port: int, handler: ServerHandler) -> None:
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(1)

    log.info(f"Server started at {host}:{port}")

    try:
        while True:
            conn, address = sock.accept()
            thread = threading.Thread(target=handler.handle_connection, args=(conn,), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        log.info("Server shutdown")


if __name__ == "__main__":
    hdl = ServerHandler()
    hdl.register_function(add)
    hdl.register_function(sub)
    hdl.register_function(upper)

    start_server(host="127.0.0.1", port=8000, handler=hdl)
