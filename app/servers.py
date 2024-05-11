import os
import socket
import concurrent.futures
from abc import ABC, abstractmethod
from app.http_utils import HttpVersion, HttpRequest, HttpResponse, HttpResponseStatus, HttpMethod


class Server(ABC):

    def __init__(self, host, port, args):
        self.host = host
        self.port = port
        self.args = args

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


class HttpServer(Server):

    def handle_connection(self, connection_socket: socket):

        with connection_socket:
            # Fetch data and create the HttpRequest
            data = connection_socket.recv(1024*1000*5)
            request = HttpRequest.from_bytes(data)

            # Construct the response
            if request.target.startswith('/echo/'):

                response_status = HttpResponseStatus.OK
                body_string = request.target.removeprefix('/echo/')
                response_body = body_string.encode('utf-8')
                response_headers = {'Content-Type': 'text/plain', 'Content-Length': str(len(body_string))}

            elif request.target == '/user-agent':

                response_status = HttpResponseStatus.OK
                body_string = request.headers['User-Agent']
                response_body = body_string.encode('utf-8')
                response_headers = {'Content-Type': 'text/plain', 'Content-Length': str(len(body_string))}

            elif request.method == HttpMethod.GET and request.target.startswith('/files/'):

                file_name = request.target.removeprefix('/files/')
                file_path = os.path.join(self.args[2], file_name)

                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        data = f.read()

                    response_status = HttpResponseStatus.OK
                    response_body = data
                    response_headers = {'Content-Type': 'application/octet-stream',
                                        'Content-Length': str(len(response_body))}

                else:
                    response_status = HttpResponseStatus.NOT_FOUND
                    response_headers = {}
                    response_body = b''

            elif request.method == HttpMethod.POST and request.target.startswith('/files/'):

                file_name = request.target.removeprefix('/files/')
                file_path = os.path.join(self.args[2], file_name)

                with open(file_path, 'wb') as f:
                    f.write(request.body)

                response_status = HttpResponseStatus.CREATED
                response_headers = {}
                response_body = b''

            elif request.target == '/':
                response_status = HttpResponseStatus.OK
                response_headers = {}
                response_body = b''

            else:
                response_status = HttpResponseStatus.NOT_FOUND
                response_headers = {}
                response_body = b''

            response = HttpResponse(HttpVersion.HTTP11, response_status, response_headers, response_body)

            # To simulate a delay
            # time.sleep(5)

            # Send response
            connection_socket.send(response.to_bytes())

            # Debugging
            print(f'Request line - http_method: {request.method}')
            print(f'Request line - request_target: {request.target}')
            print(f'Request line - http_version: {request.version}{os.linesep}')
            print(f'Complete request: {os.linesep}{request}')
            print(f'Response: {os.linesep}{response}')
