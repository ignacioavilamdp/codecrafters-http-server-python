import os
import gzip

from alicante.servers import AlicanteServer
from alicante.http import HttpRequest, HttpResponse, HttpVersion, HttpResponseStatus, HttpMethod

HOST = "localhost"
PORT = 4221

app = AlicanteServer(HOST, PORT)


@app.route('/', HttpMethod.GET)
def get_home(request: HttpRequest) -> HttpResponse:
    return HttpResponse(HttpVersion.HTTP11, HttpResponseStatus.OK, {}, b'')


@app.route('/echo/<to_echo>', HttpMethod.GET)
def get_echo(request: HttpRequest, to_echo: str) -> HttpResponse:

    request_accept_encodings = [e.strip() for e in request.headers.get('Accept-Encoding', '').split(',')]

    if 'gzip' in request_accept_encodings:
        compressed_bytes = gzip.compress(to_echo.encode('utf-8'))
        compressed_bytes_as_string = compressed_bytes.hex()
        response_body = compressed_bytes_as_string.encode('utf-8')
        response_headers = {'Content-Encoding': 'gzip',
                            'Content-Type': 'text/plain',
                            'Content-Length': str(len(compressed_bytes))}
    else:
        response_body = to_echo.encode('utf-8')
        response_headers = {'Content-Type': 'text/plain',
                            'Content-Length': str(len(to_echo))}

    return HttpResponse(HttpVersion.HTTP11, HttpResponseStatus.OK, response_headers, response_body)


@app.route('/user-agent', HttpMethod.GET)
def get_user_agent(request: HttpRequest) -> HttpResponse:

    user_agent = request.headers['User-Agent']
    response_body = user_agent.encode('utf-8')
    response_headers = {'Content-Type': 'text/plain',
                        'Content-Length': str(len(user_agent))}

    return HttpResponse(HttpVersion.HTTP11, HttpResponseStatus.OK, response_headers, response_body)


@app.route('/files/<file_name>', HttpMethod.GET)
def get_file(request: HttpRequest, file_name: str) -> HttpResponse:
    file_path = os.path.join(app.resource_directory, file_name)

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

    return HttpResponse(HttpVersion.HTTP11, response_status, response_headers, response_body)


@app.route('/files/<file_name>', HttpMethod.POST)
def post_file(request: HttpRequest, file_name: str) -> HttpResponse:
    file_path = os.path.join(app.resource_directory, file_name)

    with open(file_path, 'wb') as f:
        f.write(request.body)

    return HttpResponse(HttpVersion.HTTP11, HttpResponseStatus.CREATED, {}, b'')


def main():
    app.run()


if __name__ == '__main__':
    main()
