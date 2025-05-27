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
from PySide6.QtWidgets import (QApplication, QGraphicsView, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QPushButton, QSizePolicy,
    QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1224, 601)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.imageContainer = QGraphicsView(self.centralwidget)
        self.imageContainer.setObjectName(u"imageContainer")
        self.imageContainer.setGeometry(QRect(210, 50, 411, 381))
        self.analyzeButton = QPushButton(self.centralwidget)
        self.analyzeButton.setObjectName(u"analyzeButton")
        self.analyzeButton.setGeometry(QRect(210, 520, 300, 41))
        self.projectIdInput = QLineEdit(self.centralwidget)
        self.projectIdInput.setObjectName(u"projectIdInput")
        self.projectIdInput.setGeometry(QRect(210, 440, 300, 30))
        self.colonyIdInput = QLineEdit(self.centralwidget)
        self.colonyIdInput.setObjectName(u"colonyIdInput")
        self.colonyIdInput.setGeometry(QRect(210, 480, 300, 30))
        self.saveImageButton = QPushButton(self.centralwidget)
        self.saveImageButton.setObjectName(u"saveImageButton")
        self.saveImageButton.setGeometry(QRect(690, 10, 101, 31))
        self.loadImageButton = QPushButton(self.centralwidget)
        self.loadImageButton.setObjectName(u"loadImageButton")
        self.loadImageButton.setGeometry(QRect(210, 20, 411, 31))
        self.addFolderButton = QPushButton(self.centralwidget)
        self.addFolderButton.setObjectName(u"addFolderButton")
        self.addFolderButton.setGeometry(QRect(20, 480, 141, 31))
        self.thumbnailWidget = QListWidget(self.centralwidget)
        self.thumbnailWidget.setObjectName(u"thumbnailWidget")
        self.thumbnailWidget.setGeometry(QRect(20, 50, 141, 431))
        self.DeleteButton = QPushButton(self.centralwidget)
        self.DeleteButton.setObjectName(u"DeleteButton")
        self.DeleteButton.setGeometry(QRect(20, 20, 71, 31))
        self.centralwidget_2 = QWidget(self.centralwidget)
        self.centralwidget_2.setObjectName(u"centralwidget_2")
        self.centralwidget_2.setGeometry(QRect(690, 40, 521, 451))
        self.excelButton = QPushButton(self.centralwidget)
        self.excelButton.setObjectName(u"excelButton")
        self.excelButton.setGeometry(QRect(880, 10, 111, 31))
        self.deleteColonies = QPushButton(self.centralwidget)
        self.deleteColonies.setObjectName(u"deleteColonies")
        self.deleteColonies.setGeometry(QRect(790, 10, 91, 31))
        self.deleteAll = QPushButton(self.centralwidget)
        self.deleteAll.setObjectName(u"deleteAll")
        self.deleteAll.setGeometry(QRect(90, 20, 71, 31))
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
        self.projectIdInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Project ID", None))
        self.colonyIdInput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Colony Label", None))
        self.saveImageButton.setText(QCoreApplication.translate("MainWindow", u"Save Progress", None))
        self.loadImageButton.setText(QCoreApplication.translate("MainWindow", u"Load Image From Save File", None))
        self.addFolderButton.setText(QCoreApplication.translate("MainWindow", u"Add Images to Workspace", None))
        self.DeleteButton.setText(QCoreApplication.translate("MainWindow", u"Delete 1", None))
        self.excelButton.setText(QCoreApplication.translate("MainWindow", u"Export To Excel", None))
        self.deleteColonies.setText(QCoreApplication.translate("MainWindow", u"Delete Selection", None))
        self.deleteAll.setText(QCoreApplication.translate("MainWindow", u"Clear All", None))
    # retranslateUi

