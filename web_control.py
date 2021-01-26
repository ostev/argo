from http.server import BaseHTTPRequestHandler, HTTPServer
from web_utils import respond_json, not_found
import time
import re


from gpiozero import Motor

from get_robot import get_robot

from helpers import switch, GREEN, CYAN, RESET, default, map_range

hostName = "raspberrypi.local"
serverPort = 8080

requestRegex = re.compile(r"/set/(speed|angle)/(-?\d\d?\d?)")

speed: int = 0
angle: int = 0

robot = get_robot()


def run_angle(robot, angle: int, speed: int):
    print(speed)
    robot.run(map_range(angle, -90, 90, -1, 1), speed / 100)


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
        elif self.path == "/calibrate":
            speed = 0
            angle = 0

            respond_json(
                self,
                """{ "command": "calibrate", "speed": "%s", "angle": "%s" }"""
                % (speed, angle),
            )

            robot.stop()
            robot.calibrate()

        elif self.path == "/stop":
            speed = 0
            respond_json(
                self,
                """{ "command": "stop", "speed": "%s", "angle": "%s" }"""
                % (speed, angle),
            )
            robot.stop()
            print("\n%sStopped robot.%s" % (CYAN, RESET))
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

                        run_angle(robot, angle, speed)
                    else:
                        not_found(self)
                elif match.group(1) == "angle":
                    new_angle = int(match.group(2))
                    if new_angle >= -90 and new_angle <= 90:
                        angle = new_angle
                        print("\n%sSet angle to %s.%s" % (CYAN, angle, RESET))
                        respond_json(
                            self,
                            """{ "command": "set/angle", "speed": "%s", "angle": "%s" }"""
                            % (speed, angle),
                        )

                        run_angle(robot, angle, speed)
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
