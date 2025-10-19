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
        self.placed_figures = []  # Каждая фигура - список пар [(координаты, type), ...]
        self.forbidden_zones = []  # Каждая запретная зона - список пар [(координаты, type), ...]
        self.placed_cells = set()  # Для 1c/4.1c: пары ((координаты), type)
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
        self.placed_cells = set()
        self.current_rotation = 0
        self.update_current_figure()
        self.update_figures_count()
        self.update()
        
    def set_task(self, task):
        self.current_task = task
        self.placed_figures = []
        self.forbidden_zones = []
        self.placed_cells = set()
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
                # Для всех задач кроме 1c/4.1c type всегда 0
                cell_type = 0
                cells.append(((new_row, new_col), cell_type))
        return cells
    
    def get_forbidden_zone_cells(self, figure_cells):
        forbidden_cells = []
        
        # Извлекаем только координаты из figure_cells
        coord_cells = [coord for coord, cell_type in figure_cells]
        
        if self.current_task in ["1a", "1b", "1c"]:
            for row, col in coord_cells:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        new_row, new_col = row + dr, col + dc
                        if 0 <= new_row < self.grid_size and 0 <= new_col < self.grid_size:
                            # Для всех задач type всегда 0
                            forbidden_cells.append(((new_row, new_col), 0))
        
        elif self.current_task in ["4.1a", "4.1b", "4.1c"]:
            for row, col in coord_cells:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < self.grid_size and 0 <= new_col < self.grid_size:
                        # Для всех задач type всегда 0
                        forbidden_cells.append(((new_row, new_col), 0))
        
        # Убираем клетки, которые уже есть в фигуре
        forbidden_coords = set([coord for coord, cell_type in forbidden_cells])
        figure_coords = set([coord for coord, cell_type in figure_cells])
        forbidden_cells = [((row, col), cell_type) for (row, col), cell_type in forbidden_cells 
                          if (row, col) not in figure_coords]
        
        return forbidden_cells
    
    def can_place_figure(self, row, col):
        if self.current_task in ["1c", "4.1c"]:
            # Для 1c/4.1c проверяем отдельную клетку
            coord_to_check = (row, col)
            cell_type = 0  # Для 1c/4.1c type всегда 0
            
            # Проверяем, не занята ли клетка
            for placed_coord, placed_type in self.placed_cells:
                if placed_coord == coord_to_check:
                    return False
            
            # Проверяем, не в запретной зоне ли клетка
            for forbidden_coord, forbidden_type in self.forbidden_zones:
                if forbidden_coord == coord_to_check:
                    return False
            
            return True
        
        # Для остальных задач проверяем всю фигуру
        cells = self.get_figure_cells(row, col)
        
        if len(cells) != len(self.current_figure):
            return False
        
        # Проверяем, не пересекается ли с уже размещенными фигурами
        for cell_coord, cell_type in cells:
            for figure in self.placed_figures:
                for placed_cell_coord, placed_cell_type in figure:
                    if placed_cell_coord == cell_coord:
                        return False
        
        # Проверяем, не в запретной зоне ли
        for cell_coord, cell_type in cells:
            for forbidden_coord, forbidden_type in self.forbidden_zones:
                if forbidden_coord == cell_coord:
                    return False
        
        return True
    
    def find_connected_components(self):
        if not self.placed_cells:
            return []
            
        visited = set()
        components = []
        
        if self.current_task == "1c":
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        else:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        # Используем только координаты для поиска компонент связности
        placed_coords = {coord for coord, cell_type in self.placed_cells}
        
        for coord in placed_coords:
            if coord not in visited:
                component = []
                stack = [coord]
                
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        # Находим соответствующий тип для этой координаты
                        cell_type = next((t for c, t in self.placed_cells if c == current), 0)
                        component.append((current, cell_type))
                        
                        for dr, dc in directions:
                            neighbor = (current[0] + dr, current[1] + dc)
                            if neighbor in placed_coords and neighbor not in visited:
                                stack.append(neighbor)
                
                components.append(component)
        
        return components
    
    def update_figures_from_components(self):
        self.placed_figures = []
        self.forbidden_zones = []
        
        components = self.find_connected_components()
        s = self.variables["s"]
        
        for component in components:
            if len(component) == s:
                self.placed_figures.append(component)
                forbidden_cells = self.get_forbidden_zone_cells(component)
                self.forbidden_zones.extend(forbidden_cells)
    
    def place_figure(self, row, col):
        if self.current_task in ["1c", "4.1c"]:
            if self.can_place_figure(row, col):
                # Для 1c/4.1c type всегда 0
                cell_type = 0
                self.placed_cells.add(((row, col), cell_type))
                self.update_figures_from_components()
                
                self.update_figures_count()
                self.update()
                return True
            return False
        
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
        if self.current_task in ["1c", "4.1c"]:
            # Ищем клетку с такими координатами (игнорируя type)
            cell_to_remove = None
            for cell in self.placed_cells:
                if cell[0] == (row, col):
                    cell_to_remove = cell
                    break
            
            if cell_to_remove:
                self.placed_cells.remove(cell_to_remove)
                self.update_figures_from_components()
                
                self.update_figures_count()
                self.update()
                return True
            return False
        
        # Для остальных задач ищем фигуру, содержащую эту клетку
        for i, figure in enumerate(self.placed_figures):
            for cell_coord, cell_type in figure:
                if cell_coord == (row, col):
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

        if self.current_task in ["1a", "4.1a", "1b", "4.1b", "1c", "4.1c", "2a", "4.2a"]:
            self.draw_grid(painter, width, height, cell_width, cell_height)
            
            # Рисуем запретные зоны (используем только координаты)
            for zone_coord, zone_type in self.forbidden_zones:
                row, col = zone_coord
                x = col * cell_width
                y = row * cell_height
                painter.fillRect(int(x), int(y), int(cell_width), int(cell_height), 
                               QBrush(QColor(255, 0, 0, 80)))
            
            if self.current_task in ["1c", "4.1c"]:
                # Рисуем отдельные клетки для 1c/4.1c (используем только координаты)
                for coord, cell_type in self.placed_cells:
                    row, col = coord
                    x = col * cell_width
                    y = row * cell_height
                    color = QColor(0, 255, 0, 180)
                    painter.fillRect(int(x), int(y), int(cell_width), int(cell_height), 
                                   QBrush(color))
            
            # Рисуем фигуры (используем только координаты)
            for figure in self.placed_figures:
                for coord, cell_type in figure:
                    row, col = coord
                    x = col * cell_width
                    y = row * cell_height
                    painter.fillRect(int(x), int(y), int(cell_width), int(cell_height), 
                                   QBrush(QColor(0, 0, 255, 180)))
        
        if self.current_task in ["1a", "4.1a", "1b", "4.1b"]:
            if self.hover_cell is not None and self.can_place_figure(*self.hover_cell):
                row, col = self.hover_cell
                cells = self.get_figure_cells(row, col)
                for coord, cell_type in cells:
                    r, c = coord
                    x = c * cell_width
                    y = r * cell_height
                    painter.fillRect(int(x), int(y), int(cell_width), int(cell_height), 
                                   QBrush(QColor(255, 0, 0, 120)))
            
        elif self.current_task in ["3a", "3b", "4.3a", "4.3b"]:
            painter.fillRect(0, 0, width, height, QBrush(QColor(240, 240, 240)))
            painter.setPen(QPen(Qt.black, 2))
            painter.drawText(self.rect(), Qt.AlignCenter, f"Пункты {self.current_task}\n(реализация в разработке)")
        
        if self.hover_cell is not None and self.current_task in ["1a", "4.1a", "1b", "4.1b", "1c", "4.1c", "2a", "4.2a"]:
            row, col = self.hover_cell
            
            x = col * cell_width
            y = row * cell_height
            
            painter.setPen(QPen(Qt.red, 3))
            painter.drawRect(int(x), int(y), int(cell_width), int(cell_height))
            
            if self.current_task in ["1c", "4.1c"] and self.can_place_figure(row, col):
                painter.fillRect(int(x), int(y), int(cell_width), int(cell_height), 
                               QBrush(QColor(255, 0, 0, 120)))
    
    def draw_grid(self, painter, width, height, cell_width, cell_height):
        painter.setPen(QPen(Qt.black, 1))
        
        for i in range(self.grid_size + 1):
            x = i * cell_width
            painter.drawLine(int(x), 0, int(x), height)
        
        for i in range(self.grid_size + 1):
            y = i * cell_height
            painter.drawLine(0, int(y), width, int(y))
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.current_task not in ["1a", "4.1a", "1b", "4.1b", "1c", "4.1c", "2a", "4.2a"]:
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
        if self.current_task in ["1a", "4.1a", "1b", "4.1b", "1c", "4.1c", "2a", "4.2a"]:
            if event.button() == Qt.LeftButton and self.hover_cell is not None:
                row, col = self.hover_cell
                
                # Проверяем, есть ли уже фигура в этой клетке (используем только координаты)
                figure_exists = False
                for figure in self.placed_figures:
                    for coord, cell_type in figure:
                        if coord == (row, col):
                            figure_exists = True
                            break
                    if figure_exists:
                        break
                
                if self.current_task in ["1c", "4.1c"]:
                    # Проверяем, есть ли уже клетка с такими координатами
                    cell_exists = any(coord == (row, col) for coord, cell_type in self.placed_cells)
                    if cell_exists:
                        self.remove_figure_at(row, col)
                    else:
                        self.place_figure(row, col)
                elif self.current_task in ["2a", "4.2a"]:
                    pass
                else:
                    if figure_exists:
                        self.remove_figure_at(row, col)
                    else:
                        self.place_figure(row, col)

        print("placed_figures: " + f"{self.placed_figures}")
        print("forbidden_zones: " + f"{self.forbidden_zones}")
        print("placed_cells: " + f"{self.placed_cells}")
        print("current_figure: " + f"{self.current_figure}")
        print("current_rotation: " + f"{self.current_rotation}")
    
    def leaveEvent(self, event):
        self.hover_cell = None
        self.coords_label.hide()
        self.update()