import concurrent.futures
import os
import socket
import time
from enum import Enum

CRLF = '\r\n'

HOST = "localhost"
PORT = 4221


class HttpVersion(Enum):
    HTTP10 = 'HTTP/1.0'
    HTTP11 = 'HTTP/1.1'


class HttpMethod(Enum):
    CONNECT = 'CONNECT'
    DELETE = 'DELETE'
    GET = 'GET'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    PATCH = 'PATCH'
    POST = 'POST'
    PUT = 'PUT'
    TRACE = 'TRACE'


class HttpResponseStatus(Enum):
    OK = (200, 'OK')
    BAD_REQUEST = (400, 'Bad Request')
    UNAUTHORIZED = (401, 'Unauthorized')
    FORBIDDEN = (403, 'Forbidden')
    NOT_FOUND = (404, 'Not found')

    def __init__(self, status_code, status_text):
        self.status_code = status_code
        self.status_text = status_text


class HttpRequest:

    def __init__(self, http_method: HttpMethod, request_target: str, http_version: HttpVersion, headers: dict[str, str],
                 body: str):
        self.http_method = http_method
        self.request_target = request_target
        self.http_version = http_version
        self.headers = headers
        self.body = body

    def __str__(self):
        request_line = f'{self.http_method.value} {self.request_target} {self.http_version.value}'
        headers_list = [f'{key}: {value}' for (key, value) in self.headers.items()]
        return CRLF.join([request_line, CRLF.join(headers_list), '', self.body])

    @staticmethod
    def from_string(request_string: str):
        request_line, *headers_list, empty_line, body = request_string.split(CRLF)
        http_method_name, request_target, http_version_name = request_line.split(' ')

        headers = dict()
        for header in headers_list:
            key, sep, value = header.partition(':')
            headers[key] = value.strip()

        return HttpRequest(HttpMethod(http_method_name), request_target, HttpVersion(http_version_name), headers, body)

    @staticmethod
    def from_bytes(request_bytes: bytes):
        return HttpRequest.from_string(request_bytes.decode(encoding='utf-8'))


class HttpResponse:
    def __init__(self, http_version: HttpVersion, response_status: HttpResponseStatus, headers: dict[str, str],
                 body: str):
        self.http_version = http_version
        self.response_status = response_status
        self.headers = headers
        self.body = body

    def __str__(self):
        status_line = f'{self.http_version.value} {self.response_status.status_code} {self.response_status.status_text}'
        headers_list = [f'{key}: {value}' for (key, value) in self.headers.items()]
        return CRLF.join([status_line, CRLF.join(headers_list), '', self.body])

    def to_bytes(self):
        return str(self).encode('utf-8')


def handle_connection(connection_socket: socket):

    with connection_socket:
        # Fetch data and create the HttpRequest
        data = connection_socket.recv(1024)
        http_request = HttpRequest.from_bytes(data)

        # Construct the response
        if http_request.request_target.startswith('/echo/'):
            http_response_status = HttpResponseStatus.OK
            body = http_request.request_target.removeprefix('/echo/')
            headers = {'Content-Type': 'text/plain', 'Content-Length': str(len(body))}
        elif http_request.request_target == '/user-agent':
            http_response_status = HttpResponseStatus.OK
            body = http_request.headers['User-Agent']
            headers = {'Content-Type': 'text/plain', 'Content-Length': str(len(body))}
        elif http_request.request_target == '/':
            http_response_status = HttpResponseStatus.OK
            headers = {}
            body = ''
        else:
            http_response_status = HttpResponseStatus.NOT_FOUND
            headers = {}
            body = ''

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


def run_server():
    with socket.create_server((HOST, PORT), reuse_port=False) as server_socket:
        print(f"Server running and accepting connections at {HOST}:{PORT}{os.linesep}")

        # Main loop for incoming connections
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            while True:
                (connection_socket, connection_adress) = server_socket.accept()  # wait for client connection
                print(f'Connection stablished with {connection_adress[0]}:{connection_adress[1]}{os.linesep}')

                executor.submit(handle_connection, connection_socket)


def main():
    try:
        run_server()
    except KeyboardInterrupt:
        print('Server stopped with keyboard interrupt')

    print('--------------------Server shutting down--------------------')


if __name__ == "__main__":
    main()
