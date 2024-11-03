from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsPixmapItem, QGraphicsScene
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from ui_form import Ui_MainWindow
from customGraphicsView import ImageGraphicsView
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Create an instance of ImageGraphicsView without adding it to a layout
        self.image_container = ImageGraphicsView(self)
        
        # Set the geometry to match the original image container's size and position
        self.image_container.setGeometry(self.ui.imageContainer.geometry())

        # Remove the original imageContainer widget (if it's no longer needed)
        self.ui.imageContainer.setParent(None)

        # Set up a QGraphicsScene
        self.scene = QGraphicsScene(self)
        self.image_container.setScene(self.scene)

        # Connect the button to open image dialog
        self.ui.uploadButton.clicked.connect(self.open_image_dialog)

    def open_image_dialog(self):
        # Show file dialog with image filter
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Image", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            # Load the image and display it in the QGraphicsView
            pixmap = QPixmap(file_path)
            self.display_image(pixmap)

    def display_image(self, pixmap):
        # Clear any existing items in the scene
        self.scene.clear()

        # Create a QGraphicsPixmapItem with the selected image and add it to the scene
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)

        # Fit the image to the QGraphicsView initially
        self.image_container.fitInView(pixmap_item, Qt.KeepAspectRatio)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())