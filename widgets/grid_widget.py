from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPainter, QPen, QMouseEvent, QBrush, QColor
from PySide6.QtCore import Qt, QPoint
from utils.constants import Constants


class GridWidget(QWidget):
    def __init__(self, grid_size=Constants.DEFAULT_GRID_SIZE):
        super().__init__()
        self.grid_size = grid_size
        self.current_task = "1a"
        self.setMinimumSize(Constants.GRID_MIN_SIZE, Constants.GRID_MIN_SIZE)
        self.hover_cell = None
        self.coords_label = None
        self.setup_coords_label()
        self.setMouseTracking(True)
        
    def setup_coords_label(self):
        self.coords_label = QLabel(self)
        self.coords_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid black;
                padding: 5px;
                font-weight: bold;
            }
        """)
        self.coords_label.setAlignment(Qt.AlignCenter)
        self.coords_label.hide()
        
    def set_grid_size(self, size):
        self.grid_size = size
        self.hover_cell = None
        self.coords_label.hide()
        self.update()
        
    def set_task(self, task):
        self.current_task = task
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        cell_width = width / self.grid_size
        cell_height = height / self.grid_size

        if self.current_task in ["1a", "1b", "1c"]:
            self.draw_grid(painter, width, height, cell_width, cell_height)
            
            # TODO: Добавить зоны для разных вариантов задач
            # Здесь будет код для отрисовки специальных зон в зависимости от текущей задачи
            
        elif self.current_task in ["2a", "4.1a", "4.1b", "4.1c", "4.2a", "3a", "3b", "4.3a", "4.3b"]:
            painter.fillRect(0, 0, width, height, QBrush(QColor(240, 240, 240)))
            painter.setPen(QPen(Qt.black, 2))
            painter.drawText(self.rect(), Qt.AlignCenter, f"Пункты {self.current_task}\n(реализация в разработке)")
        
        if self.hover_cell is not None and self.current_task in ["1a", "1b", "1c"]:
            row, col = self.hover_cell
            x = col * cell_width
            y = row * cell_height
            
            painter.setPen(QPen(Qt.red, 3))
            painter.drawRect(int(x), int(y), int(cell_width), int(cell_height))
    
    def draw_grid(self, painter, width, height, cell_width, cell_height):
        painter.setPen(QPen(Qt.black, 1))
        
        for i in range(self.grid_size + 1):
            x = i * cell_width
            painter.drawLine(int(x), 0, int(x), height)
        
        for i in range(self.grid_size + 1):
            y = i * cell_height
            painter.drawLine(0, int(y), width, int(y))
        
        if self.current_task == "1a":
            
            pass
        elif self.current_task == "1b":
            
            pass
        elif self.current_task == "1c":
            
            pass
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.current_task not in ["1a", "1b", "1c"]:
            self.hover_cell = None
            self.coords_label.hide()
            return
            
        if self.grid_size == 0:
            return
            
        width = self.width()
        height = self.height()
        
        cell_width = width / self.grid_size
        cell_height = height / self.grid_size
        
        col = int(event.position().x() / cell_width)
        row = int(event.position().y() / cell_height)
        
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            self.hover_cell = (row, col)
            
            self.coords_label.setText(f"({row}, {col})")
            self.coords_label.adjustSize()
            
            label_x = event.position().x() + 15
            label_y = event.position().y() + 15
            
            if label_x + self.coords_label.width() > width:
                label_x = event.position().x() - self.coords_label.width() - 5
            if label_y + self.coords_label.height() > height:
                label_y = event.position().y() - self.coords_label.height() - 5
                
            self.coords_label.move(int(label_x), int(label_y))
            self.coords_label.show()
        else:
            self.hover_cell = None
            self.coords_label.hide()
        
        self.update()
    
    def leaveEvent(self, event):
        self.hover_cell = None
        self.coords_label.hide()
        self.update()