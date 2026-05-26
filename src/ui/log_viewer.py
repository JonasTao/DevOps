from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QComboBox, QLineEdit, QLabel
)
from PyQt5.QtCore import Qt
from src.utils.logger import logger
from src.config.config import Config
import os

class LogViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        header_label = QLabel("[系统日志]")
        header_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 2px;
                border-bottom: 1px solid #003300;
                padding-bottom: 5px;
            }
        """)
        layout.addWidget(header_label)
        
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        self.level_filter = QComboBox()
        self.level_filter.addItems(["[全部级别]", "[DEBUG]", "[INFO]", "[WARNING]", "[ERROR]", "[CRITICAL]"])
        self.level_filter.currentIndexChanged.connect(self.filter_logs)
        self.level_filter.setStyleSheet("""
            QComboBox {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
            QComboBox QAbstractItemView {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
            }
        """)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索日志...")
        self.search_edit.textChanged.connect(self.filter_logs)
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 1px solid #00ff00;
            }
        """)
        
        self.refresh_btn = QPushButton("[刷新]")
        self.refresh_btn.clicked.connect(self.load_logs)
        self.refresh_btn.setStyleSheet(self.get_button_style())
        
        self.clear_btn = QPushButton("[清空]")
        self.clear_btn.clicked.connect(self.clear_logs)
        self.clear_btn.setStyleSheet(self.get_button_style())
        
        control_layout.addWidget(self.level_filter)
        control_layout.addWidget(self.search_edit)
        control_layout.addWidget(self.refresh_btn)
        control_layout.addWidget(self.clear_btn)
        layout.addLayout(control_layout)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                color: #00ff00;
                font-family: 'Courier New', 'Consolas', monospace;
                font-size: 11px;
                border: 1px solid #003300;
            }
        """)
        layout.addWidget(self.log_text)
        
        self.setLayout(layout)
        self.load_logs()
    
    def get_button_style(self):
        return """
            QPushButton {
                background-color: #0a0a0a;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 5px 15px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #003300;
                border: 1px solid #00ff00;
            }
        """
    
    def load_logs(self):
        self.log_text.clear()
        log_file = Config.LOG_FILE
        
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # 显示最后500行
                    for line in lines[-500:]:
                        self.log_text.append(line.strip())
            else:
                self.log_text.append("[系统] 暂无日志文件")
        except Exception as e:
            self.log_text.append(f"[错误] 读取日志失败: {e}")
        
        self.log_text.moveCursor(self.log_text.textCursor().End)
    
    def filter_logs(self):
        level = self.level_filter.currentText()
        search_text = self.search_edit.text().lower()
        
        self.log_text.clear()
        log_file = Config.LOG_FILE
        
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                    for line in lines[-500:]:
                        line = line.strip()
                        
                        # 级别过滤
                        if level != "[全部级别]":
                            level_clean = level.replace("[", "").replace("]", "")
                            if level_clean not in line:
                                continue
                        
                        # 搜索过滤
                        if search_text and search_text not in line.lower():
                            continue
                        
                        self.log_text.append(line)
        except Exception as e:
            self.log_text.append(f"[错误] 过滤日志失败: {e}")
        
        self.log_text.moveCursor(self.log_text.textCursor().End)
    
    def clear_logs(self):
        self.log_text.clear()
        self.log_text.append("[系统] 日志已清空")
