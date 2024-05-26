[![progress-banner](https://backend.codecrafters.io/progress/http-server/20ea0ade-be30-43c2-85db-ebc926e2fe06)](https://app.codecrafters.io/users/codecrafters-bot?r=2qF)

This is my own implementation of the 
["Build Your Own HTTP server" Challenge](https://app.codecrafters.io/courses/http-server/overview) from 
[Code Crafters](https://codecrafters.io)

[HTTP](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol) is the protocol that powers the web. In this
challenge, I built an HTTP/1.1 server that is capable of serving multiple clients using `python (3.11)`. 

Only standard  library components are used. No additional dependencies involved (discard the Pipfile dependencies file,
it is used by the CodeCrafters testing engine, not the application).


# Alicante

Along the way I built my own super minimalist Web Framework named Alicante. 

The syntax is inspired in Flask. The usage is straightforward. Just instantiate an AlicanteServer object, write your
endpoint handlers and decorate them accordingly. Keyword parameters are accepted in the path target.


```python
# application.py
from alicante.servers import AlicanteServer
from alicante.http import HttpRequest, HttpResponse, HttpMethod, HttpResponseStatus

app = AlicanteServer('localhost', 4221)


@app.route('/', HttpMethod.GET)
def get_home(request: HttpRequest) -> HttpResponse:
    return HttpResponse(HttpResponseStatus.OK, {}, b'Hi, this is the home page')


@app.route('/', HttpMethod.POST)
def get_home(request: HttpRequest) -> HttpResponse:
    return HttpResponse(HttpResponseStatus.METHOD_NOT_ALLOWED, {}, b'What are you doing?')


@app.route('/about', HttpMethod.GET)
def get_home(request: HttpRequest) -> HttpResponse:
    return HttpResponse(HttpResponseStatus.OK, {}, b'This is an AlicanteServer running')


@app.route('/echo/<to_echo>', HttpMethod.GET)
def get_echo(request: HttpRequest, to_echo: str) -> HttpResponse:
    response_body = f'You said: {to_echo}'.encode('utf-8')
    response_headers = {'Content-Type': 'text/plain',
                        'Content-Length': str(len(response_body))}

    return HttpResponse(HttpResponseStatus.OK, response_headers, response_body)


@app.route('/user-agent', HttpMethod.GET)
def get_user_agent(request: HttpRequest) -> HttpResponse:
    user_agent = request.headers['User-Agent']
    response_body = user_agent.encode('utf-8')
    response_headers = {'Content-Type': 'text/plain',
                        'Content-Length': str(len(user_agent))}

    return HttpResponse(HttpResponseStatus.OK, response_headers, response_body)


@app.route('/gogogo', HttpMethod.GET)
def get_user_agent(request: HttpRequest) -> HttpResponse:
    return HttpResponse(HttpResponseStatus.NOT_FOUND, {}, b'Where are you trying to go?')


def main():
    app.run()


if __name__ == '__main__':
    main()

```

