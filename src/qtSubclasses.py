from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout
from PyQt6.QtCore import QAbstractTableModel, Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class CustomDialog(QDialog):
    def __init__(self, titletext, labeltext):
        super().__init__()
        
        self.setWindowTitle(titletext)
        
        QBtn = (QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        
        self.buttonbox = QDialogButtonBox(QBtn)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)
        
        dialoglayout = QVBoxLayout()
        message = QLabel(labeltext)
        dialoglayout.addWidget(message)
        dialoglayout.addWidget(self.buttonbox)
        self.setLayout(dialoglayout)
        

class SubmissionTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        
        self.grey = '#e0e0eb'
        
    def data(self, index, role):
        cell_value = self._data.iloc[index.row(), index.column()]
        
        if role == Qt.ItemDataRole.DisplayRole:
            #value = self._data.iloc[index.row(), index.column()]
            return str(cell_value)
        # TDP Add
        if role == Qt.ItemDataRole.ToolTipRole:
            return cell_value
        
    def rowCount(self, index):
        return self._data.shape[0]
    
    def columnCount(self, index):
        return self._data.shape[1]
    
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
            

class PieCanvas(FigureCanvasQTAgg):
    def __init__(self, pieslices, pielabels, parent=None):
        fig, ax = plt.subplot()
        ax.pie(pieslices, labels=pielabels, labeldistance=1.15)
        super().__init__(fig)