from http.server import BaseHTTPRequestHandler, HTTPServer
from web_utils import respond_json
import time

from helpers import switch, GREEN, RESET

hostName = "localhost"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        respond_json(self, switch({lambda _: "default": lambda _: "hello"}, self.path))


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print(GREEN + ("Server started http://%s:%s" % (hostName, serverPort)) + RESET)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("\n\n" + GREEN + "Server stopped.\n" + RESET)
