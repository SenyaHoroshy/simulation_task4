from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPainter, QPen, QMouseEvent, QBrush, QColor
from PySide6.QtCore import Qt, QPoint, Signal
from utils.constants import Constants
from utils.figure_manager import FigureManager


class GridWidget(QWidget):
    figures_count_changed = Signal(int)
    
    def __init__(self, grid_size=Constants.DEFAULT_GRID_SIZE):
        super().__init__()
        self.grid_size = grid_size
        self.current_task = "1a"
        self.variables = {"s": 1, "t": 1}
        self.setMinimumSize(Constants.GRID_MIN_SIZE, Constants.GRID_MIN_SIZE)
        self.hover_cell = None
        self.coords_label = None
        self.placed_figures = []
        self.forbidden_zones = []
        self.current_figure = self.get_figure_shape()
        self.current_rotation = 0
        self.setup_coords_label()
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        
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
        self.placed_figures = []
        self.forbidden_zones = []
        self.current_rotation = 0
        self.update_current_figure()
        self.update_figures_count()
        self.update()
        
    def set_task(self, task):
        self.current_task = task
        self.placed_figures = []
        self.forbidden_zones = []
        self.current_rotation = 0
        self.update_current_figure()
        self.update_figures_count()
        self.update()
        
    def set_variables(self, variables):
        self.variables = variables
        self.update_current_figure()
        self.update()
    
    def get_figure_shape(self):
        if self.current_task in ["1a", "4.1a"]:
            return FigureManager.get_figure_shapes()["corner"]
        elif self.current_task in ["1b", "4.1b"]:
            s, t = self.variables["s"], self.variables["t"]
            rectangle = []
            for i in range(s):
                for j in range(t):
                    rectangle.append((i, j))
            return rectangle
        return FigureManager.get_figure_shapes()["corner"]
    
    def update_current_figure(self):
        base_figure = self.get_figure_shape()
        self.current_figure = FigureManager.rotate_figure(base_figure, self.current_rotation)
    
    def rotate_figure(self):
        self.current_rotation = (self.current_rotation + 1) % 4
        self.update_current_figure()
        self.update()
    
    def get_figure_cells(self, base_row, base_col):
        cells = []
        for dr, dc in self.current_figure:
            new_row = base_row + dr
            new_col = base_col + dc
            if 0 <= new_row < self.grid_size and 0 <= new_col < self.grid_size:
                cells.append((new_row, new_col))
        return cells
    
    def get_forbidden_zone_cells(self, figure_cells):
        forbidden_cells = set()
        
        if self.current_task in ["1a", "1b", "1c"]:
            for row, col in figure_cells:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        new_row, new_col = row + dr, col + dc
                        if 0 <= new_row < self.grid_size and 0 <= new_col < self.grid_size:
                            forbidden_cells.add((new_row, new_col))
        
        elif self.current_task in ["4.1a", "4.1b", "4.1c"]:
            for row, col in figure_cells:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < self.grid_size and 0 <= new_col < self.grid_size:
                        forbidden_cells.add((new_row, new_col))
        
        forbidden_cells = forbidden_cells - set(figure_cells)
        
        return list(forbidden_cells)
    
    def can_place_figure(self, row, col):
        cells = self.get_figure_cells(row, col)
        
        if len(cells) != len(self.current_figure):
            return False
        
        for cell in cells:
            for figure in self.placed_figures:
                if cell in figure:
                    return False
        
        for cell in cells:
            if cell in self.forbidden_zones:
                return False
        
        return True
    
    def place_figure(self, row, col):
        if self.can_place_figure(row, col):
            cells = self.get_figure_cells(row, col)
            self.placed_figures.append(cells)
            
            forbidden_cells = self.get_forbidden_zone_cells(cells)
            self.forbidden_zones.extend(forbidden_cells)
            
            self.update_figures_count()
            self.update()
            return True
        return False
    
    def remove_figure_at(self, row, col):
        for i, figure in enumerate(self.placed_figures):
            if (row, col) in figure:
                removed_figure = self.placed_figures.pop(i)
                
                self.update_all_forbidden_zones()
                
                self.update_figures_count()
                self.update()
                return True
        return False
    
    def update_all_forbidden_zones(self):
        self.forbidden_zones = []
        for figure in self.placed_figures:
            forbidden_cells = self.get_forbidden_zone_cells(figure)
            self.forbidden_zones.extend(forbidden_cells)
    
    def update_figures_count(self):
        count = len(self.placed_figures)
        self.figures_count_changed.emit(count)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R:
            self.rotate_figure()
        else:
            super().keyPressEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        cell_width = width / self.grid_size
        cell_height = height / self.grid_size

        if self.current_task in ["1a", "4.1a", "1b", "4.1b"]:
            self.draw_grid(painter, width, height, cell_width, cell_height)
            
            for zone_cell in self.forbidden_zones:
                row, col = zone_cell
                x = col * cell_width
                y = row * cell_height
                painter.fillRect(int(x), int(y), int(cell_width), int(cell_height), 
                               QBrush(QColor(255, 0, 0, 80)))
            
            for figure in self.placed_figures:
                for row, col in figure:
                    x = col * cell_width
                    y = row * cell_height
                    painter.fillRect(int(x), int(y), int(cell_width), int(cell_height), 
                                   QBrush(QColor(0, 0, 255, 180)))
        
        if self.current_task in ["1a", "4.1a", "1b", "4.1b"]:
            if self.hover_cell is not None and self.can_place_figure(*self.hover_cell):
                row, col = self.hover_cell
                cells = self.get_figure_cells(row, col)
                for r, c in cells:
                    x = c * cell_width
                    y = r * cell_height
                    painter.fillRect(int(x), int(y), int(cell_width), int(cell_height), 
                                   QBrush(QColor(255, 0, 0, 120)))
            
        elif self.current_task in ["1c", "2a", "4.1c", "4.2a", "3a", "3b", "4.3a", "4.3b"]:
            painter.fillRect(0, 0, width, height, QBrush(QColor(240, 240, 240)))
            painter.setPen(QPen(Qt.black, 2))
            painter.drawText(self.rect(), Qt.AlignCenter, f"Пункты {self.current_task}\n(реализация в разработке)")
        
        if self.hover_cell is not None and self.current_task in ["1a", "4.1a", "1b", "4.1b"]:
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
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.current_task not in ["1a", "4.1a", "1b", "4.1b"]:
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
    
    def mousePressEvent(self, event: QMouseEvent):
        if self.current_task in ["1a", "4.1a", "1b", "4.1b"]:
            if event.button() == Qt.LeftButton and self.hover_cell is not None:
                row, col = self.hover_cell
                
                figure_exists = False
                for figure in self.placed_figures:
                    if (row, col) in figure:
                        figure_exists = True
                        break
                
                if figure_exists:
                    self.remove_figure_at(row, col)
                else:
                    self.place_figure(row, col)
    
    def leaveEvent(self, event):
        self.hover_cell = None
        self.coords_label.hide()
        self.update()