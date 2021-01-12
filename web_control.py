from http.server import BaseHTTPRequestHandler, HTTPServer
from web_utils import respond_json, not_found
import time
import re


from gpiozero import Motor

from Robot import Robot
from Motors import Motors
from get_robot import get_robot

from helpers import switch, GREEN, CYAN, RESET, default

hostName = "raspberrypi.local"
serverPort = 8080

requestRegex = re.compile(r"/set/(speed|angle)/(\d\d?\d?)")

speed: int = 0
angle: int = 0

robot = get_robot()


class WebControlHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global angle
        global speed
        global robot

        if self.path == "/status":
            respond_json(
                self,
                """{ "command": "status", "speed": "%s", "angle": "%s" }"""
                % (speed, angle),
            )
        else:
            match = requestRegex.match(self.path)
            if match != None:
                if match.group(1) == "speed":
                    newSpeed = int(match.group(2))
                    if newSpeed <= 100:
                        speed = newSpeed
                        print("\n%sSet speed to %s.%s" % (CYAN, speed, RESET))
                        respond_json(
                            self,
                            """{ "command": "set/speed", "speed": "%s", "angle": "%s" }"""
                            % (speed, angle),
                        )

                    else:
                        not_found(self)
                elif match.group(1) == "angle":
                    newAngle = int(match.group(2))
                    if newAngle >= -90 and newAngle <= 90:
                        angle = newAngle
                        print("\n%sSet angle to %s.%s" % (CYAN, angle, RESET))
                        respond_json(
                            self,
                            """{ "command": "set/angle", "speed": "%s", "angle": "%s" }"""
                            % (speed, angle),
                        )
                    else:
                        not_found(self)
                else:
                    not_found(self)
            else:
                not_found(self)


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), WebControlHandler)
    print("\n%sServer started at http://%s:%s%s" % (GREEN, hostName, serverPort, RESET))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    robot.close()
    print("\n\n%sServer stopped.%s\n" % (GREEN, RESET))
