import sys
import json
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                               QMenuBar, QMenu, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from widgets.grid_widget import GridWidget
from widgets.settings_panel import SettingsPanel
from utils.constants import Constants
from ui.help_windows import HelpDialog, HelpWindow


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
        
        help_menu = menubar.addMenu('Помощь')
        help_action = help_menu.addAction('Помощь')
        help_action.triggered.connect(self.show_help)
        
        condition_menu = menubar.addMenu('Условие')
        condition_action = condition_menu.addAction('Условие')
        condition_action.triggered.connect(self.show_condition)
        
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
    
    def show_help(self):
        help_dialog = HelpDialog("Помощь", HelpWindow.get_help_content(), self)
        help_dialog.exec()
    
    def show_condition(self):
        condition_dialog = HelpDialog("Условие задачи", HelpWindow.get_condition_content(), self)
        condition_dialog.exec()
        
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
    
    def has_figures(self):
        return len(self.grid_widget.placed_figures) > 0 or len(self.grid_widget.placed_cells) > 0
    
    def closeEvent(self, event):
        if not self.has_figures():
            event.accept()
            return
        
        reply = QMessageBox(self)
        reply.setWindowTitle("Подтверждение выхода")
        reply.setIcon(QMessageBox.Question)
        reply.setText("На поле есть размещенные фигуры. Вы хотите сохранить перед выходом?")
        
        cancel_button = reply.addButton("Отмена", QMessageBox.RejectRole)
        exit_button = reply.addButton("Выйти", QMessageBox.DestructiveRole)
        save_exit_button = reply.addButton("Сохранить и выйти", QMessageBox.AcceptRole)
        
        reply.setDefaultButton(save_exit_button)
        
        reply.exec()
        
        clicked_button = reply.clickedButton()
        
        if clicked_button == cancel_button:
            event.ignore()
        elif clicked_button == exit_button:
            event.accept()
        elif clicked_button == save_exit_button:
            if self.save_file(exit_after_save=True):
                event.accept()
            else:
                event.ignore()
    
    def save_file(self, exit_after_save=False):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                'Сохранить состояние', 
                '', 
                'JSON Files (*.json);;All Files (*)'
            )
            
            if not file_path:
                return False
            
            if not file_path.endswith('.json'):
                file_path += '.json'
            
            # Конвертируем данные для сохранения
            data = {
                'grid_size': self.grid_widget.grid_size,
                'current_task': self.grid_widget.current_task,
                'variables': self.grid_widget.variables,
                'placed_figures': [
                    [[list(coord), cell_type] for coord, cell_type in figure] 
                    for figure in self.grid_widget.placed_figures
                ],
                'placed_cells': [
                    [list(coord), cell_type] for coord, cell_type in self.grid_widget.placed_cells
                ],
                'forbidden_zones': [
                    [list(coord), cell_type] for coord, cell_type in self.grid_widget.forbidden_zones
                ],
                'current_rotation': self.grid_widget.current_rotation
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            if not exit_after_save:
                QMessageBox.information(self, 'Успех', 'Файл успешно сохранен!')
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось сохранить файл: {str(e)}')
            return False

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
                
                # Конвертируем загруженные данные
                self.grid_widget.grid_size = data['grid_size']
                self.grid_widget.current_task = data['current_task']
                self.grid_widget.variables = data['variables']
                
                # Конвертируем фигуры
                self.grid_widget.placed_figures = [
                    [((coord[0], coord[1]), cell_type) for coord, cell_type in figure] 
                    for figure in data['placed_figures']
                ]
                
                # Конвертируем запретные зоны
                self.grid_widget.forbidden_zones = [
                    ((coord[0], coord[1]), cell_type) for coord, cell_type in data['forbidden_zones']
                ]
                
                self.grid_widget.current_rotation = data['current_rotation']
                
                if 'placed_cells' in data:
                    self.grid_widget.placed_cells = set(
                        ((coord[0], coord[1]), cell_type) for coord, cell_type in data['placed_cells']
                    )
                else:
                    self.grid_widget.placed_cells = set()
                
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