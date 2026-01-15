import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout
)
from PyQt5.QtCore import Qt


class HelloWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hello PyQt5")
        self.resize(1920, 1080)

        label = QLabel("Hello, PyQt5!")
        label.setAlignment(Qt.AlignCenter)

        button = QPushButton("Click me")
        button.clicked.connect(self.on_click)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(button)

        self.setLayout(layout)

    def on_click(self):
        print("Button clicked!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = HelloWindow()
    win.show()
    sys.exit(app.exec_())
