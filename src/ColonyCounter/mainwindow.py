from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsPixmapItem, QGraphicsScene, QMessageBox, QGraphicsEllipseItem, QGraphicsItem, QGraphicsRectItem, QSlider, QInputDialog
from PySide6.QtGui import QPixmap, QImage, QPen, QMouseEvent, QPainter, QRegion, QPainterPath
from PySide6.QtCore import Qt, QRectF
from ui_form import Ui_MainWindow
from customGraphicsView import ImageGraphicsView
import sys
import cv2
import numpy as np
import imagej
import scyjava as sj
import os
from sklearn.cluster import DBSCAN
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
from skimage.morphology import label






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
        sj.config.add_option('-Xmx1g')
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ij = imagej.init('sc.fiji:fiji', headless=False)


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
            QMessageBox.information(None, "Error", "No image loaded")
            return

        # Convert QPixmap to QImage
        qimage = self.pixmap.toImage()

        # Convert QImage to numpy array
        width = qimage.width()
        height = qimage.height()
        channels = 4  # Assuming RGBA format
        ptr = qimage.bits()
        arr = np.array(ptr).reshape(height, width, channels)
        if arr.shape[2] == 4:
            arr = arr[:, :, :3].dot([0.299, 0.587, 0.114])  # Convert to grayscale
        arr = np.clip(arr, 0, 255).astype(np.uint8)
        # Convert numpy array to ImagePlus object
        imp = self.ij.py.to_java(arr)

      # Show the image in ImageJ
        self.ij.ui().show(imp)

      # Run commands in ImageJ
        self.ij.py.run_macro("run('8-bit');",)  # Convert to 8-bit
        self.ij.py.run_macro("run('Threshold...');",)
        lower_threshold, ok1 = QInputDialog.getInt(None, "Enter Lower Threshold", "Lower Threshold:", 0, 0, 255, 1)
        self.ij.py.run_macro("run('Fill Holes');",)
        self.ij.py.run_macro("run('Convert to Mask');",)
        self.ij.py.run_macro("run('Watershed');",)  # Apply watershed
        self.ij.py.run_macro("run('Remove Outliers...', 'radius=2 threshold=50 which=Bright');",)
        self.ij.py.run_macro("run('Despeckle');",)
      # Analyze particles with specific settings
        self.ij.py.run_macro("run('Analyze Particles...', 'size=170-50000 circularity=0.35-1.00 show=Outlines display exclude summarize');",)

      # # Optionally, you can save the result if needed
      # # self.ij.io().save(imp, 'path_to_save_result')  # Uncomment to save

      # # Close ImageJ after processing (optional)
      #   self.ij.dispose()

      # # Show success message
      #   QMessageBox.information(None, "Success", "Image processed and thresholded successfully")

      # # Clear the ImageJ window
      #   self.ij.window().clear()














    # def process_image(self):
    #     if self.pixmap is None:
    #         QMessageBox.information(None, "Error", "No image loaded")
    #         return

    #     # Convert QPixmap to QImage
    #     qimage = self.pixmap.toImage()

    #     # Convert QImage to numpy array
    #     width = qimage.width()
    #     height = qimage.height()
    #     channels = 4  # Assuming RGBA format
    #     ptr = qimage.bits()
    #     arr = np.array(ptr).reshape(height, width, channels)

    #     # Convert to grayscale if needed (use only the RGB channels if the image is RGBA)
    #     if arr.shape[2] == 4:
    #         arr = arr[:, :, :3].dot([0.299, 0.587, 0.114])  # Convert to grayscale

    #     # Normalize to 8-bit (values from 0 to 255) if necessary
    #     arr = np.clip(arr, 0, 255).astype(np.uint8)

    #     imp = self.ij.py.to_java(arr)
    #     self.ij.ui().show(imp)
    #     self.ij.py.run_macro("run('Threshold...');")
    #     # Prompt the user for the lower and upper threshold values
    #     lower_threshold, ok1 = QInputDialog.getInt(None, "Enter Lower Threshold", "Lower Threshold:", 0, 0, 255, 1)
    #     upper_threshold, ok2 = QInputDialog.getInt(None, "Enter Upper Threshold", "Upper Threshold:", 255, 0, 255, 1)

    #     if not ok1 or not ok2:
    #         return  # If the user cancelled the input dialogs

    #     # Apply the threshold manually (binary mask creation)
    #     thresholded = np.where((arr >= lower_threshold) & (arr <= upper_threshold), 255, 0)

    #     # Ensure the thresholded image is of correct uint8 type for display
    #     thresholded = thresholded.astype(np.uint8)

    #     # Convert the thresholded image (binary) back to QImage
    #     thresholded_qimage = QImage(thresholded.data, thresholded.shape[1], thresholded.shape[0], QImage.Format_Grayscale8)

    #     # Convert QImage to QPixmap for display
    #     pixmap_8bit = QPixmap.fromImage(thresholded_qimage)

    #     # Set the QPixmap to a QLabel or other widget for display
    #     self.display_image(pixmap_8bit)

    #     # Optionally, save the thresholded image
    #     # self.save_thresholded_image(thresholded)  # Uncomment if saving is needed



    #     QMessageBox.information(None, "Success", "Image processed and thresholded successfully")


    # def process_image(self):
    #     if self.pixmap is None:
    #         QMessageBox.information(None, "Error", "No image loaded")
    #         return

    #     # Convert QPixmap to QImage
    #     qimage = self.pixmap.toImage()

    #     # Convert QImage to numpy array
    #     width = qimage.width()
    #     height = qimage.height()
    #     channels = 4  # Assuming RGBA format
    #     ptr = qimage.bits()
    #     arr = np.array(ptr).reshape(height, width, channels)

    #     # Convert to grayscale if needed (use only the RGB channels if the image is RGBA)
    #     if arr.shape[2] == 4:
    #         arr = arr[:, :, :3].dot([0.299, 0.587, 0.114])  # Convert to grayscale

    #     # Normalize to 8-bit (values from 0 to 255) if necessary
    #     arr = np.clip(arr, 0, 255).astype(np.uint8)

    #     # Prompt the user for the lower and upper threshold values

    #     imp = self.ij.py.to_java(arr)
    #     self.ij.ui().show(imp)
    #     self.ij.py.run_macro("run('Threshold...');")
    #     # Step 1: Convert to Binary (Make Binary)
    #     self.ij.py.run_macro("run('Make Binary');")

    #     # Step 2: Apply Watershed
    #     self.ij.py.run_macro("run('Watershed');")

    #     # Step 3: Analyze Particles (Size 50-50000, Circularity 0.7-1.00)
    #     self.ij.py.run_macro("run('Analyze Particles...', 'size=50-50000 circularity=0.7-1.00 show=[Outlines]');")

    #     results_table = self.ij.table()
    #     particle_count = results_table.size()
    #     # Wait for the user to finish
    #     QMessageBox.information(None, "Bacteria Count", f"Number of bacteria detected: {particle_count}")
    #     self.ij.window().clear()




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
