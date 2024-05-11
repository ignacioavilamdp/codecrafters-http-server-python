import sys

from app.servers import HttpServer

HOST = "localhost"
PORT = 4221


def main():
    server = HttpServer(HOST, PORT, sys.argv)

    try:
        print(f'Directory argument: {sys.argv[2]}')
        # for arg in sys.argv:
        #     print(arg)
        server.run()
    except KeyboardInterrupt:
        print('Server stopped with keyboard interrupt')

    print('--------------------Server shutting down--------------------')


if __name__ == "__main__":
    main()
