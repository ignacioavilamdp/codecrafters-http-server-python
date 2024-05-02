# Uncomment this to pass the first stage
import socket

CRLF = '\r\n'


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=False)
    (connection_socket, address) = server_socket.accept()  # wait for client

    print(f'server_socket object: {connection_socket}')
    print(f'address: {address}')
    print()

    status_line = 'HTTP/1.1 200 OK'
    response = f'{status_line}{CRLF}{CRLF}'

    if connection_socket:
        message_bytes = connection_socket.recv(999)
        message_text = message_bytes.decode('utf-8')
        print('received message')
        print(message_text)
        print()

        print('message to send')
        print(response)
        connection_socket.send(response.encode('utf-8'))


if __name__ == "__main__":
    main()
