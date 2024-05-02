# Uncomment this to pass the first stage
import os
import socket

CRLF = '\r\n'

HOST = "localhost"
PORT = 4221


def main():
    # Run the server
    server_socket = socket.create_server((HOST, PORT), reuse_port=False)
    print(f"Server running and accepting connections at {HOST}:{PORT}{os.linesep}")

    (connection, address) = server_socket.accept()  # wait for client
    print(f'Connection stablished with {address[0]}:{address[1]}{os.linesep}')

    # Receive the request
    request = connection.recv(1024).decode('utf-8')

    # Parse the request
    request_line = request.split(CRLF)[0]
    request_line_elements = request_line.split(' ')
    http_method = request_line_elements[0]
    request_target = request_line_elements[1]
    http_version = request_line_elements[2]

    # Response
    if request_target == '/':
        status_line = 'HTTP/1.1 200 OK'
    else:
        status_line = 'HTTP/1.1 404 Not Found'
    response = f'{status_line}{CRLF}{CRLF}'

    connection.send(response.encode('utf-8'))

    # Debugging
    print(f'Request line - http_method: {http_method}')
    print(f'Request line - request_target: {request_target}')
    print(f'Request line - http_version: {http_version}')
    print(f'Complete request: {os.linesep}{request}')
    print(f'Response: {os.linesep}{response}')


if __name__ == "__main__":
    main()
