import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QBrush
from PyQt6.QtCore import Qt

class BackgroundImageWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.image = QPixmap(image_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        aspect_ratio = self.image.width() / self.image.height()
        target_rect = self.rect()

        # Shrink the target_rect while maintaining aspect ratio
        new_width = int(target_rect.width() * 0.9)
        new_height = int(new_width / aspect_ratio)

        if new_height > target_rect.height():
            # Shrink based on height instead
            new_height = int(target_rect.height() * 0.9)
            new_width = int(new_height * aspect_ratio)

        # Center the resized image
        target_rect.setWidth(new_width)
        target_rect.setHeight(new_height)
        target_rect.moveCenter(self.rect().center())

        painter.drawPixmap(target_rect, self.image)
        painter.end()

