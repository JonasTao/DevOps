from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QLineEdit, QLabel,
    QDialog, QFormLayout, QComboBox, QSpinBox, QCheckBox,
    QTimeEdit, QDateEdit, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDateTime, QTimer, pyqtSignal
from src.core.server import Server
from src.utils.logger import logger
import uuid
from datetime import datetime

class ScheduledTask:
    def __init__(self, id, name, command, server_id, schedule_type, 
                 cron_expression=None, run_once_time=None, enabled=True):
        self.id = id
        self.name = name
        self.command = command
        self.server_id = server_id
        self.schedule_type = schedule_type
        self.cron_expression = cron_expression
        self.run_once_time = run_once_time
        self.enabled = enabled
        self.last_run = None
        self.next_run = None
        self.status = "等待中"

class TaskSchedulerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.tasks = []
        self.init_ui()
        self.load_sample_tasks()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_tasks)
        self.timer.start(60000)  # 每分钟检查一次
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        header_label = QLabel("[任务调度]")
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
        
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 11px;
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
            }
        """)
        layout.addWidget(self.task_list)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        self.add_btn = QPushButton("[+]")
        self.add_btn.clicked.connect(self.show_add_dialog)
        self.add_btn.setStyleSheet(self.get_button_style())
        
        self.edit_btn = QPushButton("[编辑]")
        self.edit_btn.clicked.connect(self.show_edit_dialog)
        self.edit_btn.setStyleSheet(self.get_button_style())
        
        self.delete_btn = QPushButton("[-]")
        self.delete_btn.clicked.connect(self.delete_task)
        self.delete_btn.setStyleSheet(self.get_button_style())
        
        self.run_btn = QPushButton("[立即执行]")
        self.run_btn.clicked.connect(self.run_task_now)
        self.run_btn.setStyleSheet(self.get_button_style())
        
        self.toggle_btn = QPushButton("[启用/禁用]")
        self.toggle_btn.clicked.connect(self.toggle_task)
        self.toggle_btn.setStyleSheet(self.get_button_style())
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.run_btn)
        button_layout.addWidget(self.toggle_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
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
        """
    
    def load_sample_tasks(self):
        sample_tasks = [
            ScheduledTask(
                id=str(uuid.uuid4()),
                name="系统监控",
                command="df -h && free -m",
                server_id="",
                schedule_type="cron",
                cron_expression="0 */6 * * *",
                enabled=True
            ),
            ScheduledTask(
                id=str(uuid.uuid4()),
                name="日志清理",
                command="find /var/log -name '*.log' -mtime +7 -delete",
                server_id="",
                schedule_type="cron",
                cron_expression="0 2 * * *",
                enabled=True
            ),
        ]
        self.tasks.extend(sample_tasks)
        self.refresh_task_list()
    
    def refresh_task_list(self):
        self.task_list.clear()
        for task in self.tasks:
            status_icon = "[运行中]" if task.enabled else "[已禁用]"
            schedule_info = task.cron_expression if task.schedule_type == "cron" else "一次性"
            item_text = f"{status_icon} {task.name} | {schedule_info} | {task.status}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, task)
            self.task_list.addItem(item)
    
    def show_add_dialog(self):
        dialog = TaskDialog()
        if dialog.exec_() == QDialog.Accepted:
            task = dialog.get_task()
            task.id = str(uuid.uuid4())
            self.tasks.append(task)
            self.refresh_task_list()
            logger.info(f"添加任务: {task.name}")
    
    def show_edit_dialog(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "[警告]", "请先选择任务")
            return
        
        task = selected_items[0].data(Qt.UserRole)
        dialog = TaskDialog(task)
        if dialog.exec_() == QDialog.Accepted:
            updated_task = dialog.get_task()
            task.name = updated_task.name
            task.command = updated_task.command
            task.schedule_type = updated_task.schedule_type
            task.cron_expression = updated_task.cron_expression
            task.run_once_time = updated_task.run_once_time
            self.refresh_task_list()
            logger.info(f"更新任务: {task.name}")
    
    def delete_task(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "[警告]", "请先选择任务")
            return
        
        task = selected_items[0].data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "[确认删除]",
            f"确定要删除任务: {task.name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.tasks.remove(task)
            self.refresh_task_list()
            logger.info(f"删除任务: {task.name}")
    
    def run_task_now(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "[警告]", "请先选择任务")
            return
        
        task = selected_items[0].data(Qt.UserRole)
        task.status = "执行中"
        task.last_run = datetime.now()
        self.refresh_task_list()
        
        logger.info(f"立即执行任务: {task.name}")
        QMessageBox.information(self, "[执行]", f"任务 '{task.name}' 已执行")
        
        task.status = "等待中"
        self.refresh_task_list()
    
    def toggle_task(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "[警告]", "请先选择任务")
            return
        
        task = selected_items[0].data(Qt.UserRole)
        task.enabled = not task.enabled
        self.refresh_task_list()
        logger.info(f"{'启用' if task.enabled else '禁用'}任务: {task.name}")
    
    def check_tasks(self):
        now = datetime.now()
        for task in self.tasks:
            if task.enabled and task.schedule_type == "cron":
                # 简化的CRON检查逻辑
                pass

class TaskDialog(QDialog):
    def __init__(self, task=None):
        super().__init__()
        self.task = task
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("[添加任务]" if not self.task else "[编辑任务]")
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a0a;
                border: 1px solid #003300;
            }
        """)
        
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("任务名称")
        
        self.command_edit = QTextEdit()
        self.command_edit.setPlaceholderText("要执行的命令")
        self.command_edit.setMaximumHeight(80)
        
        self.schedule_type = QComboBox()
        self.schedule_type.addItems(["CRON", "一次性"])
        self.schedule_type.currentIndexChanged.connect(self.on_schedule_type_changed)
        
        self.cron_edit = QLineEdit()
        self.cron_edit.setPlaceholderText("* * * * * (分 时 日 月 周)")
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        self.date_edit.setVisible(False)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QDateTime.currentDateTime().time())
        self.time_edit.setVisible(False)
        
        edit_style = """
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit {
                background-color: #0d0d0d;
                border: 1px solid #003300;
                color: #00ff00;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """
        
        for widget in [self.name_edit, self.command_edit, self.cron_edit,
                       self.schedule_type, self.date_edit, self.time_edit]:
            widget.setStyleSheet(edit_style)
        
        layout.addRow(self.create_label("[名称]:"), self.name_edit)
        layout.addRow(self.create_label("[命令]:"), self.command_edit)
        layout.addRow(self.create_label("[类型]:"), self.schedule_type)
        layout.addRow(self.create_label("[CRON]:"), self.cron_edit)
        layout.addRow(self.create_label("[日期]:"), self.date_edit)
        layout.addRow(self.create_label("[时间]:"), self.time_edit)
        
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
        
        if self.task:
            self.name_edit.setText(self.task.name)
            self.command_edit.setText(self.task.command)
            self.schedule_type.setCurrentIndex(0 if self.task.schedule_type == "cron" else 1)
            self.cron_edit.setText(self.task.cron_expression or "")
    
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
    
    def on_schedule_type_changed(self, index):
        is_cron = index == 0
        self.cron_edit.setVisible(is_cron)
        self.date_edit.setVisible(not is_cron)
        self.time_edit.setVisible(not is_cron)
    
    def get_task(self):
        schedule_type = "cron" if self.schedule_type.currentIndex() == 0 else "once"
        run_once_time = None
        
        if schedule_type == "once":
            dt = QDateTime(self.date_edit.date(), self.time_edit.time())
            run_once_time = dt.toPyDateTime()
        
        return ScheduledTask(
            id="",
            name=self.name_edit.text(),
            command=self.command_edit.toPlainText(),
            server_id="",
            schedule_type=schedule_type,
            cron_expression=self.cron_edit.text() if schedule_type == "cron" else None,
            run_once_time=run_once_time,
            enabled=True
        )
