from http.server import BaseHTTPRequestHandler, HTTPServer
from web_utils import respond_json
import time

from helpers import switch, GREEN, RESET

hostName = "raspberrypi.local"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):
    speed: int = 0
    angle: int = 90

    def do_GET(self):
        respond_json(
            self,
            switch(
                {
                    lambda _: "default": lambda _: """{ "command": "status", "speed": "%s", "angle": "%s" }"""
                    % (self.speed, self.angle)
                },
                self.path,
            ),
        )


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print(GREEN + ("Server started http://%s:%s" % (hostName, serverPort)) + RESET)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("\n\n" + GREEN + "Server stopped.\n" + RESET)
