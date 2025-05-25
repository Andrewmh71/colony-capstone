from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsPixmapItem, QGraphicsScene, QMessageBox, QGraphicsEllipseItem, QGraphicsItem, QGraphicsRectItem, QSlider, QInputDialog,  QVBoxLayout,  QSizePolicy
from PySide6.QtGui import QPixmap, QImage, QPen, QMouseEvent, QPainter, QRegion, QPainterPath, QIcon, QWindow
import time
from PySide6.QtCore import Qt, QRectF, QSize
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
import shutil
import hashlib
from PySide6.QtWidgets import QFileDialog, QMessageBox, QMainWindow, QListWidget, QListWidgetItem, QVBoxLayout, QWidget
import psutil
import win32gui
import time
import win32con
import pandas as pd
from pandas import ExcelWriter
import openpyxl
import tkinter as tk
from tkinter import filedialog
import re




pillow_heif.register_heif_opener()


class ImageUploader(QMainWindow):
    def __init__(self, app_folder="app_images"):
        super().__init__()

        self.app_folder = app_folder
        self.saved_hashes = {}  # Dictionary to store hashes of saved images with the corresponding file path

        # Load existing hashes from the folder if any
        self._load_existing_hashes()

        if not os.path.exists(self.app_folder):
            os.makedirs(self.app_folder)

        # Set up the main window layout
        self.setWindowTitle("Image Uploader")
        self.setGeometry(100, 100, 800, 600)

        # List Widget to show images
        self.image_list_widget = QListWidget(self)
        self.image_list_widget.setGeometry(10, 10, 780, 550)
        self.image_list_widget.setViewMode(QListWidget.IconMode)
        self.image_list_widget.setIconSize(QSize(100, 100))
        self.image_list_widget.setSpacing(10)
        self.image_list_widget.setDragEnabled(False)  # Disable dragging on the list widget
        self.image_list_widget.setAcceptDrops(False)  # Also ensure drops are not accepted

        # Load images into the list widget
        self.load_images_into_widget()

        # Set layout and central widget
        layout = QVBoxLayout()
        layout.addWidget(self.image_list_widget)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def get_all_images(self):
        """Return all saved image paths"""
        return list(self.saved_hashes.values())

    def _load_existing_hashes(self):
        """Load the hashes of images already in the app folder"""
        for image_name in os.listdir(self.app_folder):
            image_path = os.path.join(self.app_folder, image_name)
            if os.path.isfile(image_path):
                image_hash = self._get_image_hash(image_path)
                self.saved_hashes[image_hash] = image_path  # Store the hash and path

    #Hash each uploaded image, so that duplicates cannot be uploaded
    def _get_image_hash(self, image_path):
        """Generate a hash for the given image file"""
        hash_sha256 = hashlib.sha256()
        with open(image_path, 'rb') as f:
            while chunk := f.read(8192):  # Read file in chunks
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def upload_images(self):
        """Upload and save images, skipping duplicates based on hash"""
        # Open a file dialog to select images
        file_paths, _ = QFileDialog.getOpenFileNames(None, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.heic)")
        if not file_paths:
            return

        saved_images = []

        for image_path in file_paths:
            try:
                # Generate the hash of the current image
                image_hash = self._get_image_hash(image_path)

                # Check if the image hash already exists
                if image_hash in self.saved_hashes:
                    existing_image = self.saved_hashes[image_hash]  # Get the existing image path
                    print(f"Image {os.path.basename(image_path)} is already saved as {os.path.basename(existing_image)}.")
                    continue  # Skip this image as it is a duplicate based on content

                # Proceed to save the image
                image_name = os.path.basename(image_path)
                saved_path = os.path.join(self.app_folder, image_name)

                # Ensure unique name if image already exists (based on name)
                if os.path.exists(saved_path):
                    base_name, ext = os.path.splitext(image_name)
                    counter = 1
                    while os.path.exists(saved_path):
                        new_name = f"{base_name}_{counter}{ext}"
                        saved_path = os.path.join(self.app_folder, new_name)
                        counter += 1

                shutil.copy(image_path, saved_path)
                self.saved_hashes[image_hash] = saved_path  # Store the hash and path of the saved image
                saved_images.append(saved_path)

            except Exception as e:
                QMessageBox.warning(None, "Error", f"Failed to save image {image_path}: {str(e)}")

        if saved_images:
            QMessageBox.information(None, "Images Saved", f"Images have been successfully saved to: {self.app_folder}")
        return saved_images  # List of saved image paths

    def load_images_into_widget(self):
        """Load the images from the folder into the list widget"""
        for image_hash, image_path in self.saved_hashes.items():
            # Create a list item for each image
            image_name = os.path.basename(image_path)
            item = QListWidgetItem(image_name)

            # Create a thumbnail for each image
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                print(f"Failed to load image: {image_path}")
                continue  # Skip this image if it can't be loaded
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)  # Scale the pixmap to fit in the list widget
            item.setIcon(QIcon(pixmap))

            # Add item to the list widget
            self.image_list_widget.addItem(item)

            # Make the item clickable and associate the image path with it
            item.setData(Qt.UserRole, image_path)  # Store the path of the image in the item data
            print(f"Image added to list: {image_name}")  # Debugging print statement

        # Connect the itemClicked signal to the handler after adding the items
        self.image_list_widget.itemClicked.connect(self.on_image_clicked)

    def on_image_clicked(self, item):
        """Handle the click on an image item in the list"""
        image_path = item.data(Qt.UserRole)  # Retrieve the image path from the item data
        print(f"Clicked on image: {image_path}")  # This should print when you click an image item

        # Call the function to process the clicked image
        self.process_single_image(image_path)

    def process_single_image(self, image_path):
        """Process the selected image based on the path"""
        print(f"Processing {image_path}")  # Debug: Check which image is being processed

        # Load the image using Pillow (with pillow-heif support)
        image = Image.open(image_path)

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

class MainWindow(QMainWindow):

    def display_thumbnails(self, image_paths):
           """Displays thumbnails of the images in the QListWidget."""
           self.ui.thumbnailWidget.clear()
           for path in image_paths:
               item = QListWidgetItem()
               pixmap = QPixmap(path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
               icon = QIcon(pixmap)
               item.setIcon(icon)
               item.setText(os.path.basename(path))
               item.setSizeHint(QSize(120, 120))  # Add some padding
               item.setData(Qt.UserRole, path)  # Store the image path as custom data
               self.ui.thumbnailWidget.addItem(item)



    def __init__(self):
        super().__init__()
        self.hwnd = []
        sj.config.add_option('-Xmx1g')
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ij = imagej.init('sc.fiji:fiji', headless=False)

        self.ui.thumbnailWidget.setViewMode(QListWidget.IconMode)
        self.ui.thumbnailWidget.setIconSize(QSize(100, 100))
        self.ui.thumbnailWidget.setResizeMode(QListWidget.Adjust)
        self.ui.thumbnailWidget.setSpacing(10)
        self.ui.thumbnailWidget.itemClicked.connect(self.on_image_clicked)
        # Ensure the layout object is correctly assigned from Qt Designer
        layout = QVBoxLayout()
        self.ui.centralwidget_2.setLayout(layout)

       # Create the ImageJ container widget
        self.imagejContainer = QWidget(self)

       # Set the QSizePolicy for the imagejContainer to Fixed
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.imagejContainer.setSizePolicy(size_policy)  # Fix size of the widget

       # Add the imagejContainer to the layout
        layout.addWidget(self.imagejContainer)


        # Create an instance of ImageGraphicsView without adding it to a layout
        self.image_container = ImageGraphicsView(self)

        # Set the geometry to match the original image container's size and position
        self.image_container.setGeometry(self.ui.imageContainer.geometry())

        # Remove the original imageContainer widget (if it's no longer needed)
        self.ui.imageContainer.setParent(None)

        # Set up a QGraphicsScene
        self.scene = QGraphicsScene(self)
        self.image_container.setScene(self.scene)

        # Initialize ImageUploader
        self.image_uploader = ImageUploader()
        all_images = self.image_uploader.get_all_images()  # Get all saved images
        self.display_thumbnails(all_images)

        # Connect the button to open image dialog and save images
        # self.ui.uploadButton.clicked.connect(self.open_image_dialog)


        # Connect the analyze button to process the image
        self.ui.analyzeButton.clicked.connect(self.process_image)

        # Connect the crop button to enable ellipse drawing

        # Connect the save button to save the cropped image
        self.ui.saveImageButton.clicked.connect(self.save_results)
        self.ui.excelButton.clicked.connect(self.export_results)

        self.ui.addBacteriaButton.clicked.connect(self.add_colonies)

        # self.ui.nextButton.clicked.connect(self.next_image)
        self.ui.loadImageButton.clicked.connect(self.open_image_with_rois)
        self.ui.addFolderButton.clicked.connect(self.upload_images)

        self.ui.DeleteButton.clicked.connect(self.delete_image)


        self.pixmap = None
        self.file_path = None
        self.ellipse_item = None
        self.image = None
        self.image_item = None
        self.drawing_enabled = False

    def export_results(self):
        # Read the summary CSV file into a DataFrame
        df_summary = pd.read_csv("final_summary.csv")

        # Open a file dialog to select the existing Excel file
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        file_path = filedialog.askopenfilename(title="Select an Excel file", filetypes=[("Excel files", "*.xlsx;*.xls")])

        if not file_path:
            print("No file selected.")
            return

        # Extract the file name from current image path
        match = re.search(r'[^/\\]+$', self.current_image_path)

        if match:
            # Get the matched file name for the sheet name
            sheet_name = match.group(0)  # Extracted file name as the sheet name

            try:
                # Try to open the existing Excel file to append a new sheet
                with ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
                    df_summary.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"Summary saved to {file_path} in sheet '{sheet_name}'")
            except FileNotFoundError:
                print(f"File not found: {file_path}")
        else:
            print("No image selected")


    def delete_image(self):
        """Delete the selected image and its associated ROI file."""
        reply = QMessageBox.question(
            self,
            "Delete Image",
            "Are you sure you want to delete this image and its associated ROI data?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Delete the image file
                if os.path.exists(self.current_image_path):
                    os.remove(self.current_image_path)
                    print(f"Deleted image: {self.current_image_path}")
                else:
                    print("Image file does not exist.")

                # Try to delete the associated ROI file
                base_name = os.path.splitext(os.path.basename(self.current_image_path))[0]
                roi_file_path = os.path.join("app_ROI", f"{base_name}_ROI.zip")

                if os.path.exists(roi_file_path):
                    os.remove(roi_file_path)
                    print(f"Deleted ROI file: {roi_file_path}")
                else:
                    print("Associated ROI file not found.")

                # Remove the deleted image from saved_hashes
                if self.current_image_path in self.image_uploader.saved_hashes.values():
                    del self.image_uploader.saved_hashes[next(key for key, value in self.image_uploader.saved_hashes.items() if value == self.current_image_path)]
                    print(f"Removed {self.current_image_path} from saved_hashes.")

                # Refresh the thumbnail list (this also ensures the list widget updates)

                self.image_uploader.load_images_into_widget()
                all_images = self.image_uploader.get_all_images()
                self.display_thumbnails(all_images)

                # Clear current image display
                self.scene.clear()
                self.current_image_path = None

                QMessageBox.information(self, "Deleted", "Image and associated ROI (if any) deleted successfully.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while deleting: {e}")


    def on_image_clicked(self, item):

        self.ij.py.run_macro("""
        run("Clear Results", "");
        roiManager("Reset");""")
        """Handles click events on the list item."""
        image_path = item.data(Qt.UserRole)  # Retrieve the stored image path
        print(f"Image clicked: {image_path}")  # Debug: Check which image was clicked

        if self.hwnd:
            print(self.hwnd)
            for elem in self.hwnd:
                    win32gui.PostMessage(elem, win32con.WM_CLOSE, 0, 0)
            self.hwnd = []

        # Running the macro via ImageJ Python API

        # Running the macro via ImageJ Python API


        # Set the current image path
        self.current_image_path = image_path

        # Display the image in the PyQt GUI
        self.display_image(image_path)


    def display_image(self, image_path):
       """Displays the clicked image in the main view."""
       image = Image.open(image_path)

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





    def upload_images(self):
        saved_images = self.image_uploader.upload_images()
        if saved_images:
            print(f"Saved images: {saved_images}")
            # Use get_all_images to display both newly saved and already existing images
            all_images = self.image_uploader.get_all_images()  # Get all images (including previously saved)
            self.display_thumbnails(all_images)

    def save_results(self):
        if not hasattr(self, 'current_image_path') or not self.current_image_path:
            print("No image selected.")
            return

        # Extract image filename without extension
        image_name = os.path.splitext(os.path.basename(self.current_image_path))[0]
        roi_filename = f"{image_name}_ROI.zip"

        # Construct path to app_ROI folder (same level as app_images)
        app_dir = os.path.dirname(os.path.abspath(self.current_image_path))
        base_dir = os.path.dirname(app_dir)  # assumes app_images is a subfolder
        roi_dir = os.path.join(base_dir, "app_ROI")

        # Create the ROI folder if it doesn't exist
        os.makedirs(roi_dir, exist_ok=True)

        # Full path for ROI file
        file_path = os.path.join(roi_dir, roi_filename)

        # Escape backslashes for ImageJ macro
        escaped_path = file_path.replace("\\", "\\\\")
        macro = f'roiManager("Save", "{escaped_path}");'

        # Run the macro
        self.ij.py.run_macro(macro)
        print(f"ROI saved to {file_path}")

    def preprocess_image(self, arr):
        if arr.shape[2] == 4:
            arr = arr[:, :, :3]

        resize_factor = 0.1
        resized_image = cv2.resize(arr, (0, 0), fx=resize_factor, fy=resize_factor)
        gray_resized = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

        circles_resized = cv2.HoughCircles(
            gray_resized, cv2.HOUGH_GRADIENT,
            dp=1.3, minDist=100, param1=50, param2=30,
            minRadius=30, maxRadius=100
        )

        if circles_resized is not None:
            circles_resized = np.round(circles_resized[0, :]).astype("int")
            image_center = (arr.shape[1] // 2, arr.shape[0] // 2)
            most_centered_circle = min(
                circles_resized,
                key=lambda c: np.sqrt((int(c[0]/resize_factor) - image_center[0])**2 + (int(c[1]/resize_factor) - image_center[1])**2)
            )
            x, y, r = (int(most_centered_circle[0] / resize_factor),
                       int(most_centered_circle[1] / resize_factor),
                       int(most_centered_circle[2] / resize_factor))

            mask = np.zeros_like(arr)
            cv2.circle(mask, (x, y), r, (255, 255, 255), -1)
            result = cv2.bitwise_and(arr, mask)

            x1, y1 = max(0, x - r), max(0, y - r)
            x2, y2 = min(arr.shape[1], x + r), min(arr.shape[0], y + r)
            cropped_image = result[y1:y2, x1:x2]

            cropped_image = cropped_image.dot([0.299, 0.587, 0.114])
            cropped_image = np.clip(cropped_image, 0, 255).astype(np.uint8)


            # downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            # output_path = os.path.join(downloads_dir, "cropped_image.png")
            # cv2.imwrite(output_path, cropped_image)
            # print(f"Saved cropped image to: {output_path}")

            return cropped_image
        else:
            print("No circles found.")
            return None

    def open_image_with_rois(self):

        if self.hwnd:
            QMessageBox.information(
                self,
                "Image Already Loaded",
                "An image is already loaded. Please close it before opening another."
            )
            return
        """Auto-load the ROI set associated with the current image."""
        if not hasattr(self, 'current_image_path') or not self.current_image_path:
            print("No image selected.")
            return

        image_path = self.current_image_path.replace("\\", "/")
        image_name = os.path.basename(image_path)
        image_stem = os.path.splitext(image_name)[0]
        roi_dir = os.path.join(os.path.dirname(image_path), "../app_ROI")
        roi_dir = os.path.abspath(roi_dir)
        roi_path = os.path.join(roi_dir, f"{image_stem}_ROI.zip").replace("\\", "/")

        if not os.path.exists(image_path):
            print("Image file does not exist.")
            return

        if not os.path.exists(roi_path):
            print(f"ROI file not found: {roi_path}")
            return

        # Load image as array with OpenCV
        arr = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if arr is None:
            print("Failed to read image as array")
            return

        # Run preprocessing only
        cropped = self.preprocess_image(arr)
        if cropped is None:
            print("Preprocessing failed.")
            return

        # Convert to ImageJ image and show
        imp = self.ij.py.to_java(cropped)
        self.ij.ui().show(imp)
        hwnd = self.find_imagej_hwnd()
        if hwnd:
            print(f"Found ImageJ HWND: {hwnd}")
            self.hwnd.append(hwnd)
            try:
                win = QWindow.fromWinId(hwnd)  # Convert hwnd to QWindow
                container = self.createWindowContainer(win)  # Create a container for QWindow

                # Parent the container to centralwidget_2
                self.container = container
                self.container.setParent(self.ui.centralwidget_2)

                # Set the geometry to match the parent widget's size (top-left)
                self.container.setGeometry(self.ui.centralwidget_2.rect())  # Fills the space
                self.container.show()

            except Exception as e:
                print(f"Error embedding ImageJ window: {e}")
        else:
            print("Failed to find ImageJ window")

        self.ij.py.run_macro("setTool('freehand');",)
        # Open ROIs
        macro = f"""
        run("ROI Manager...");
        roiManager("Reset");
        roiManager("Open", "{roi_path}");
        //roiManager("Show All");
        roiManager("Show All with labels");
        roiManager("Deselect");
        roiManager("Measure");

        """
        self.ij.py.run_macro(macro)
        # self.add_colonies()



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


    def add_colonies(self):

        macro = """
        //run("Clear Results", "");
        roiCount = roiManager("count");

        run("Add to Manager");

        if (!isOpen("ROI Manager")) {
            run("ROI Manager...");
        }

        roiCount = roiManager("count");
        roiManager("Select", roiCount - 1);

        // Debug: Print selection type
        isComposite = (selectionType() == 9); // Check for composite selection

        if (isComposite) {
            roiManager("Split");
            wait(200); // Give time for processing
        }

        // Get the updated ROI count
        roiCountAfter = roiManager("count");

        if (!isComposite) {
            // Process single ROI directly
            roiManager("Select", roiCount - 1);
            run("Add Selection...");
        } else {
            // Remove original composite ROI
            roiManager("Select", roiCount - 1);
            roiManager("Delete");
            }
        roiCountAfter = roiManager("count"); // Update count


        run("Clear Results", "");
        roiManager("Deselect");
        roiManager("Measure");







        // Process each split ROI
        //for (i = roiCountAfter - 1; i >= 0; i--) {
            //roiManager("Select", i);
            //roiManager("Measure");

       // }
        //for (i = roiCountAfter - 1; i >= roiCount-1; i--) {
           // roiManager("Select", i);
           // run("Add Selection...");
      // }
       // roiManager("Deselect");
       // run("Select None");
    """

        self.ij.py.run_macro(macro)

    def find_imagej_hwnd(self, timeout=5.0):
        start_time = time.time()
        while time.time() - start_time < timeout:
            def enum_handler(hwnd, result):
                title = win32gui.GetWindowText(hwnd)
                try:
                    print(f"Window title: {title}")  # For debugging
                except UnicodeEncodeError:
                    print(f"Window title (unicode error): {title.encode('ascii', 'ignore').decode('ascii')}")
                if "(V)" in title:
                    result.append(hwnd)

            hwnds = []
            win32gui.EnumWindows(enum_handler, hwnds)
            if hwnds:
                return hwnds[0]
            time.sleep(0.1)
        return None

    def process_image(self):


        if self.hwnd:
            QMessageBox.information(
                self,
                "Image Already Loaded",
                "An image is already loaded. Please close it before opening another."
            )
            return
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



        # Check if the image is loaded properly
        if arr is None:
            print("Error: The image could not be loaded.")
        else:
             #Resize the image to reduce computation
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


        # Running the macro via ImageJ Python API
        # self.ij.py.run_macro(macro)


        # # Running the macro via ImageJ Python API
        # self.ij.py.run_macro(macro)
        self.ij.ui().show(imp)

        time.sleep(1)  # Give time to draw



        # Handle the resizing event to reset position and avoid jumping around


        self.ij.py.run_macro('roiManager("Reset");')

        self.ij.py.run_macro("run('8-bit');",)  # Convert to 8-bit

        self.ij.py.run_macro("run('Convert to Mask');",)
        self.ij.py.run_macro('setThreshold(0, 0);')
        self.ij.py.run_macro("run('Convert to Mask');",)

        self.ij.py.run_macro("run('Remove Outliers...', 'radius=2 threshold=50 which=Bright');",)
        for i in range(2):
            self.ij.py.run_macro("run('Despeckle');",)

        self.ij.py.run_macro("run('Watershed');",)
        self.ij.py.run_macro("run('Analyze Particles...', 'size=70-50000 circularity=0.70-1.00 display exclude summarize overlay add');",)
        
        project_id = self.ui.projectIdInput.text().strip()
        colony_label = self.ui.colonyIdInput.text().strip()

        if not project_id:
            project_id = "UNSET"
        if not colony_label:
            colony_label = "Unknown"


        self.ij.py.run_macro("""
            // Save Summary table if open
            if (isOpen("Summary")) {
                selectWindow("Summary");
                saveAs("Results", "summary_temp.csv");
            }
            // Save Results table if open
            if (isOpen("Results")) {
                selectWindow("Results");
                saveAs("Results", "results_table.csv");
            }
        """)
        df_results = pd.read_csv("results_table.csv")
        sizes = df_results["Area"]
        std_dev_size = round(df_results["Area"].std(ddof=1), 3)


        # Load the CSV into pandas
        df_summary = pd.read_csv("summary_temp.csv")
        # copy summary results from csv to excel
    

        image_file_name = os.path.basename(self.current_image_path)
        

        try:
            number_of_colonies = int(df_summary.at[0, 'Count'])
            average_size = float(df_summary.at[0, 'Average Size'])
        except KeyError:
            print("Expected columns missing.")
            return


        final_row = pd.DataFrame([{
            "project_id": project_id,
            "image_file_name": image_file_name,
            "colony_label": colony_label,
            "number_of_colonies": number_of_colonies,
            "average_size": average_size,
            "std_dev_size": std_dev_size
        }])

        # Save to final_summary.csv (append if exists)
        csv_path = "final_summary.csv"
        if os.path.exists(csv_path):
            final_row.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            final_row.to_csv(csv_path, index=False)

        self.ij.py.run_macro("setTool('freehand');",)
        self.ij.ui().show(imp)



        hwnd = self.find_imagej_hwnd()
        if hwnd:
            print(f"Found ImageJ HWND: {hwnd}")
            self.hwnd.append(hwnd)
            try:
                win = QWindow.fromWinId(hwnd)  # Convert hwnd to QWindow
                container = self.createWindowContainer(win)  # Create a container for QWindow

                # Parent the container to centralwidget_2
                self.container = container
                self.container.setParent(self.ui.centralwidget_2)

                # Set the geometry to match the parent widget's size (top-left)
                self.container.setGeometry(self.ui.centralwidget_2.rect())  # Fills the space
                self.container.show()

            except Exception as e:
                print(f"Error embedding ImageJ window: {e}")
        else:
            print("Failed to find ImageJ window")

        self.ij.py.run_macro("""
        if (!isOpen("ROI Manager")) {
            run("ROI Manager...");
        }
        roiCount = roiManager("count");
        if (roiCount > 0) {
            roiManager("Select", 0);
            roiManager("Update");
        }
        """)



    def wheelEvent(self, event):
        if hasattr(self, "container"):
            self.container.move(0, 0)  # Move to top-left corner explicitly if needed
            # Get the current mouse position within the container


    def resizeEvent(self, event):
         """
         Ensure that the ImageJ window stays centered (top-left position)
         """
         super().resizeEvent(event)

         # Ensure the container (ImageJ window) stays fixed in the top-left of the parent widget
         if hasattr(self, "container"):
             parent_rect = self.ui.centralwidget_2.rect()

             # Align the container to the top-left corner of the parent widget
             self.container.setGeometry(parent_rect)  # Align with the parent widget's geometry
             self.container.move(0, 0)  # Move to top-left corner explicitly if needed
             print("Container resized and moved to top-left.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())