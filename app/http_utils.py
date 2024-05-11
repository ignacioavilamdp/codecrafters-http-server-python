from enum import Enum

CRLF = '\r\n'


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
    NOT_FOUND = (404, 'Not Found')

    def __init__(self, status_code, status_text):
        self.status_code = status_code
        self.status_text = status_text


class HttpRequest:

    def __init__(self, http_method: HttpMethod, request_target: str, http_version: HttpVersion, headers: dict[str, str],
                 body: bytes):
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
                 body: bytes):
        self.http_version = http_version
        self.response_status = response_status
        self.headers = headers
        self.body = body

    def __str__(self):
        status_line = f'{self.http_version.value} {self.response_status.status_code} {self.response_status.status_text}'
        headers_list = [f'{key}: {value}' for (key, value) in self.headers.items()]

        return CRLF.join([status_line, CRLF.join(headers_list), '', str(self.body)])

    def to_bytes(self):
        status_line = f'{self.http_version.value} {self.response_status.status_code} {self.response_status.status_text}'
        headers_list = [f'{key}: {value}' for (key, value) in self.headers.items()]
        text_part = CRLF.join([status_line, CRLF.join(headers_list), '']) + CRLF

        return text_part.encode('utf-8') + self.body
