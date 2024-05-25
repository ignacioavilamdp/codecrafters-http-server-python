from enum import Enum

CRLF = '\r\n'
ENCODING = 'utf-8'


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
    CREATED = (201, 'Created')
    BAD_REQUEST = (400, 'Bad Request')
    UNAUTHORIZED = (401, 'Unauthorized')
    FORBIDDEN = (403, 'Forbidden')
    NOT_FOUND = (404, 'Not Found')

    def __init__(self, code, text):
        self.code = code
        self.text = text


class HttpRequest:

    def __init__(self, method: HttpMethod, target: str, version: HttpVersion, headers: dict[str, str], body: bytes):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.body = body

    def __str__(self):
        request_line = f'{self.method.value} {self.target} {self.version.value}'
        headers_list = [f'{key}: {value}' for (key, value) in self.headers.items()]
        return CRLF.join([request_line, CRLF.join(headers_list), '', str(self.body)])

    @staticmethod
    def from_bytes(request_bytes: bytes):
        complete_header, empty_line, body = request_bytes.partition(f'{CRLF}{CRLF}'.encode(ENCODING))
        request_line, *headers_list = complete_header.decode(ENCODING).split(CRLF)
        method_name, target, version_name = request_line.split(' ')

        headers = dict()
        for header in headers_list:
            key, sep, value = header.partition(':')
            headers[key] = value.strip()

        return HttpRequest(HttpMethod(method_name), target, HttpVersion(version_name), headers, body)


class HttpResponse:
    def __init__(self, version: HttpVersion, status: HttpResponseStatus, headers: dict[str, str], body: bytes):
        self.version = version
        self.status = status
        self.headers = headers
        self.body = body

    def __str__(self):
        status_line = f'{self.version.value} {self.status.code} {self.status.text}'
        headers_list = [f'{key}: {value}' for (key, value) in self.headers.items()]
        return CRLF.join([status_line, CRLF.join(headers_list), '', str(self.body)])

    def to_bytes(self):
        status_line = f'{self.version.value} {self.status.code} {self.status.text}'
        headers_list = [f'{key}: {value}' for (key, value) in self.headers.items()]
        complete_header = CRLF.join([status_line, CRLF.join(headers_list), '']) + CRLF

        return complete_header.encode(ENCODING) + self.body