from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsPixmapItem, QGraphicsScene, QMessageBox, QGraphicsEllipseItem, QGraphicsItem, QGraphicsRectItem
from PySide6.QtGui import QPixmap, QImage, QPen, QMouseEvent, QPainter, QRegion, QPainterPath
from PySide6.QtCore import Qt, QRectF
from ui_form import Ui_MainWindow
from customGraphicsView import ImageGraphicsView
import sys
import cv2
import numpy as np

class ResizeHandle(QGraphicsRectItem):
    def __init__(self, parent=None, position=None):
        super().__init__(-5, -5, 10, 10, parent)
        self.setBrush(Qt.black)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)  # Allow direct moving
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setCursor(Qt.SizeFDiagCursor)
        self.position = position  # Position can be 'topLeft', 'topRight', 'bottomLeft', 'bottomRight'
        self.resizing = False

    def mousePressEvent(self, event: QMouseEvent):
        self.resizing = True
        self.setCursor(Qt.SizeFDiagCursor)
        self.initial_pos = event.scenePos()
        self.initial_rect = self.parentItem().rect()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.resizing = False
        self.setCursor(Qt.SizeFDiagCursor)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.resizing:
            parent = self.parentItem()
            rect = parent.rect()

            delta = event.scenePos() - self.initial_pos
            if self.position == 'topLeft':
                rect.setTopLeft(self.initial_rect.topLeft() + delta)
            elif self.position == 'topRight':
                rect.setTopRight(self.initial_rect.topRight() + delta)
            elif self.position == 'bottomLeft':
                rect.setBottomLeft(self.initial_rect.bottomLeft() + delta)
            elif self.position == 'bottomRight':
                rect.setBottomRight(self.initial_rect.bottomRight() + delta)

            # Apply the new rect to the ellipse
            parent.prepareGeometryChange()
            parent.setRect(rect)
            parent.update_handles()

        super().mouseMoveEvent(event)

class EllipseItem(QGraphicsEllipseItem):
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setPen(QPen(Qt.red, 2))


        self.handles = {
                    'topLeft': ResizeHandle(self, 'topLeft'),
                    'topRight': ResizeHandle(self, 'topRight'),
                    'bottomLeft': ResizeHandle(self, 'bottomLeft'),
                    'bottomRight': ResizeHandle(self, 'bottomRight')
                }
        self.update_handles()

    def update_handles(self):
        rect = self.rect()
        self.handles['topLeft'].setPos(rect.topLeft())
        self.handles['topRight'].setPos(rect.topRight())
        self.handles['bottomLeft'].setPos(rect.bottomLeft())
        self.handles['bottomRight'].setPos(rect.bottomRight())

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.update_handles()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.update_handles()
        return super().itemChange(change, value)

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

        # Connect the analyze button to process the image
        self.ui.analyzeButton.clicked.connect(self.process_image)

        # Connect the crop button to enable ellipse drawing
        self.ui.cropButton.clicked.connect(self.enable_ellipse_drawing)

        # Connect the save button to save the cropped image
        self.ui.saveButton.clicked.connect(self.save_cropped_image)

        self.pixmap = None
        self.file_path = None
        self.ellipse_item = None
        self.image = None
        self.image_item = None
        self.drawing_enabled = False

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
            self.file_path = file_path
            pixmap = QPixmap(file_path)
            self.display_image(pixmap)

    def enable_ellipse_drawing(self):
        if self.image_item:
            self.drawing_enabled = True
            rect = QRectF(0, 0, 100, 100)
            self.ellipse_item = EllipseItem(rect)
            self.scene.addItem(self.ellipse_item)

    def display_image(self, pixmap):
        # Clear any existing items in the scene
        self.scene.clear()

        # Create a QGraphicsPixmapItem with the selected image and add it to the scene
        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.image_item)

        # Fit the image to the QGraphicsView initially
        self.image_container.fitInView(self.image_item, Qt.KeepAspectRatio)

        # Store the pixmap
        self.pixmap = pixmap

    def process_image(self):
        if self.pixmap is None:
            QMessageBox.information(self, "Error", "No image loaded")
            return

        image = cv2.imread(self.file_path, cv2.IMREAD_GRAYSCALE)

        if image is None:
            QMessageBox.information(self, "Error", "Error converting image")
            return

            # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (11, 11), 0)

            # Apply a binary threshold to the image
        _, thresholded = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY_INV)

            # Use morphological operations to enhance the image
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        morphed = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel)

            # Create a mask to ignore black borders
        mask = cv2.inRange(image, 1, 255)  # Mask where the image is not black

            # Apply the mask to the morphed image
        morphed = cv2.bitwise_and(morphed, morphed, mask=mask)

            # Find contours in the thresholded image
        contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Filter contours by area to count smaller blobs
        min_area = 10  # Minimum area of a contour to be considered a colony
        filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

            # Draw contours on the original image
        output = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(output, filtered_contours, -1, (0, 255, 0), 2)

            # Count the number of colonies
        colony_count = len(filtered_contours)

            # Show the colony count in a message box
        QMessageBox.information(self, "Colony Count", f'Number of colonies: {colony_count}')

            # Convert the processed image to QImage
        height, width, channel = output.shape
        bytes_per_line = 3 * width
        q_image = QImage(output.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Convert QImage to QPixmap and display it
        pixmap = QPixmap.fromImage(q_image)
        self.display_image(pixmap)

    def capture_ellipse_area(self):
        if self.pixmap is None or self.ellipse_item is None:
            QMessageBox.information(self, "Error", "No image or ellipse defined")
            return None

            # Convert QPixmap to QImage
        q_image = self.pixmap.toImage()

            # Get the ellipse's geometry in scene coordinates
        rect = self.ellipse_item.mapRectToScene(self.ellipse_item.rect())
        center = (int(rect.center().x()), int(rect.center().y()))
        radius_x = int(rect.width() / 2)
        radius_y = int(rect.height() / 2)

            # Create an elliptical mask using QPainterPath
        path = QPainterPath()
        path.addEllipse(center[0] - radius_x, center[1] - radius_y, 2 * radius_x, 2 * radius_y)

            # Apply the mask to the image
        result = QImage(q_image.size(), QImage.Format_ARGB32)
        result.fill(Qt.transparent)

        painter = QPainter(result)
        painter.setClipPath(path)
        painter.drawImage(0, 0, q_image)
        painter.end()

        return result

    def save_cropped_image(self):
        cropped_image = self.capture_ellipse_area()
        if cropped_image is None:
            return

        # Save the QImage to a file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            cropped_image.save(file_path)
            QMessageBox.information(self, "Success", f"Image saved to {file_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
