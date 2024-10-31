import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

# Yes, this is Chat GPT code
class App(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the window
        self.setWindowTitle("Colony Counter")
        self.setGeometry(100, 100, 300, 200)  # (x, y, width, height)

        # Create a layout and widgets
        layout = QVBoxLayout()

        # Create a label
        self.label = QLabel("Hello, welcome to the app!")
        layout.addWidget(self.label)

        # Create a button
        self.button = QPushButton("Click Me")
        self.button.clicked.connect(self.on_button_click)  # Connect button click event
        layout.addWidget(self.button)

        # Set the layout for the window
        self.setLayout(layout)

    def on_button_click(self):
        # Change the label text when the button is clicked
        self.label.setText("Button clicked!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())