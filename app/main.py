import os
import socket
import string
from enum import Enum

CRLF = '\r\n'

HOST = "localhost"
PORT = 4221


class ResponseStatus(Enum):

    OK = (200, 'OK')
    BAD_REQUEST = (400, 'Bad Request')
    UNAUTHORIZED = (401, 'Unauthorized')
    FORBIDDEN = (403, 'Forbidden')
    NOT_FOUND = (404, 'Not found')

    def __init__(self, status_code, status_text):
        self.status_code = status_code
        self.status_text = status_text


class HttpRequest:

    def __init__(self, http_method, request_target, http_version, headers, body):
        self.http_method = http_method
        self.request_target = request_target
        self.http_version = http_version
        self.headers = headers
        self.body = body

    @staticmethod
    def from_string(request_string):
        request_line, *headers, empty_line, body = request_string.split(CRLF)
        http_method, request_target, http_version = request_line.split(' ')
        return HttpRequest(http_method, request_target, http_version, headers, body)


class HttpResponse:
    def __init__(self, http_version, response_status: ResponseStatus, headers, body):
        self.http_version = http_version
        self.response_status = response_status
        self.headers = headers
        self.body = body

    def to_string(self):
        status_line = f'{self.http_version} {self.response_status.status_code} {self.response_status.status_text}'
        return CRLF.join([status_line, CRLF.join(self.headers), '', self.body])


def main():
    # Run the server
    server_socket = socket.create_server((HOST, PORT), reuse_port=False)
    print(f"Server running and accepting connections at {HOST}:{PORT}{os.linesep}")

    (connection, address) = server_socket.accept()  # wait for client
    print(f'Connection stablished with {address[0]}:{address[1]}{os.linesep}')

    # Receive and process the request
    request_string = connection.recv(1024).decode('utf-8')
    http_request = HttpRequest.from_string(request_string)

    # Construct the response
    if http_request.request_target.startswith('/echo/'):
        body = http_request.request_target.removeprefix('/echo/')
        content_type_header = 'Content-Type: text/plain'
        content_length = f'Content-Length: {len(body)}'
        http_response = HttpResponse('HTTP/1.1', ResponseStatus.OK, [content_type_header, content_length], body)
    else:
        http_response = HttpResponse('HTTP/1.1', ResponseStatus.NOT_FOUND, [], '')

    # Send response
    connection.send(http_response.to_string().encode('utf-8'))

    # Debugging
    print(f'Request line - http_method: {http_request.http_method}')
    print(f'Request line - request_target: {http_request.request_target}')
    print(f'Request line - http_version: {http_request.http_version}{os.linesep}')
    print(f'Complete request: {os.linesep}{request_string}')
    print(f'Response: {os.linesep}{http_response.to_string()}')


if __name__ == "__main__":
    main()
