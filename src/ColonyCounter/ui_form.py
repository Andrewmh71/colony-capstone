# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGraphicsView, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QSizePolicy, QStatusBar,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(912, 599)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.imageContainer = QGraphicsView(self.centralwidget)
        self.imageContainer.setObjectName(u"imageContainer")
        self.imageContainer.setGeometry(QRect(20, 90, 221, 171))
        self.analyzeButton = QPushButton(self.centralwidget)
        self.analyzeButton.setObjectName(u"analyzeButton")
        self.analyzeButton.setGeometry(QRect(20, 260, 221, 71))
        self.addBacteriaButton = QPushButton(self.centralwidget)
        self.addBacteriaButton.setObjectName(u"addBacteriaButton")
        self.addBacteriaButton.setGeometry(QRect(180, 60, 61, 31))
        self.saveImageButton = QPushButton(self.centralwidget)
        self.saveImageButton.setObjectName(u"saveImageButton")
        self.saveImageButton.setGeometry(QRect(70, 60, 51, 31))
        self.loadImageButton = QPushButton(self.centralwidget)
        self.loadImageButton.setObjectName(u"loadImageButton")
        self.loadImageButton.setGeometry(QRect(120, 60, 61, 31))
        self.addFolderButton = QPushButton(self.centralwidget)
        self.addFolderButton.setObjectName(u"addFolderButton")
        self.addFolderButton.setGeometry(QRect(260, 490, 621, 31))
        self.thumbnailWidget = QListWidget(self.centralwidget)
        self.thumbnailWidget.setObjectName(u"thumbnailWidget")
        self.thumbnailWidget.setGeometry(QRect(260, 30, 621, 461))
        self.DeleteButton = QPushButton(self.centralwidget)
        self.DeleteButton.setObjectName(u"DeleteButton")
        self.DeleteButton.setGeometry(QRect(20, 60, 51, 31))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.analyzeButton.setText(QCoreApplication.translate("MainWindow", u"Analyze", None))
        self.addBacteriaButton.setText(QCoreApplication.translate("MainWindow", u"Update", None))
        self.saveImageButton.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.loadImageButton.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.addFolderButton.setText(QCoreApplication.translate("MainWindow", u"Add Images to Workspce", None))
        self.DeleteButton.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
    # retranslateUi

