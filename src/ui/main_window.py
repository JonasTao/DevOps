import sys
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QTabWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QSplitter, QAction,
    QMenuBar, QStatusBar, QToolBar, QLabel, QPushButton
)
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QColor
from PyQt5.QtCore import Qt, QSize
from src.config.config import Config
from src.ui.server_manager import ServerManagerWidget
from src.ui.command_executor import CommandExecutorWidget
from src.ui.file_transfer import FileTransferWidget
from src.ui.task_scheduler import TaskSchedulerWidget
from src.ui.log_viewer import LogViewerWidget
from src.ui.matrix_rain import MatrixRain

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        self.setMinimumSize(1400, 900)
        self.setWindowIcon(QIcon())
        
        self.set_black_theme()
        
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()
        self.create_main_content()
        
        self.setStyleSheet(self.get_hacker_stylesheet())
    
    def set_black_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#0a0a0a"))
        palette.setColor(QPalette.WindowText, QColor("#00ff00"))
        palette.setColor(QPalette.Base, QColor("#0d0d0d"))
        palette.setColor(QPalette.AlternateBase, QColor("#111111"))
        palette.setColor(QPalette.ToolTipBase, QColor("#00ff00"))
        palette.setColor(QPalette.ToolTipText, QColor("#00ff00"))
        palette.setColor(QPalette.Text, QColor("#00ff00"))
        palette.setColor(QPalette.Button, QColor("#1a1a1a"))
        palette.setColor(QPalette.ButtonText, QColor("#00ff00"))
        palette.setColor(QPalette.BrightText, QColor("#ff0000"))
        palette.setColor(QPalette.Link, QColor("#00ff00"))
        palette.setColor(QPalette.Highlight, QColor("#003300"))
        palette.setColor(QPalette.HighlightedText, QColor("#00ff00"))
        self.setPalette(palette)
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #0a0a0a;
                color: #00ff00;
                border-bottom: 1px solid #003300;
            }
            QMenuBar::item {
                padding: 8px 20px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
            QMenuBar::item:selected {
                background-color: #003300;
                color: #00ff00;
            }
            QMenu {
                background-color: #0a0a0a;
                color: #00ff00;
                border: 1px solid #003300;
            }
            QMenu::item {
                padding: 8px 25px;
                font-family: 'Courier New', monospace;
            }
            QMenu::item:selected {
                background-color: #003300;
            }
        """)
        
        file_menu = menubar.addMenu('[文件]')
        exit_action = QAction('[退出]', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu('[视图]')
        refresh_action = QAction('[刷新]', self)
        view_menu.addAction(refresh_action)
        
        help_menu = menubar.addMenu('[帮助]')
        about_action = QAction('[关于]', self)
        help_menu.addAction(about_action)
    
    def create_tool_bar(self):
        toolbar = self.addToolBar('工具栏')
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #0a0a0a;
                border-bottom: 1px solid #003300;
            }
            QToolButton {
                color: #00ff00;
                border: 1px solid #003300;
                padding: 5px 15px;
                font-family: 'Courier New', monospace;
            }
            QToolButton:hover {
                background-color: #003300;
            }
        """)
        
        connect_action = QAction('[连接服务器]', self)
        disconnect_action = QAction('[断开连接]', self)
        toolbar.addActions([connect_action, disconnect_action])
        toolbar.addSeparator()
        
        exec_action = QAction('[执行命令]', self)
        toolbar.addAction(exec_action)
    
    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #0a0a0a;
                color: #00ff00;
                border-top: 1px solid #003300;
                font-family: 'Courier New', monospace;
            }
        """)
        self.status_label = QLabel("[就绪] 系统在线")
        self.status_bar.addWidget(self.status_label)
        
        self.cpu_label = QLabel("CPU: 0%")
        self.mem_label = QLabel("内存: 0%")
        self.status_bar.addPermanentWidget(self.cpu_label)
        self.status_bar.addPermanentWidget(self.mem_label)
    
    def create_main_content(self):
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("""
            QSplitter {
                background-color: #0a0a0a;
            }
            QSplitter::handle {
                background-color: #003300;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #00ff00;
            }
        """)
        
        self.matrix_rain = MatrixRain()
        self.splitter.addWidget(self.matrix_rain)
        self.splitter.setStretchFactor(0, 0)
        
        self.server_manager = ServerManagerWidget()
        self.splitter.addWidget(self.server_manager)
        self.splitter.setStretchFactor(1, 1)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #003300;
                background-color: #0d0d0d;
            }
            QTabBar::tab {
                background-color: #0a0a0a;
                color: #00ff00;
                padding: 10px 25px;
                margin-right: 2px;
                border: 1px solid #003300;
                border-bottom: none;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                letter-spacing: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0d0d0d;
                color: #00ff00;
                border: 1px solid #00ff00;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background-color: #003300;
            }
        """)
        
        self.command_executor = CommandExecutorWidget()
        self.file_transfer = FileTransferWidget()
        self.task_scheduler = TaskSchedulerWidget()
        self.log_viewer = LogViewerWidget()
        
        self.tab_widget.addTab(self.command_executor, "[命令执行]")
        self.tab_widget.addTab(self.file_transfer, "[文件传输]")
        self.tab_widget.addTab(self.task_scheduler, "[任务调度]")
        self.tab_widget.addTab(self.log_viewer, "[日志查看]")
        
        self.splitter.addWidget(self.tab_widget)
        self.splitter.setStretchFactor(2, 4)
        
        self.setCentralWidget(self.splitter)
        
        self.server_manager.server_selected.connect(self.on_server_selected)
    
    def on_server_selected(self, server):
        self.status_label.setText(f"[已选择] {server.name} @ {server.ip}")
        self.command_executor.set_server(server)
        self.file_transfer.set_server(server)
    
    def get_hacker_stylesheet(self):
        return """
            QMainWindow {
                background-color: #0a0a0a;
            }
            QWidget {
                color: #00ff00;
                font-family: 'Courier New', 'Consolas', monospace;
            }
            QLineEdit {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 5px;
                font-family: 'Courier New', monospace;
            }
            QLineEdit:focus {
                border: 1px solid #00ff00;
                background-color: #001100;
            }
            QTextEdit {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                font-family: 'Courier New', monospace;
            }
            QTextEdit:focus {
                border: 1px solid #00ff00;
            }
            QPushButton {
                background-color: #0a0a0a;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 6px 15px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #003300;
                border: 1px solid #00ff00;
            }
            QPushButton:pressed {
                background-color: #00ff00;
                color: #0a0a0a;
            }
            QListWidget {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #002200;
            }
            QListWidget::item:hover {
                background-color: #002200;
            }
            QListWidget::item:selected {
                background-color: #003300;
                color: #00ff00;
            }
            QComboBox {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
            }
            QProgressBar {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
            }
            QProgressBar::chunk {
                background-color: #00ff00;
            }
            QDialog {
                background-color: #0a0a0a;
                border: 1px solid #003300;
            }
            QLabel {
                color: #00ff00;
                font-family: 'Courier New', monospace;
            }
        """
    
    def closeEvent(self, event):
        from src.core.ssh_manager import ssh_manager
        ssh_manager.close_all()
        event.accept()
