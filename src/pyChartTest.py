from PyQt6.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        pieplate = FigureCanvasQTAgg(fig)
        layout.addWidget(pieplate)
        

labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
sizes = [15, 30, 45, 10]
fig = Figure()
pie = fig.add_subplot()
pie.pie(sizes, labels=labels)   

app = QApplication([])
window = MainWindow()
window.show()
app.exec()