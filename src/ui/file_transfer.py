from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QLineEdit, QLabel,
    QProgressBar, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QIcon
from src.core.server import Server
from src.core.ssh_manager import ssh_manager
from src.utils.logger import logger
import os
import paramiko

class SFTPWorker(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, operation, local_path, remote_path, ssh_client):
        super().__init__()
        self.operation = operation
        self.local_path = local_path
        self.remote_path = remote_path
        self.ssh_client = ssh_client
    
    def run(self):
        try:
            sftp = self.ssh_client.open_sftp()
            
            if self.operation == "upload":
                sftp.put(self.local_path, self.remote_path)
            elif self.operation == "download":
                sftp.get(self.remote_path, self.local_path)
            
            sftp.close()
            self.finished_signal.emit(True, f"{self.operation} 完成")
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class FileTransferWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_server = None
        self.current_local_path = os.getcwd()
        self.current_remote_path = "/home"
        self.sftp = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        header_label = QLabel("[文件传输]")
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
        
        self.server_label = QLabel("[未选择服务器]")
        self.server_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.server_label)
        
        splitter_layout = QHBoxLayout()
        splitter_layout.setSpacing(10)
        
        left_panel = QVBoxLayout()
        local_header = QLabel("[本地文件]")
        local_header.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                padding: 5px 0;
            }
        """)
        left_panel.addWidget(local_header)
        
        self.local_path_edit = QLineEdit()
        self.local_path_edit.setText(self.current_local_path)
        self.local_path_edit.setStyleSheet("""
            QLineEdit {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        left_panel.addWidget(self.local_path_edit)
        
        self.local_list = QListWidget()
        self.local_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.local_list.itemDoubleClicked.connect(self.on_local_double_click)
        self.local_list.setStyleSheet("""
            QListWidget {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #002200;
            }
            QListWidget::item:hover {
                background-color: #002200;
            }
            QListWidget::item:selected {
                background-color: #003300;
            }
        """)
        left_panel.addWidget(self.local_list)
        splitter_layout.addLayout(left_panel)
        
        transfer_layout = QVBoxLayout()
        transfer_layout.setSpacing(5)
        
        self.upload_btn = QPushButton("[上传 >>]")
        self.upload_btn.setEnabled(False)
        self.upload_btn.clicked.connect(self.upload_file)
        self.upload_btn.setStyleSheet(self.get_button_style())
        
        self.download_btn = QPushButton("[<< 下载]")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.download_file)
        self.download_btn.setStyleSheet(self.get_button_style())
        
        transfer_layout.addStretch()
        transfer_layout.addWidget(self.upload_btn)
        transfer_layout.addWidget(self.download_btn)
        transfer_layout.addStretch()
        splitter_layout.addLayout(transfer_layout)
        
        right_panel = QVBoxLayout()
        remote_header = QLabel("[远程文件]")
        remote_header.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                padding: 5px 0;
            }
        """)
        right_panel.addWidget(remote_header)
        
        self.remote_path_edit = QLineEdit()
        self.remote_path_edit.setText(self.current_remote_path)
        self.remote_path_edit.setStyleSheet("""
            QLineEdit {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        right_panel.addWidget(self.remote_path_edit)
        
        self.remote_list = QListWidget()
        self.remote_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.remote_list.itemDoubleClicked.connect(self.on_remote_double_click)
        self.remote_list.setStyleSheet("""
            QListWidget {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #002200;
            }
            QListWidget::item:hover {
                background-color: #002200;
            }
            QListWidget::item:selected {
                background-color: #003300;
            }
        """)
        right_panel.addWidget(self.remote_list)
        splitter_layout.addLayout(right_panel)
        
        layout.addLayout(splitter_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                font-family: 'Courier New', monospace;
            }
            QProgressBar::chunk {
                background-color: #00ff00;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        self.refresh_local_btn = QPushButton("[刷新本地]")
        self.refresh_local_btn.clicked.connect(self.load_local_files)
        self.refresh_local_btn.setStyleSheet(self.get_button_style())
        
        self.refresh_remote_btn = QPushButton("[刷新远程]")
        self.refresh_remote_btn.clicked.connect(self.load_remote_files)
        self.refresh_remote_btn.setEnabled(False)
        self.refresh_remote_btn.setStyleSheet(self.get_button_style())
        
        self.browse_btn = QPushButton("[浏览]")
        self.browse_btn.clicked.connect(self.browse_local)
        self.browse_btn.setStyleSheet(self.get_button_style())
        
        bottom_layout.addWidget(self.refresh_local_btn)
        bottom_layout.addWidget(self.refresh_remote_btn)
        bottom_layout.addWidget(self.browse_btn)
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        self.load_local_files()
    
    def get_button_style(self):
        return """
            QPushButton {
                background-color: #0a0a0a;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 5px 12px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #003300;
                border: 1px solid #00ff00;
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
        self.upload_btn.setEnabled(connected)
        self.download_btn.setEnabled(connected)
        self.refresh_remote_btn.setEnabled(connected)
        
        if connected:
            self.load_remote_files()
    
    def load_local_files(self):
        self.local_list.clear()
        try:
            for item in os.listdir(self.current_local_path):
                item_path = os.path.join(self.current_local_path, item)
                is_dir = os.path.isdir(item_path)
                list_item = QListWidgetItem(f"{'[目录]' if is_dir else '[文件]'} {item}")
                list_item.setData(Qt.UserRole, item_path)
                self.local_list.addItem(list_item)
        except Exception as e:
            logger.error(f"加载本地文件失败: {e}")
    
    def load_remote_files(self):
        if not self.current_server or not ssh_manager.is_connected(self.current_server.id):
            return
        
        self.remote_list.clear()
        try:
            ssh = ssh_manager.connections.get(self.current_server.id)
            if ssh:
                stdin, stdout, stderr = ssh.exec_command(f"ls -la {self.current_remote_path}")
                lines = stdout.read().decode('utf-8').strip().split('\n')
                
                for line in lines[1:]:  # 跳过总计行
                    parts = line.split()
                    if len(parts) >= 9:
                        is_dir = parts[0].startswith('d')
                        name = ' '.join(parts[8:])
                        list_item = QListWidgetItem(f"{'[目录]' if is_dir else '[文件]'} {name}")
                        list_item.setData(Qt.UserRole, f"{self.current_remote_path}/{name}")
                        self.remote_list.addItem(list_item)
        except Exception as e:
            logger.error(f"加载远程文件失败: {e}")
            self.remote_list.addItem(QListWidgetItem(f"[错误] {str(e)}"))
    
    def on_local_double_click(self, item):
        path = item.data(Qt.UserRole)
        if os.path.isdir(path):
            self.current_local_path = path
            self.local_path_edit.setText(path)
            self.load_local_files()
    
    def on_remote_double_click(self, item):
        path = item.data(Qt.UserRole)
        if item.text().startswith("[目录]"):
            self.current_remote_path = path
            self.remote_path_edit.setText(path)
            self.load_remote_files()
    
    def upload_file(self):
        selected_items = self.local_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "[警告]", "请先选择要上传的文件")
            return
        
        if not self.current_server or not ssh_manager.is_connected(self.current_server.id):
            QMessageBox.warning(self, "[警告]", "请先连接服务器")
            return
        
        for item in selected_items:
            local_path = item.data(Qt.UserRole)
            if os.path.isfile(local_path):
                filename = os.path.basename(local_path)
                remote_path = f"{self.current_remote_path}/{filename}"
                
                try:
                    ssh = ssh_manager.connections.get(self.current_server.id)
                    sftp = ssh.open_sftp()
                    sftp.put(local_path, remote_path)
                    sftp.close()
                    logger.info(f"上传文件成功: {filename}")
                except Exception as e:
                    logger.error(f"上传文件失败: {e}")
                    QMessageBox.critical(self, "[错误]", f"上传失败: {str(e)}")
        
        self.load_remote_files()
    
    def download_file(self):
        selected_items = self.remote_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "[警告]", "请先选择要下载的文件")
            return
        
        if not self.current_server or not ssh_manager.is_connected(self.current_server.id):
            QMessageBox.warning(self, "[警告]", "请先连接服务器")
            return
        
        for item in selected_items:
            remote_path = item.data(Qt.UserRole)
            if not item.text().startswith("[目录]"):
                filename = os.path.basename(remote_path)
                local_path = os.path.join(self.current_local_path, filename)
                
                try:
                    ssh = ssh_manager.connections.get(self.current_server.id)
                    sftp = ssh.open_sftp()
                    sftp.get(remote_path, local_path)
                    sftp.close()
                    logger.info(f"下载文件成功: {filename}")
                except Exception as e:
                    logger.error(f"下载文件失败: {e}")
                    QMessageBox.critical(self, "[错误]", f"下载失败: {str(e)}")
        
        self.load_local_files()
    
    def browse_local(self):
        path = QFileDialog.getExistingDirectory(self, "[选择目录]", self.current_local_path)
        if path:
            self.current_local_path = path
            self.local_path_edit.setText(path)
            self.load_local_files()
