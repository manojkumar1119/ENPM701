import serial

class IMUReader:
    # Reads heading angle lines like 'X: 123.4' from serial and returns angle in 0..360
    def __init__(self, port="/dev/ttyUSB0", baud=9600):
        self.ser = serial.Serial(port, baud)

    def flush_garbage(self, n=5):
        for _ in range(n):
            self.ser.readline()

    def get_angle(self) -> float:
        while True:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                parts = line.split()
                if len(parts) >= 2 and parts[0].rstrip(":").upper() == "X":
                    try:
                        return float(parts[1]) % 360.0
                    except:
                        continue
