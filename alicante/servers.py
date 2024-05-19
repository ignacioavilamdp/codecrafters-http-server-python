import os
import re
import socket
import concurrent.futures
from typing import Callable
from abc import ABC, abstractmethod
from alicante.http import HttpVersion, HttpRequest, HttpResponse, HttpResponseStatus, HttpMethod


class Server(ABC):

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def run(self):
        # Creates the server socket
        with socket.create_server((self.host, self.port), reuse_port=False) as server_socket:
            print(f"Server running and accepting connections at {self.host}:{self.port}{os.linesep}")

            # Main loop for incoming connections
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                while True:
                    (connection_socket, connection_adress) = server_socket.accept()  # wait for client connection
                    print(f'Connection stablished with {connection_adress[0]}:{connection_adress[1]}{os.linesep}')

                    executor.submit(self.handle_connection, connection_socket)

    @abstractmethod
    def handle_connection(self, connection_socket: socket):
        raise NotImplementedError("handle_connection() must be implemented")


class AlicanteServer(Server):

    def __init__(self, host, port):
        super().__init__(host, port)
        self.pattern_handlers = dict()
        self.resource_directory = None

    def handle_connection(self, connection_socket: socket):

        with connection_socket:
            # Fetch data and create the HttpRequest
            data = connection_socket.recv(1024*1000*5)
            request = HttpRequest.from_bytes(data)

            # Construct the response
            response = self.handle_request(request)

            # To simulate a delay
            # time.sleep(5)

            # Send response
            connection_socket.send(response.to_bytes())

    def handle_request(self, request: HttpRequest) -> HttpResponse:

        for (method, regex_pattern), handler in self.pattern_handlers.items():
            if method == request.method:
                m = re.match(regex_pattern, request.target)
                if m and m.group() == request.target:
                    kwargs = m.groupdict()
                    return handler(request, **kwargs)

        return self.default_handler()

    def route(self, route_pattern: str, method: HttpMethod):

        def wrapper(handler: Callable[[HttpRequest], HttpResponse]):
            self.add_handler(route_pattern, method, handler)
            return handler

        return wrapper

    def add_handler(self, route_pattern: str, method: HttpMethod, handler: Callable[[HttpRequest], HttpResponse]):

        regex_pattern = self.get_regex_pattern(route_pattern)
        key = (method, regex_pattern)
        if key in self.pattern_handlers:
            raise Exception('Method/Request pair already mapped')
        self.pattern_handlers[key] = handler

    def get_regex_pattern(self, route_pattern: str) -> str:
        tokens = re.split(r'<(.*?)>', route_pattern)
        var_names = tokens[1::2]
        tokens[1::2] = [rf'(?P<{name}>\S*)' for name in var_names]
        return ''.join(tokens)

    def default_handler(self) -> HttpResponse:
        return HttpResponse(HttpVersion.HTTP11, HttpResponseStatus.NOT_FOUND, {}, b'')
