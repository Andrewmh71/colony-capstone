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
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QGraphicsView, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1282, 826)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.uploadButton = QPushButton(self.centralwidget)
        self.uploadButton.setObjectName(u"uploadButton")
        self.uploadButton.setGeometry(QRect(250, 610, 531, 91))
        font = QFont()
        font.setPointSize(18)
        self.uploadButton.setFont(font)
        self.imageContainer = QGraphicsView(self.centralwidget)
        self.imageContainer.setObjectName(u"imageContainer")
        self.imageContainer.setGeometry(QRect(70, 60, 791, 471))
        self.cropButton = QPushButton(self.centralwidget)
        self.cropButton.setObjectName(u"cropButton")
        self.cropButton.setGeometry(QRect(760, 0, 80, 24))
        self.analyzeButton = QPushButton(self.centralwidget)
        self.analyzeButton.setObjectName(u"analyzeButton")
        self.analyzeButton.setGeometry(QRect(670, 0, 80, 24))
        self.saveButton = QPushButton(self.centralwidget)
        self.saveButton.setObjectName(u"saveButton")
        self.saveButton.setGeometry(QRect(590, 0, 80, 24))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1282, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.uploadButton.setText(QCoreApplication.translate("MainWindow", u"Upload Image", None))
        self.cropButton.setText(QCoreApplication.translate("MainWindow", u"Crop", None))
        self.analyzeButton.setText(QCoreApplication.translate("MainWindow", u"Analyze", None))
        self.saveButton.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi

