from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QPainter, QWheelEvent, QMouseEvent
from PySide6.QtCore import Qt, QPointF

class ImageGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.zoom_factor = 1.25       # Factor by which to zoom in or out
        self.current_zoom = 1.0       # Track the current zoom level
        self.initial_zoom = 1.0       # Minimum zoom level, set after fitting the image
        self.max_zoom = 3.0           # Maximum zoom level (300%)
        self.is_panning = False
        self.last_pan_point = QPointF()  # Track the last point for panning

        # Smooth transformations
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.NoDrag)  # Use custom panning instead of built-in

    def fit_image_to_view(self):
        # Fit the image to the view initially, respecting the aspect ratio
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        self.initial_zoom = self.transform().m11()  # Capture the initial scale factor as min zoom
        self.current_zoom = self.initial_zoom       # Start at the initial zoom level

    def wheelEvent(self, event: QWheelEvent):
        # Zoom with Ctrl + scroll and apply zoom limits
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0 and self.current_zoom < self.max_zoom:
                self.scale(self.zoom_factor, self.zoom_factor)
                self.current_zoom *= self.zoom_factor
            elif event.angleDelta().y() < 0 and self.current_zoom > self.initial_zoom:
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
                self.current_zoom /= self.zoom_factor
            self.limit_view_to_scene()

        # Horizontal scrolling with Shift + scroll
        elif event.modifiers() == Qt.ShiftModifier:
            scroll_amount = event.angleDelta().y() / 120  # Each notch provides 120 units
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - scroll_amount * 20)

        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        # Enable panning with left mouse button
        if event.button() == Qt.LeftButton:
            self.is_panning = True
            self.setCursor(Qt.ClosedHandCursor)
            self.last_pan_point = event.position()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        # Perform panning when the left mouse button is held down
        if self.is_panning:
            delta = self.mapToScene(self.last_pan_point.toPoint()) - self.mapToScene(event.position().toPoint())
            self.last_pan_point = event.position()
            self.translate(delta.x(), delta.y())  # Use translate for smooth panning
            self.limit_view_to_scene()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        # Disable panning when the left mouse button is released
        if event.button() == Qt.LeftButton:
            self.is_panning = False
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def limit_view_to_scene(self):
        # Keep the view within the scene boundaries
        view_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        scene_rect = self.sceneRect()

        # Calculate the offset needed to keep the view within the scene
        x_offset = max(scene_rect.left() - view_rect.left(), 0) if view_rect.left() < scene_rect.left() else \
                   min(scene_rect.right() - view_rect.right(), 0) if view_rect.right() > scene_rect.right() else 0
        y_offset = max(scene_rect.top() - view_rect.top(), 0) if view_rect.top() < scene_rect.top() else \
                   min(scene_rect.bottom() - view_rect.bottom(), 0) if view_rect.bottom() > scene_rect.bottom() else 0

        if x_offset != 0 or y_offset != 0:
            self.translate(x_offset, y_offset)
