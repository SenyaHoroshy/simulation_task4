from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                               QSpinBox, QLabel, QComboBox, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from utils.constants import Constants


class SettingsPanel(QWidget):
    task_changed = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedWidth(Constants.SETTINGS_PANEL_WIDTH)
        self.current_variables = {"s": 0, "t": 0}
        self.current_task = "1a"
        self.current_grid_size = Constants.DEFAULT_GRID_SIZE
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
        self.task_combo.currentTextChanged.connect(self.on_task_changed)
        layout.addWidget(self.task_combo)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("Размер сетки (n x n):"))
        self.grid_size_input = QSpinBox()
        self.grid_size_input.setRange(Constants.MIN_GRID_SIZE, Constants.MAX_GRID_SIZE)
        self.grid_size_input.setValue(Constants.DEFAULT_GRID_SIZE)
        layout.addWidget(self.grid_size_input)
        
        layout.addSpacing(10)
        
        self.s_widget = QWidget()
        self.s_layout = QHBoxLayout(self.s_widget)
        self.s_layout.setContentsMargins(0, 0, 0, 0)
        self.s_layout.addWidget(QLabel("s:"))
        self.s_input = QSpinBox()
        self.s_input.setRange(1, Constants.MAX_GRID_SIZE)
        self.s_input.setValue(1)
        self.s_layout.addWidget(self.s_input)
        self.s_layout.addStretch()
        layout.addWidget(self.s_widget)
        
        self.t_widget = QWidget()
        self.t_layout = QHBoxLayout(self.t_widget)
        self.t_layout.setContentsMargins(0, 0, 0, 0)
        self.t_layout.addWidget(QLabel("t:"))
        self.t_input = QSpinBox()
        self.t_input.setRange(1, Constants.MAX_GRID_SIZE)
        self.t_input.setValue(1)
        self.t_layout.addWidget(self.t_input)
        self.t_layout.addStretch()
        layout.addWidget(self.t_widget)
        
        self.s_widget.setVisible(False)
        self.t_widget.setVisible(False)
        
        layout.addSpacing(20)
        
        info_title = QLabel("Текущие параметры:")
        info_title.setStyleSheet("font-weight: bold;")
        layout.addWidget(info_title)
        
        self.parameters_label = QLabel("Пункт: 1a\nn: 10")
        self.parameters_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        self.parameters_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.parameters_label)
        
        layout.addSpacing(10)
        
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

        self.counter_widget = QLabel(f"Количество фигур: {0}")
        layout.addWidget(self.counter_widget)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
        self.update_input_visibility()
    
    def get_grid_size(self):
        return self.grid_size_input.value()
    
    def get_selected_task(self):
        return self.task_combo.currentText()
    
    def get_variables(self):
        return self.current_variables.copy()
    
    def update_input_visibility(self):
        task = self.get_selected_task()
        
        if task in ["1a", "4.1a"]:
            self.s_widget.setVisible(False)
            self.t_widget.setVisible(False)
        #elif task in ["1b", "4.1b"]:
            #self.s_widget.setVisible(True)
            #self.t_widget.setVisible(True)
        #elif task in ["1c", "4.1c"]:
            #self.s_widget.setVisible(True)
            #self.t_widget.setVisible(False)
        #else:
            #self.s_widget.setVisible(False)
            #self.t_widget.setVisible(False)
    
    def update_parameters_display(self):
        if self.current_task in ["1a", "4.1a"]:
            parameters_text = f"Пункт: {self.current_task}\nn: {self.current_grid_size}"
        #elif self.current_task in ["1b", "4.1b"]:
            #parameters_text = f"Пункт: {self.current_task}\nn: {self.current_grid_size}\ns: {self.current_variables['s']}\nt: {self.current_variables['t']}"
        #elif self.current_task in ["1c", "4.1c"]:
            #parameters_text = f"Пункт: {self.current_task}\nn: {self.current_grid_size}\ns: {self.current_variables['s']}"
        else:
            parameters_text = f"Пункт: {self.current_task}\nn: {self.current_grid_size}"
        
        self.parameters_label.setText(parameters_text)
    
    def update_counter_display(self, counter):
        self.counter_widget.setText(f"Количество фигур: {counter}")

    def apply_settings(self):
        self.current_task = self.get_selected_task()
        self.current_grid_size = self.get_grid_size()
        
        if self.current_task in ["1a", "4.1a"]:
            self.current_variables["s"] = 1
            self.current_variables["t"] = 1
        #elif self.current_task in ["1b", "4.1b"]:
            #self.current_variables["s"] = self.s_input.value()
            #self.current_variables["t"] = self.t_input.value()
        #elif self.current_task in ["1c", "4.1c"]:
            #self.current_variables["s"] = self.s_input.value()
            #self.current_variables["t"] = 1
        else:
            self.current_variables = {"s": 1, "t": 1}
        
        self.update_input_visibility()
        
        self.update_parameters_display()

    def on_task_changed(self):
        self.task_changed.emit()