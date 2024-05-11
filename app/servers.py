import os
import socket
import concurrent.futures
from abc import ABC, abstractmethod
from app.http_utils import HttpVersion, HttpRequest, HttpResponse, HttpResponseStatus


class Server(ABC):

    def __init__(self, host, port, args):
        self.host = host
        self.port = port
        self.args = args

    def run(self):
        # Creates a server socket, binds it to host and port and accept connections (using socket.create_server() is easier)
        with socket.socket() as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
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


class HttpServer(Server):

    def handle_connection(self, connection_socket: socket):

        with connection_socket:
            # Fetch data and create the HttpRequest
            data = connection_socket.recv(1024)
            http_request = HttpRequest.from_bytes(data)

            # Construct the response
            if http_request.request_target.startswith('/echo/'):

                http_response_status = HttpResponseStatus.OK
                body_string = http_request.request_target.removeprefix('/echo/')
                body = body_string.encode('utf-8')
                headers = {'Content-Type': 'text/plain', 'Content-Length': str(len(body_string))}

            elif http_request.request_target == '/user-agent':

                http_response_status = HttpResponseStatus.OK
                body_string = http_request.headers['User-Agent']
                body = body_string.encode('utf-8')
                headers = {'Content-Type': 'text/plain', 'Content-Length': str(len(body_string))}

            elif http_request.request_target.startswith('/files/'):

                file_name = http_request.request_target.removeprefix('/files/')

                option = self.args[1]
                directory_path = self.args[2]
                file_path = os.path.join(directory_path, file_name)

                print(file_path)

                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        data = f.read()

                    http_response_status = HttpResponseStatus.OK
                    body = data
                    headers = {'Content-Type': 'application/octet-stream',
                               'Content-Length': str(len(body))} #, 'Content-Length': str(len(body))}

                else:
                    http_response_status = HttpResponseStatus.NOT_FOUND
                    headers = {}
                    body = b''

            elif http_request.request_target == '/':
                http_response_status = HttpResponseStatus.OK
                headers = {}
                body = b''

            else:
                http_response_status = HttpResponseStatus.NOT_FOUND
                headers = {}
                body = b''

            http_response = HttpResponse(HttpVersion.HTTP11, http_response_status, headers, body)

            # To simulate a delay
            # time.sleep(5)

            # Send response
            connection_socket.send(http_response.to_bytes())

            # Debugging
            print(f'Request line - http_method: {http_request.http_method}')
            print(f'Request line - request_target: {http_request.request_target}')
            print(f'Request line - http_version: {http_request.http_version}{os.linesep}')
            print(f'Complete request: {os.linesep}{http_request}')
            print(f'Response: {os.linesep}{http_response}')
