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
# from jnius import autoclass
import scyjava
from scyjava import jimport
import matplotlib.pyplot as plt





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
        print(self.ui.saveButton)  # Should not be None
        print(self.ui.addBacteriaButton)
        # Connect the save button to save the cropped image
        self.ui.saveButton.clicked.connect(self.save_cropped_image)

        self.ui.addBacteriaButton.clicked.connect(self.add_colonies)





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

    def add_colonies(self):
        # # macro = """
        # # rm = RoiManager.getInstance();
        # # if (rm == null) rm = new RoiManager();
        # # roi = getSelection();
        # # if (roi != null) {
        # #     rm.addRoi(roi);
        # # } else {
        # #     print("No selection found.");
        # # }
        # # """
        # # self.ij.py.run_macro(macro)

        # self.ij.py.run_macro("run('Add to Manager');")

        # self.ij.py.run_macro("rm.addRoi(roi);",)  # Convert to 8-bit









        macro = """
        run("Add to Manager");

        if (!isOpen("ROI Manager")) {
            run("ROI Manager...");
        }

        roiManager("Select", 0);

        // Debug: Print selection type
        print("Selection Type: " + selectionType());

        isComposite = (selectionType() == 9); // Check for composite selection
        print("Is Composite? " + isComposite);

        if (isComposite) {
            print("Attempting to split composite selection...");
            roiManager("Split");
            wait(200); // Give time for processing
        }

        // Get the updated ROI count
        roiCountAfter = roiManager("count");
        print("ROI Count After Split: " + roiCountAfter);

        if (!isComposite || roiCountAfter == 1) {
            // Process single ROI directly
            roiManager("Select", 0);
            roiManager("Measure");
            run("Add Selection...");
            roiManager("Delete");
        } else {
            // Remove original composite ROI
            roiManager("Select", 0);
            roiManager("Delete");

            roiCountAfter = roiManager("count"); // Update count

            // Process each split ROI
            for (i = roiCountAfter - 1; i >= 0; i--) {
                roiManager("Select", i);
                roiManager("Measure");
                run("Add Selection...");
                roiManager("Delete");
            }
        }



        """

        self.ij.py.run_macro(macro)







        # macro = """
        # run("Add to Manager");
        # if (!isOpen("ROI Manager")) {
        #     run("ROI Manager...");
        # }
        # roiCount = roiManager("count");

        # if (roiCount == 1) {
        #     roiManager("Measure");
        #     run("Add Selection...");
        #     roiManager("Delete");
        # } else {
        #     roiManager("Select", 0);
        #     roiManager("Delete"); // Remove composite ROI

        #     roiCount = roiManager("count"); // Update count after deletion

        #     for (i = 0; i < roiCount; i++) {
        #         roiManager("Select", i);
        #         roiManager("Measure");
        #         run("Add Selection...");
        #         roiManager("Delete");
        #     }
        # }
        # """

        # self.ij.py.run_macro(macro)



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
        # image = arr
        # if arr.shape[2] == 4:
        #     arr = arr[:, :, :3].dot([0.299, 0.587, 0.114])  # Convert to grayscale
        # arr = np.clip(arr, 0, 255).astype(np.uint8)



        # Step 1: Read the original image
        # image_path = r'C:\Users\luke\Downloads\IMG_5280.jpg'  # Replace with the correct path
        # image = cv2.imread(image_path)

        # Check if the image is loaded properly
        if arr is None:
            print("Error: The image could not be loaded.")
        else:
            # Step 2: Resize the image to reduce computation
            resize_factor = 0.1  # Resize to 10% of the original size (you can adjust this)
            resized_image = cv2.resize(arr, (0, 0), fx=resize_factor, fy=resize_factor)

            # Convert resized image to grayscale
            gray_resized = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

            # Step 3: Detect circles in the resized image
            circles_resized = cv2.HoughCircles(
                gray_resized,
                cv2.HOUGH_GRADIENT,
                dp=1.3,
                minDist=100,
                param1=50,
                param2=30,
                minRadius=30,
                maxRadius=100
            )

            # Step 4: If circles are detected, find the most centered circle
            if circles_resized is not None:
                circles_resized = np.round(circles_resized[0, :]).astype("int")

                # Calculate the center of the original image
                height, width = arr.shape[:2]
                image_center = (width // 2, height // 2)

                # Variable to store the most centered circle
                most_centered_circle = None
                min_distance = float('inf')

                # Find the circle closest to the center of the image
                for (x_resized, y_resized, r_resized) in circles_resized:
                    # Scale the circle parameters back to the original image size
                    x_original = int(x_resized / resize_factor)
                    y_original = int(y_resized / resize_factor)
                    r_original = int(r_resized / resize_factor)

                    # Calculate the Euclidean distance from the center of the image to the circle center
                    distance = np.sqrt((x_original - image_center[0]) ** 2 + (y_original - image_center[1]) ** 2)

                    # If this circle is the most centered so far, store it
                    if distance < min_distance:
                        most_centered_circle = (x_original, y_original, r_original)
                        min_distance = distance

                # If we found a most centered circle, crop the image inside the circle
                if most_centered_circle:
                    x, y, r = most_centered_circle
                    output_image = arr.copy()

                    # Step 5: Create a mask for the circle
                    mask = np.zeros_like(arr)
                    cv2.circle(mask, (x, y), r, (255, 255, 255), -1)  # White circle on black background

                    # Step 6: Apply the mask to the original image
                    result = cv2.bitwise_and(arr, mask)

                    # Step 7: Crop the region inside the circle
                    # Create a bounding box around the circle
                    x1 = max(0, x - r)
                    y1 = max(0, y - r)
                    x2 = min(arr.shape[1], x + r)
                    y2 = min(arr.shape[0], y + r)

                    cropped_image = result[y1:y2, x1:x2]

                    # Step 8: Display the cropped result
                    plt.imshow(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
                    plt.show()

                else:
                    print("No circles detected.")
            else:
                print("No circles detected.")





        if cropped_image.shape[2] == 4:  # Check if the image has 4 channels (RGBA)
            # Discard the alpha channel (use only RGB channels)
            cropped_image = cropped_image[:, :, :3]

        # Convert to grayscale (if RGB image)
        cropped_image = cropped_image.dot([0.299, 0.587, 0.114])  # RGB to grayscale conversion
        cropped_image = np.clip(cropped_image, 0, 255).astype(np.uint8)  # Ensure values are within 0-255 range

        # Convert numpy array to ImagePlus object
        imp = self.ij.py.to_java(cropped_image)

        # Show the image in ImageJ
        self.ij.ui().show(imp)

        # Run commands in ImageJ

        # self.ij.ui().show(imp)


        # image_to_thresh = self.ij.py.from_java(imp)
        # image_to_thresh = np.array(image_to_thresh)

        # # Apply an inverted simple threshold
        # thresh_value = 175  # The threshold value
        # max_value = 255  # Max value for the thresholded pixels (white)

        # # Invert the threshold operation (black becomes white, white becomes black)
        # retval, thresholded_image = cv2.threshold(image_to_thresh, thresh_value, max_value, cv2.THRESH_BINARY_INV)
        # # retval, thresholded_image = cv2.threshold(image_to_thresh, thresh_value, max_value, cv2.THRESH_BINARY)

        # # Convert back to ImagePlus (Java object)
        # imp = self.ij.py.to_java(thresholded_image)

        # self.ij.ui().show(imp)


        # Access and modify a preference (for example, black background setting)


        # Access and modify a preference (for example, black background setting)


        # self.ij.py.run_macro('setOption("BlackBackground", true);')
        self.ij.py.run_macro("run('8-bit');",)  # Convert to 8-bit

        self.ij.py.run_macro("run('Convert to Mask');",)
        self.ij.py.run_macro('setThreshold(0, 0);')
        self.ij.py.run_macro("run('Convert to Mask');",)
        # self.ij.py.run_macro("run('Make Binary');",)




        # self.ij.ui().setBlackBackground(True)
        # # Optionally, print to confirm
        # print(prefs.get('blackBackground'))  # Should print True
        # self.ij.py.run_macro("run('Convert to Mask');",)

        # # Optionally, show the inverted image

        # self.ij.py.run_macro("run('transform.invert');",)
      #   # self.ij.ui().show(imp)
      #   # self.ij.py.run_macro("run('8-bit');",)
        # self.ij.py.run_macro("run('Fill Holes', '');",)
        # self.ij.py.run_macro("run('Watershed');",)
        # self.ij.py.run_macro("run('Remove Outliers...', 'radius=2 threshold=50 which=Bright');",)
      #   # self.ij.py.run_macro("run('Watershed');",)  # Apply watershed
      #   # self.ij.py.run_macro("run('Remove Outliers...', 'radius=15 threshold=50 which=Bright');",)
        self.ij.py.run_macro("run('Remove Outliers...', 'radius=15 threshold=50 which=Bright');",)
        for i in range(2):
            self.ij.py.run_macro("run('Despeckle');",)

      # # Analyze particles with specific settings
        # self.ij.py.run_macro("run('Gaussian Blur...', 'sigma=2');",)

        # self.ij.py.run_macro("run('Analyze Particles...', 'size=50-50000 circularity=0.65-1.00 show=Outlines display exclude summarize overlay');",)
        self.ij.py.run_macro("run('Watershed');",)
        self.ij.py.run_macro("run('Analyze Particles...', 'size=120-50000 circularity=0.80-1.00 display exclude summarize overlay');",)

        self.ij.py.run_macro("setTool('freehand');",)
        self.ij.ui().show(imp)

      # # # Optionally, you can save the result if needed
      # # # self.ij.io().save(imp, 'path_to_save_result')  # Uncomment to save

      # # # Close ImageJ after processing (optional)
      # #   self.ij.dispose()

      # # # Show success message
      # #   QMessageBox.information(None, "Success", "Image processed and thresholded successfully")

      # # # Clear the ImageJ window
      # #   self.ij.window().clear()


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
