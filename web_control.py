from http.server import BaseHTTPRequestHandler, HTTPServer
from web_utils import respond_json, not_found
import time
import re

from helpers import switch, GREEN, CYAN, RESET, default

hostName = "raspberrypi.local"
serverPort = 8080

requestRegex = re.compile(r"/set/(speed|angle)/(\d\d?\d?)")


class MyServer(BaseHTTPRequestHandler):
    speed: int = 0
    angle: int = 0

    def do_GET(self):
        if self.path == "/status":
            respond_json(
                self,
                """{ "command": "status", "speed": "%s", "angle": "%s" }"""
                % (self.speed, self.angle),
            )
        else:
            match = requestRegex.match(self.path)
            if match != None:
                if match.group(1) == "speed":
                    speed = int(match.group(2))
                    if speed <= 100:
                        self.speed = speed
                        print("\n%sSet speed to %s.%s" % (CYAN, self.speed, RESET))
                        respond_json(
                            self,
                            """{ "command": "set/speed", "speed": "%s", "angle": "%s" }"""
                            % (self.speed, self.angle),
                        )
                    else:
                        not_found(self)
                elif match.group(1) == "angle":
                    angle = int(match.group(2))
                    if angle >= -90 and angle <= 90:
                        self.angle = angle
                        print("\n%sSet angle to %s.%s" % (CYAN, self.angle, RESET))
                        respond_json(
                            self,
                            """{ "command": "set/angle", "speed": "%s", "angle": "%s" }"""
                            % (self.speed, self.angle),
                        )
                    else:
                        not_found(self)
                else:
                    not_found(self)
            else:
                not_found(self)


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("\n%sServer started at http://%s:%s%s" % (GREEN, hostName, serverPort, RESET))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("\n\n%sServer stopped.%s\n" % (GREEN, RESET))
