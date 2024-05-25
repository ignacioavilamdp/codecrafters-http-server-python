import argparse

from app.application import app


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', help='server resources directory absolute path')

    args = parser.parse_args()
    if args.directory:
        print(f'Server resources directory: {args.directory}')
        app.resource_directory = args.directory
    else:
        print('Server configured without a resources directory')

    try:
        app.run()
    except KeyboardInterrupt:
        print('Server stopped with keyboard interrupt')

    print('--------------------Server shutting down--------------------')


if __name__ == "__main__":
    main()
