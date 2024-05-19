import sys

from app.application import app


def main():

    if len(sys.argv) > 1:
        if len(sys.argv) != 3 or sys.argv[1] != '--directory':
            print('Arguments error')
            print('Usage: --directory <directory>')
            return
        resources_directory = sys.argv[2]
        print(f'Server resources directory: {resources_directory}')
    else:
        resources_directory = None
        print('Server configured without a resources directory')
        print('To add a resources directory use: --directory <directory>')

    try:
        app.resource_directory = resources_directory
        app.run()
    except KeyboardInterrupt:
        print('Server stopped with keyboard interrupt')

    print('--------------------Server shutting down--------------------')


if __name__ == "__main__":
    main()
