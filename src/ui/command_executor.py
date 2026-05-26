from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QComboBox, QProgressBar, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QTextCursor, QColor
from src.core.server import Server
from src.core.ssh_manager import ssh_manager
from src.utils.logger import logger

class CommandExecutorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_server = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        header_layout = QHBoxLayout()
        self.server_label = QLabel("[未选择服务器]")
        self.server_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 1px;
            }
        """)
        header_layout.addWidget(self.server_label)
        header_layout.addStretch()
        
        self.status_indicator = QLabel("[离线]")
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #ff0000;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        header_layout.addWidget(self.status_indicator)
        layout.addLayout(header_layout)
        
        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText("输入命令...")
        self.command_input.setMaximumHeight(60)
        self.command_input.setStyleSheet("""
            QTextEdit {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
            QTextEdit:focus {
                border: 1px solid #00ff00;
            }
        """)
        layout.addWidget(self.command_input)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.exec_btn = QPushButton("[执行]")
        self.exec_btn.clicked.connect(self.execute_command)
        self.exec_btn.setEnabled(False)
        self.exec_btn.setStyleSheet(self.get_button_style())
        
        self.clear_btn = QPushButton("[清空]")
        self.clear_btn.clicked.connect(self.clear_output)
        self.clear_btn.setStyleSheet(self.get_button_style())
        
        self.quick_commands = QComboBox()
        self.quick_commands.addItems([
            "[快捷命令]",
            "ls -la",
            "df -h",
            "free -m",
            "top -bn1",
            "netstat -tlnp",
            "ps aux | grep python",
            "cat /etc/os-release"
        ])
        self.quick_commands.currentTextChanged.connect(self.on_quick_command)
        self.quick_commands.setStyleSheet("""
            QComboBox {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
            QComboBox::drop-down {
                border: 1px solid #003300;
            }
            QComboBox QAbstractItemView {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                font-family: 'Courier New', monospace;
            }
        """)
        
        button_layout.addWidget(self.exec_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.quick_commands)
        layout.addLayout(button_layout)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                color: #00ff00;
                font-family: 'Courier New', 'Consolas', monospace;
                font-size: 11px;
                border: 1px solid #003300;
            }
        """)
        layout.addWidget(self.output_text)
        
        self.setLayout(layout)
        
        self.append_output("[系统] AutoOps 命令终端 v1.0", "system")
        self.append_output("[就绪] 等待命令...\n", "system")
    
    def get_button_style(self):
        return """
            QPushButton {
                background-color: #0a0a0a;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 6px 20px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background-color: #003300;
                border: 1px solid #00ff00;
            }
            QPushButton:pressed {
                background-color: #00ff00;
                color: #0a0a0a;
            }
            QPushButton:disabled {
                color: #003300;
                border-color: #002200;
            }
        """
    
    def set_server(self, server):
        self.current_server = server
        self.server_label.setText(f"[服务器] {server.name} @ {server.ip}")
        
        connected = ssh_manager.is_connected(server.id)
        self.exec_btn.setEnabled(connected)
        
        if connected:
            self.status_indicator.setText("[在线]")
            self.status_indicator.setStyleSheet("color: #00ff00; font-family: 'Courier New', monospace; font-size: 11px;")
            self.append_output(f"[已连接] 连接到 {server.name}", "success")
        else:
            self.status_indicator.setText("[离线]")
            self.status_indicator.setStyleSheet("color: #ff0000; font-family: 'Courier New', monospace; font-size: 11px;")
    
    def execute_command(self):
        if not self.current_server:
            self.append_output("[错误] 未选择服务器", "error")
            return
        
        command = self.command_input.toPlainText().strip()
        if not command:
            self.append_output("[错误] 请先输入命令", "error")
            return
        
        self.append_output(f"{self.current_server.name}@${command}", "command")
        
        success, result = ssh_manager.execute_command(self.current_server.id, command)
        
        if success:
            self.append_output(result, "success")
            logger.info(f"命令执行成功: {command}")
        else:
            self.append_output(result, "error")
            logger.error(f"命令执行失败: {command}")
    
    def on_quick_command(self, text):
        if text != "[快捷命令]":
            self.command_input.setText(text)
    
    def append_output(self, text, style="normal"):
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        if style == "command":
            fmt = self.output_text.currentCharFormat()
            fmt.setForeground(QColor("#00ffff"))
            cursor.insertText(text + "\n", fmt)
        elif style == "success":
            fmt = self.output_text.currentCharFormat()
            fmt.setForeground(QColor("#00ff00"))
            cursor.insertText(text + "\n", fmt)
        elif style == "error":
            fmt = self.output_text.currentCharFormat()
            fmt.setForeground(QColor("#ff0000"))
            cursor.insertText(text + "\n", fmt)
        elif style == "system":
            fmt = self.output_text.currentCharFormat()
            fmt.setForeground(QColor("#00ffff"))
            cursor.insertText(text + "\n", fmt)
        else:
            cursor.insertText(text + "\n")
        
        self.output_text.setTextCursor(cursor)
        self.output_text.ensureCursorVisible()
    
    def clear_output(self):
        self.output_text.clear()
        self.command_input.clear()
        self.append_output("[系统] 终端已清空", "system")
        self.append_output("[就绪] 等待命令...\n", "system")
