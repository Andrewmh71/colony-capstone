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
        MainWindow.resize(1748, 826)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.imageContainer = QGraphicsView(self.centralwidget)
        self.imageContainer.setObjectName(u"imageContainer")
        self.imageContainer.setGeometry(QRect(70, 60, 791, 471))
        self.analyzeButton = QPushButton(self.centralwidget)
        self.analyzeButton.setObjectName(u"analyzeButton")
        self.analyzeButton.setGeometry(QRect(280, 560, 321, 91))
        self.addBacteriaButton = QPushButton(self.centralwidget)
        self.addBacteriaButton.setObjectName(u"addBacteriaButton")
        self.addBacteriaButton.setGeometry(QRect(290, 30, 101, 31))
        self.saveImageButton = QPushButton(self.centralwidget)
        self.saveImageButton.setObjectName(u"saveImageButton")
        self.saveImageButton.setGeometry(QRect(130, 30, 81, 31))
        self.loadImageButton = QPushButton(self.centralwidget)
        self.loadImageButton.setObjectName(u"loadImageButton")
        self.loadImageButton.setGeometry(QRect(210, 30, 81, 31))
        self.addFolderButton = QPushButton(self.centralwidget)
        self.addFolderButton.setObjectName(u"addFolderButton")
        self.addFolderButton.setGeometry(QRect(970, 30, 151, 31))
        self.thumbnailWidget = QListWidget(self.centralwidget)
        self.thumbnailWidget.setObjectName(u"thumbnailWidget")
        self.thumbnailWidget.setGeometry(QRect(970, 60, 621, 461))
        self.DeleteButton = QPushButton(self.centralwidget)
        self.DeleteButton.setObjectName(u"DeleteButton")
        self.DeleteButton.setGeometry(QRect(70, 30, 61, 31))
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
        self.addBacteriaButton.setText(QCoreApplication.translate("MainWindow", u"Update Changes", None))
        self.saveImageButton.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.loadImageButton.setText(QCoreApplication.translate("MainWindow", u"Load Save", None))
        self.addFolderButton.setText(QCoreApplication.translate("MainWindow", u"Add Images to Workspce", None))
        self.DeleteButton.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
    # retranslateUi

