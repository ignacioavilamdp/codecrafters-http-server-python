import os
import re
import socket
import concurrent.futures
from typing import Callable
from abc import ABC, abstractmethod
from alicante.http import HttpVersion, HttpRequest, HttpResponse, HttpResponseStatus, HttpMethod
from alicante.router import RouteHandler


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
        self.route_handlers = set()
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

        for route_handler in self.route_handlers:
            kwargs = route_handler.match(request)
            if kwargs:
                return route_handler.handler(request, **kwargs)

        return self.default_handler()

    def route(self, route_pattern: str, method: HttpMethod):

        def wrapper(handler: Callable[[HttpRequest], HttpResponse]):
            self.add_route_handler(RouteHandler(route_pattern, method, handler))
            return handler

        return wrapper

    def add_route_handler(self, route_handler: RouteHandler):
        if route_handler in self.route_handlers:
            raise Exception('Route handler already included in the server')
        self.route_handlers.add(route_handler)

    def default_handler(self) -> HttpResponse:
        return HttpResponse(HttpVersion.HTTP11, HttpResponseStatus.NOT_FOUND, {}, b'')
