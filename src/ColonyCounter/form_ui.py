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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QMainWindow, QPushButton,
    QSizePolicy, QStatusBar, QWidget)
import background_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1282, 826)
        MainWindow.setStyleSheet(u"background-image: url(:/newPrefix/images/beaver_bg.jpg);")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.uploadButton = QPushButton(self.centralwidget)
        self.uploadButton.setObjectName(u"uploadButton")
        self.uploadButton.setGeometry(QRect(130, 580, 531, 91))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(24)
        font.setBold(True)
        font.setItalic(False)
        self.uploadButton.setFont(font)
        self.uploadButton.setStyleSheet(u"background-color: transparent;\n"
"border: 5px solid gray;\n"
"border-radius: 25px;\n"
"font: 700 24pt \"Segoe UI\";")
        self.imageContainer = QGraphicsView(self.centralwidget)
        self.imageContainer.setObjectName(u"imageContainer")
        self.imageContainer.setGeometry(QRect(40, 60, 751, 451))
        self.imageContainer.setStyleSheet(u"background-color: rgba(255, 255, 255, 180); ")
        self.cropButton = QPushButton(self.centralwidget)
        self.cropButton.setObjectName(u"cropButton")
        self.cropButton.setGeometry(QRect(870, 250, 161, 41))
        self.cropButton.setStyleSheet(u"background-color: transparent;\n"
"border: 2.5px solid gray;\n"
"border-radius: 10px;\n"
"font: 700 12pt \"Segoe UI\";")
        self.cropButton.setFlat(True)
        self.analyzeButton = QPushButton(self.centralwidget)
        self.analyzeButton.setObjectName(u"analyzeButton")
        self.analyzeButton.setGeometry(QRect(870, 190, 161, 41))
        self.analyzeButton.setStyleSheet(u"background-color: transparent;\n"
"border: 2.5px solid gray;\n"
"border-radius: 10px;\n"
"font: 700 12pt \"Segoe UI\";")
        self.analyzeButton.setFlat(True)
        self.saveButton = QPushButton(self.centralwidget)
        self.saveButton.setObjectName(u"saveButton")
        self.saveButton.setGeometry(QRect(870, 130, 161, 41))
        self.saveButton.setStyleSheet(u"background-color: transparent;\n"
"border: 2.5px solid gray;\n"
"border-radius: 10px;\n"
"font: 700 12pt \"Segoe UI\";")
        self.saveButton.setFlat(True)
        self.buttonContainer = QGraphicsView(self.centralwidget)
        self.buttonContainer.setObjectName(u"buttonContainer")
        self.buttonContainer.setGeometry(QRect(860, 110, 181, 201))
        self.buttonContainer.setStyleSheet(u"background-color: rgba(255, 255, 255, 180);\n"
"border: 2px solid gray;\n"
"border-radius: 15px;\n"
"padding: 10px; ")
        MainWindow.setCentralWidget(self.centralwidget)
        self.buttonContainer.raise_()
        self.uploadButton.raise_()
        self.imageContainer.raise_()
        self.saveButton.raise_()
        self.analyzeButton.raise_()
        self.cropButton.raise_()
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.uploadButton.setText(QCoreApplication.translate("MainWindow", u"Upload Image", None))
        self.cropButton.setText(QCoreApplication.translate("MainWindow", u"Crop", None))
        self.analyzeButton.setText(QCoreApplication.translate("MainWindow", u"Analyze", None))
        self.saveButton.setText(QCoreApplication.translate("MainWindow", u"Save", None))
    # retranslateUi

