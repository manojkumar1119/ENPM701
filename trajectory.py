import matplotlib.pyplot as plt

class Trajectory:
    def __init__(self, start_x, start_y):
        self.x = [start_x]
        self.y = [start_y]

    def append(self, dx, dy):
        self.x.append(self.x[-1] + dx)
        self.y.append(self.y[-1] + dy)

    def append_abs(self, x, y):
        self.x.append(x)
        self.y.append(y)

    def plot(self):
        plt.figure()
        plt.plot(self.x, self.y, "-o", label="Robot Path")
        plt.plot(self.x[0], self.y[0], "o", markersize=10, label="Start")
        plt.plot(self.x[-1], self.y[-1], "o", markersize=10, label="End")
        plt.title("Robot Trajectory")
        plt.xlabel("X (cm)"); plt.ylabel("Y (cm)")
        plt.grid(True); plt.axis("equal"); plt.legend()
        plt.show()
