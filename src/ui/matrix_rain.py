from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer, QPointF
import random

class MatrixRain(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 800)
        self.setStyleSheet("background-color: black;")
        
        self.characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()_+-=[]{}|;:,.<>?"
        self.columns = []
        self.column_width = 20
        self.font_size = 14
        
        self.init_columns()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)
    
    def init_columns(self):
        num_columns = self.width() // self.column_width
        for _ in range(num_columns):
            self.columns.append({
                'chars': [self.get_random_char() for _ in range(self.height() // self.font_size)],
                'speed': random.randint(1, 3),
                'position': random.randint(-self.height() // self.font_size, 0),
                'bright_char': random.randint(0, self.height() // self.font_size - 1)
            })
    
    def get_random_char(self):
        return self.characters[random.randint(0, len(self.characters) - 1)]
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for col_idx, column in enumerate(self.columns):
            x = col_idx * self.column_width
            
            for row_idx, char in enumerate(column['chars']):
                y = row_idx * self.font_size + column['position'] * self.font_size
                
                if 0 <= y < self.height():
                    if row_idx == column['bright_char']:
                        painter.setPen(QColor("#00ff00"))
                        painter.setFont(QFont("Courier New", self.font_size, QFont.Bold))
                    elif row_idx <= column['bright_char'] + 5 and row_idx > column['bright_char']:
                        alpha = 255 - (row_idx - column['bright_char']) * 40
                        painter.setPen(QColor(0, 255, 0, alpha))
                        painter.setFont(QFont("Courier New", self.font_size - 2))
                    else:
                        painter.setPen(QColor("#003300"))
                        painter.setFont(QFont("Courier New", self.font_size - 2))
                    
                    painter.drawText(x, y, char)
        
        self.update_columns()
    
    def update_columns(self):
        for column in self.columns:
            column['position'] += column['speed']
            
            if column['position'] * self.font_size > self.height():
                column['position'] = -10
                column['bright_char'] = random.randint(0, self.height() // self.font_size - 1)
            
            if random.random() < 0.05:
                idx = random.randint(0, len(column['chars']) - 1)
                column['chars'][idx] = self.get_random_char()
    
    def resizeEvent(self, event):
        self.init_columns()
        super().resizeEvent(event)
