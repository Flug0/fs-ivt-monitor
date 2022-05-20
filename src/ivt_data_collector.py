from ivt_backend import Backend
import time
import sys

class Data_collector():
    def __init__(self):
        self.backend = Backend()
        self.data = dict()
        self.delta_t = 0.1 # How much minimum time difference between each data point
        self.start_time = time.time()
        self.prev_time = 0


    # Update data from backend, if updated, return True
    def get_data(self):
        self.backend.update()
        current_time = time.time()
        if current_time - self.prev_time > self.delta_t:
            self.data[current_time - self.start_time] = self.backend.get_important_data()
            self.prev_time = current_time
            return True
        else:
            return False

    def plot_data(self):
        print("HEJ")
        # Plot last values
        last_time_key = list(self.data)[-1]
        lst = []
        for element in self.data[last_time_key]:
            lst.append(self.data[last_time_key][element])
        #print(last_time_key, lst)

    def run(self):
        if self.get_data():
            #self.plot_data()
            return True
        else:
            return False

    # Convert last data point to string format and return it
    def send_data(self):
        last_time_key = list(self.data)[-1]
        string = str(last_time_key)
        for element in self.data[last_time_key]:
            string += "$" + str(self.data[last_time_key][element])
        return string


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    d = Data_collector()
    d.win.setupUi(MainWindow)
    MainWindow.show()
    MainWindow.update()
    status = app.exec_()
    d.run()
    sys.exit(status)
