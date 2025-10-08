import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
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
        
    def apply_settings(self):
        grid_size = self.settings_panel.get_grid_size()
        self.grid_widget.set_grid_size(grid_size)