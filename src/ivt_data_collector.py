from ivt import Backend
import time

class Data_collector():
    def __init__(self):
        self.backend = Backend()
        self.data = dict()
        self.delta_t = 0.1 # How much minimum time difference between each data point
        self.start_time = time.time()
        self.prev_time = 0

    def get_data(self):
        self.backend.update()
        current_time = time.time()
        if current_time - self.prev_time > self.delta_t:
            self.data[current_time - self.start_time] = self.backend.get_important_data()
            self.prev_time = current_time



d = Data_collector()
for index in range(0, 1000):
    print(d.data)
    d.get_data()
