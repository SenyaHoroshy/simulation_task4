import sys
import json
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                               QMenuBar, QMenu, QFileDialog, QMessageBox)
from widgets.grid_widget import GridWidget
from widgets.settings_panel import SettingsPanel
from utils.constants import Constants


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(Constants.APP_NAME)
        self.setGeometry(100, 100, Constants.DEFAULT_WINDOW_WIDTH, Constants.DEFAULT_WINDOW_HEIGHT)
        
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Файл')
        
        save_action = file_menu.addAction('Сохранить как...')
        save_action.triggered.connect(self.save_file)
        
        load_action = file_menu.addAction('Загрузить...')
        load_action.triggered.connect(self.load_file)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)

        self.settings_panel = SettingsPanel()
        main_layout.addWidget(self.settings_panel)

        self.grid_widget = GridWidget()
        main_layout.addWidget(self.grid_widget)
        
    def connect_signals(self):
        self.settings_panel.apply_button.clicked.connect(self.apply_settings)
        self.settings_panel.task_changed.connect(self.on_task_changed)
        self.grid_widget.figures_count_changed.connect(self.settings_panel.update_counter_display)
        
    def apply_settings(self):
        self.settings_panel.apply_settings()
        
        grid_size = self.settings_panel.current_grid_size
        selected_task = self.settings_panel.current_task
        variables = self.settings_panel.get_variables()
        
        self.grid_widget.set_grid_size(grid_size)
        self.grid_widget.set_task(selected_task)
        self.grid_widget.set_variables(variables)

        self.settings_panel.update_input_visibility()
    
    def on_task_changed(self):
        self.settings_panel.update_input_visibility()
    
    def save_file(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                'Сохранить состояние', 
                '', 
                'JSON Files (*.json);;All Files (*)'
            )
            
            if file_path:
                if not file_path.endswith('.json'):
                    file_path += '.json'
                
                data = {
                    'grid_size': self.grid_widget.grid_size,
                    'current_task': self.grid_widget.current_task,
                    'variables': self.grid_widget.variables,
                    'placed_figures': self.grid_widget.placed_figures,
                    'forbidden_zones': self.grid_widget.forbidden_zones,
                    'current_rotation': self.grid_widget.current_rotation
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, 'Успех', 'Файл успешно сохранен!')
                
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось сохранить файл: {str(e)}')
    
    def load_file(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                'Загрузить состояние', 
                '', 
                'JSON Files (*.json);;All Files (*)'
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                required_fields = ['grid_size', 'current_task', 'variables', 
                                 'placed_figures', 'forbidden_zones', 'current_rotation']
                
                for field in required_fields:
                    if field not in data:
                        raise ValueError(f'Отсутствует обязательное поле: {field}')
                
                self.grid_widget.grid_size = data['grid_size']
                self.grid_widget.current_task = data['current_task']
                self.grid_widget.variables = data['variables']
                self.grid_widget.placed_figures = data['placed_figures']
                self.grid_widget.forbidden_zones = data['forbidden_zones']
                self.grid_widget.current_rotation = data['current_rotation']
                
                self.settings_panel.task_combo.setCurrentText(data['current_task'])
                self.settings_panel.grid_size_input.setValue(data['grid_size'])
                
                self.grid_widget.update_current_figure()
                self.grid_widget.update_figures_count()
                self.grid_widget.update()
                
                self.settings_panel.current_task = data['current_task']
                self.settings_panel.current_grid_size = data['grid_size']
                self.settings_panel.current_variables = data['variables']
                self.settings_panel.update_parameters_display()
                
                QMessageBox.information(self, 'Успех', 'Файл успешно загружен!')
                
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить файл: {str(e)}')