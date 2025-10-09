from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                               QSpinBox, QLabel, QComboBox)
from PySide6.QtCore import Qt
from utils.constants import Constants


class SettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(Constants.SETTINGS_PANEL_WIDTH)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title = QLabel("Настройки")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        layout.addWidget(QLabel("Выбор пункта:"))
        self.task_combo = QComboBox()
        self.task_combo.addItems(["1a", "1b", "1c", "2a", "3a", "3b", "4.1a", "4.1b", "4.1c", "4.2a", "4.3a", "4.3b"])
        layout.addWidget(self.task_combo)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("Размер сетки (n x n):"))
        self.grid_size_input = QSpinBox()
        self.grid_size_input.setRange(Constants.MIN_GRID_SIZE, Constants.MAX_GRID_SIZE)
        self.grid_size_input.setValue(Constants.DEFAULT_GRID_SIZE)
        layout.addWidget(self.grid_size_input)
        
        layout.addSpacing(20)
        
        self.apply_button = QPushButton("Применить изменения")
        self.apply_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.apply_button)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def get_grid_size(self):
        return self.grid_size_input.value()
    
    def get_selected_task(self):
        return self.task_combo.currentText()