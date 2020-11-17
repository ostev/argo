from time import sleep

from flask import Flask, jsonify
import pickle
from gpiozero import Motor

from Motors import Motors
from Robot import Robot

left_speed = 0.0
right_speed = 0.0

current_op = ""

status_file = open("current_status.pickle", "wb")

app = Flask(__name__)

def current_status() -> dict:
    return {
        "left_speed": left_speed,
        "right_speed": right_speed,
        "current_op": current_op
    }

@app.route("/")
def root():
    return jsonify(current_status())

@app.route("/left")
def left():
    global current_op
    current_op = "left"
    status = current_status()
    pickle.dump(status, status_file, pickle.HIGHEST_PROTOCOL)
    return jsonify(status)