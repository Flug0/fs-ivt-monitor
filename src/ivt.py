 # Not the best way to import... Should be:
 # from PyQt5 import QtWidgets
 # from QtWidgets import QApplication, QMainWindow
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

def window():
    app = QApplication(sys.argv)
    win = QMainWindow()

    xPos, yPos, width, height = 100, 100, 1000, 1000

    win.setGeometry(xPos, yPos, width, height)
    win.setWindowTitle("IVT Monitor")

    label = QtWidgets.QLabel(win)
    label.setText("TEST")
    label.move(50, 50)

    win.show()
    sys.exit(app.exec_())



def main():
    window()




main()