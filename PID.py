from time import time

class PID:
    def __init__(self, kP=1, kI=0, kD=0):
        (self.kP, self.kI, self.kD) = (kP, kI, kD)

        self.current_time = time()
        self.previous_time = self.current_time

        self.previous_error = 0

        (self.cP, self.cI, self.cD) = (0, 0, 0)
    
    def update(self, error):
        self.current_time = time()
        delta_time = self.current_time - self.previous_time

        delta_error = error - self.previous_error

        self.cP = error
        self.cI += error * delta_time
        self.cD = (delta_error / delta_time) if delta_time > 0 else 0

        self.previous_time = self.current_time
        self.previous_error = error

        return sum([
            self.kP * self.cP,
            self.kI * self.cI,
            self.kD * self.cD
        ])