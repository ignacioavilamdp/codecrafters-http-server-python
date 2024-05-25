import re
from typing import Callable
from alicante.http import HttpMethod, HttpResponse, HttpRequest


class RouteHandler:

    def __init__(self, route_pattern: str, method: HttpMethod, handler: Callable[[HttpRequest], HttpResponse]):
        self.route_pattern = route_pattern
        self.regex_pattern = self.get_regex_pattern(route_pattern)
        self.method = method
        self.handler = handler

    def __eq__(self, other):
        return (self.method, self.regex_pattern) == (other.method, other.regex_pattern)

    def __hash__(self):
        return hash((self.method, self.regex_pattern))

    def match(self, request:HttpRequest) -> (bool, dict):
        if self.method == request.method:
            m = re.match(self.regex_pattern, request.target)
            if m and m.group() == request.target:
                return True, m.groupdict()
        return False, None

    def get_regex_pattern(self, route_pattern: str) -> str:
        tokens = re.split(r'<(.*?)>', route_pattern)
        var_names = tokens[1::2]
        tokens[1::2] = [rf'(?P<{name}>\S*)' for name in var_names]
        return ''.join(tokens)


