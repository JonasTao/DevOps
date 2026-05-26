from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QLineEdit, QLabel,
    QDialog, QFormLayout, QComboBox, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QColor
from src.core.server import Server, ServerStatus
from src.core.ssh_manager import ssh_manager
from src.utils.logger import logger
import uuid

class ServerManagerWidget(QWidget):
    server_selected = pyqtSignal(Server)
    
    def __init__(self):
        super().__init__()
        self.servers = []
        self.init_ui()
        self.load_sample_servers()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        header_label = QLabel("[服务器列表]")
        header_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
                border-bottom: 1px solid #003300;
                padding-bottom: 5px;
                letter-spacing: 2px;
            }
        """)
        layout.addWidget(header_label)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("搜索服务器...")
        self.search_bar.textChanged.connect(self.filter_servers)
        self.search_bar.setStyleSheet("""
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
            QLineEdit::placeholder {
                color: #003300;
            }
        """)
        layout.addWidget(self.search_bar)
        
        self.server_list = QListWidget()
        self.server_list.itemClicked.connect(self.on_server_click)
        self.server_list.setStyleSheet("""
            QListWidget {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #002200;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
            QListWidget::item:hover {
                background-color: #002200;
            }
            QListWidget::item:selected {
                background-color: #003300;
                color: #00ff00;
            }
        """)
        layout.addWidget(self.server_list)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(3)
        
        self.add_btn = QPushButton("[+]")
        self.add_btn.clicked.connect(self.show_add_dialog)
        self.add_btn.setStyleSheet(self.get_button_style())
        
        self.edit_btn = QPushButton("[编辑]")
        self.edit_btn.clicked.connect(self.show_edit_dialog)
        self.edit_btn.setStyleSheet(self.get_button_style())
        
        self.delete_btn = QPushButton("[-]")
        self.delete_btn.clicked.connect(self.delete_server)
        self.delete_btn.setStyleSheet(self.get_button_style())
        
        self.connect_btn = QPushButton("[连接]")
        self.connect_btn.clicked.connect(self.connect_server)
        self.connect_btn.setStyleSheet(self.get_button_style())
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.connect_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_button_style(self):
        return """
            QPushButton {
                background-color: #0a0a0a;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 4px 8px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
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
        """
    
    def load_sample_servers(self):
        sample_servers = [
            Server(id=str(uuid.uuid4()), name="生产服务器-01", ip="192.168.1.101", username="root", description="主生产环境"),
            Server(id=str(uuid.uuid4()), name="测试服务器-01", ip="192.168.1.102", username="admin", description="测试环境"),
            Server(id=str(uuid.uuid4()), name="开发服务器-01", ip="192.168.1.103", username="dev", description="开发环境"),
        ]
        self.servers.extend(sample_servers)
        self.refresh_server_list()
    
    def refresh_server_list(self):
        self.server_list.clear()
        for server in self.servers:
            status_icon = "[在线]" if server.status == ServerStatus.ONLINE else "[离线]"
            item = QListWidgetItem(f"{status_icon} {server.name}")
            item.setData(Qt.UserRole, server)
            
            if server.status == ServerStatus.ONLINE:
                item.setForeground(QColor("#00ff00"))
            elif server.status == ServerStatus.OFFLINE:
                item.setForeground(QColor("#ff0000"))
            elif server.status == ServerStatus.CONNECTING:
                item.setForeground(QColor("#ffff00"))
            
            self.server_list.addItem(item)
    
    def filter_servers(self, text):
        for i in range(self.server_list.count()):
            item = self.server_list.item(i)
            server = item.data(Qt.UserRole)
            match = text.lower() in server.name.lower() or text.lower() in server.ip.lower()
            item.setHidden(not match)
    
    def on_server_click(self, item):
        server = item.data(Qt.UserRole)
        self.server_selected.emit(server)
    
    def show_add_dialog(self):
        dialog = ServerDialog()
        if dialog.exec_() == QDialog.Accepted:
            server = dialog.get_server()
            server.id = str(uuid.uuid4())
            self.servers.append(server)
            self.refresh_server_list()
            logger.info(f"添加服务器: {server.name}")
    
    def show_edit_dialog(self):
        selected_items = self.server_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "[警告]", "请先选择服务器")
            return
        
        server = selected_items[0].data(Qt.UserRole)
        dialog = ServerDialog(server)
        if dialog.exec_() == QDialog.Accepted:
            updated_server = dialog.get_server()
            server.name = updated_server.name
            server.ip = updated_server.ip
            server.port = updated_server.port
            server.username = updated_server.username
            server.password = updated_server.password
            server.private_key_path = updated_server.private_key_path
            server.description = updated_server.description
            self.refresh_server_list()
            logger.info(f"更新服务器: {server.name}")
    
    def delete_server(self):
        selected_items = self.server_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "[警告]", "请先选择服务器")
            return
        
        item = selected_items[0]
        server = item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "[确认删除]", 
            f"确定要删除服务器: {server.name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            ssh_manager.disconnect(server.id)
            self.servers.remove(server)
            self.refresh_server_list()
            logger.info(f"删除服务器: {server.name}")
    
    def connect_server(self):
        selected_items = self.server_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "[警告]", "请先选择服务器")
            return
        
        server = selected_items[0].data(Qt.UserRole)
        
        if ssh_manager.is_connected(server.id):
            ssh_manager.disconnect(server.id)
            server.status = ServerStatus.OFFLINE
            self.connect_btn.setText("[连接]")
        else:
            server.status = ServerStatus.CONNECTING
            self.refresh_server_list()
            
            if ssh_manager.connect(server):
                self.connect_btn.setText("[断开]")
            else:
                self.connect_btn.setText("[连接]")
        
        self.refresh_server_list()

class ServerDialog(QDialog):
    def __init__(self, server=None):
        super().__init__()
        self.server = server
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("[添加服务器]" if not self.server else "[编辑服务器]")
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a0a;
                border: 1px solid #003300;
            }
        """)
        
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("服务器名称")
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("IP地址")
        self.port_edit = QLineEdit()
        self.port_edit.setText("22")
        self.username_edit = QLineEdit()
        self.username_edit.setText("root")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("密码")
        self.private_key_edit = QLineEdit()
        self.private_key_edit.setPlaceholderText("私钥路径")
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("描述")
        
        edit_style = """
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
        """
        
        for widget in [self.name_edit, self.ip_edit, self.port_edit, 
                       self.username_edit, self.password_edit, 
                       self.private_key_edit, self.description_edit]:
            widget.setStyleSheet(edit_style)
        
        layout.addRow(self.create_label("[名称]:"), self.name_edit)
        layout.addRow(self.create_label("[IP]:"), self.ip_edit)
        layout.addRow(self.create_label("[端口]:"), self.port_edit)
        layout.addRow(self.create_label("[用户名]:"), self.username_edit)
        layout.addRow(self.create_label("[密码]:"), self.password_edit)
        layout.addRow(self.create_label("[私钥]:"), self.private_key_edit)
        layout.addRow(self.create_label("[描述]:"), self.description_edit)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("[确定]")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("[取消]")
        cancel_btn.clicked.connect(self.reject)
        
        btn_style = """
            QPushButton {
                background-color: #0a0a0a;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 6px 15px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #003300;
                border: 1px solid #00ff00;
            }
        """
        ok_btn.setStyleSheet(btn_style)
        cancel_btn.setStyleSheet(btn_style)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
        
        if self.server:
            self.name_edit.setText(self.server.name)
            self.ip_edit.setText(self.server.ip)
            self.port_edit.setText(str(self.server.port))
            self.username_edit.setText(self.server.username)
            self.password_edit.setText(self.server.password)
            self.private_key_edit.setText(self.server.private_key_path)
            self.description_edit.setText(self.server.description)
    
    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        return label
    
    def get_server(self):
        return Server(
            id="",
            name=self.name_edit.text(),
            ip=self.ip_edit.text(),
            port=int(self.port_edit.text()),
            username=self.username_edit.text(),
            password=self.password_edit.text(),
            private_key_path=self.private_key_edit.text(),
            description=self.description_edit.text()
        )
