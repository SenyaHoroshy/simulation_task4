from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt
from utils.constants import Constants


class GridWidget(QWidget):
    def __init__(self, grid_size=Constants.DEFAULT_GRID_SIZE):
        super().__init__()
        self.grid_size = grid_size
        self.setMinimumSize(Constants.GRID_MIN_SIZE, Constants.GRID_MIN_SIZE)
        
    def set_grid_size(self, size):
        self.grid_size = size
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        cell_width = width / self.grid_size
        cell_height = height / self.grid_size
        
        painter.setPen(QPen(Qt.black, 1))
        
        for i in range(self.grid_size + 1):
            x = i * cell_width
            painter.drawLine(int(x), 0, int(x), height)
        
        for i in range(self.grid_size + 1):
            y = i * cell_height
            painter.drawLine(0, int(y), width, int(y))