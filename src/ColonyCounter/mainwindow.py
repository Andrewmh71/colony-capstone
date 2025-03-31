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
import imageio
from PIL import Image
import pillow_heif
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
from skimage.morphology import label
# from jnius import autoclass
import scyjava
from scyjava import jimport
import matplotlib.pyplot as plt


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

        # Connect the save button to save the cropped image

        self.ui.addBacteriaButton.clicked.connect(self.add_colonies)

        self.ui.nextButton.clicked.connect(self.next_image)



        self.pixmap = None
        self.file_path = None
        self.ellipse_item = None
        self.image = None
        self.image_item = None
        self.drawing_enabled = False

    pillow_heif.register_heif_opener()
    def open_image_dialog(self):
        # Show file dialog with image filter (including HEIC) for multiple files
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open Images",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.heic)"
        )

        if file_paths:
            self.file_paths = file_paths  # Store selected file paths
            self.current_image_index = 0  # Set initial index to 0
            print(f"Loaded {len(self.file_paths)} images.")  # Debug: Check number of images
            self.process_batch()  # Process the first image



    def process_batch(self):
        """Loads and displays the current image from the file paths stored in self.file_paths"""
        if not self.file_paths:  # Check if there are no files
            print("No images to process.")  # Debug: No files loaded
            return  # Exit early if there are no file paths to process

        # Get the current image path based on the current index
        current_image_path = self.file_paths[self.current_image_index]
        print(f"Processing {current_image_path}")  # Debug: Check which image is being processed

        # Load the image using Pillow (with pillow-heif support)
        image = Image.open(current_image_path)

        # Convert the image to QPixmap to display in the QGraphicsView
        image = image.convert("RGB")  # Ensure it's in RGB mode
        data = image.tobytes("raw", "RGB")  # Convert to raw byte data
        qim = QImage(data, image.width, image.height, image.width * 3, QImage.Format_RGB888)

        # Convert QImage to QPixmap
        pixmap = QPixmap.fromImage(qim)

        if pixmap.isNull():
            print("Failed to load image!")  # Debug: Image not loaded properly
            return

        # Clear any existing items in the scene
        self.scene.clear()

        # Create a QGraphicsPixmapItem with the selected image and add it to the scene
        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.image_item)

        # Fit the image to the QGraphicsView initially
        self.image_container.fitInView(self.image_item, Qt.KeepAspectRatio)

        # Store the pixmap for potential future use
        self.pixmap = pixmap


    def next_image(self):
        """Displays the next image in the file path list."""
        if self.current_image_index < len(self.file_paths) - 1:
            self.current_image_index += 1  # Move to the next image
            print(f"Moving to next image. Index: {self.current_image_index}")  # Debug: Check index
            self.process_batch()  # Process and display the next image
        else:
            print("All images processed!")  # Debug: End of list
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


        macro = """
        roiCount = roiManager("count");
        if (roiCount > 0) {
            roiManager("Deselect");
            roiManager("Delete");
        }

        run("Add to Manager");

        if (!isOpen("ROI Manager")) {
            run("ROI Manager...");
        }


        roiManager("Select", 0);

        // Debug: Print selection type
        isComposite = (selectionType() == 9); // Check for composite selection

        if (isComposite) {
            roiManager("Split");
            wait(200); // Give time for processing
        }

        // Get the updated ROI count
        roiCountAfter = roiManager("count");

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

      # If circles are detected, find the most centered circle
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
        self.ij.py.run_macro("run('Remove Outliers...', 'radius=2 threshold=50 which=Bright');",)
        for i in range(2):
            self.ij.py.run_macro("run('Despeckle');",)

      # # Analyze particles with specific settings
        # self.ij.py.run_macro("run('Gaussian Blur...', 'sigma=2');",)

        # self.ij.py.run_macro("run('Analyze Particles...', 'size=50-50000 circularity=0.65-1.00 show=Outlines display exclude summarize overlay');",)
        self.ij.py.run_macro("run('Watershed');",)
        self.ij.py.run_macro("run('Analyze Particles...', 'size=70-50000 circularity=0.70-1.00 display exclude summarize overlay');",)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())