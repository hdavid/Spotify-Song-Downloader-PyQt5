# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Template.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


margin = 20
width = 700


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(width, 600)
        MainWindow.setStyleSheet("QFrame#frame{\n"
"    background-color: qlineargradient(spread:pad, x1:0.5, y1:0.05, x2:0.5, y2:0.15, stop:0.227273 rgba(0, 192, 255, 255), stop:0.606818 rgba(0, 0,0,255));\n"
"    border-radius:10px;\n"
"}\n"
"QPushButton#close{\n"
"    background-color: rgba(0, 0,0, 0);\n"
"    color:rgba(0,0,0,255);\n"
"    \n"
"    border-radius:5px;\n"
"}\n"
"QPushButton#close:hover{\n"
"    color:rgba(250,223,11,255);\n"
"}\n"
"#song_name{\n"
"    color:rgba(255,255,255,255);\n"
"}\n"
"#status_label{\n"
"    color:rgba(255,255,255,255);\n"
"}\n"
"#status_msg{\n"
"    color:rgba(255,255,255,255);\n"
"}\n"
"#counter_label{\n"
"    color:rgba(255,255,255,255);\n"
"}\n"
"#playlist_name{\n"
"    color:rgba(255,255,255,255);\n"
"}\n"
"#details{\n"
"    color:rgba(255,255,255,255);\n"
"}\n"
"QPushButton#close:pressed{\n"
"    padding-left:1px;\n"
"    padding-top:1px;\n"
"    background-color:rgba(150,123,111,255);\n"
"}\n"
"QLineEdit#playlist_link{\n"
"    background-color:rgba(0,0,0,0);\n"
"    border:2px solid rgba(0,0,0,0);\n"
"    border-bottom-color: rgba(100,100,100,255);\n"
"    color:rgb(255,255,255);\n"
"    padding-bottom:7px;\n"
"}\n"
"\n"
"\n"
"QPushButton#Select_Home{\n"
"    background-color: rgba(0, 0,0, 0);\n"
"    color:rgba(200,200,200,255);\n"
"    border-radius:5px;\n"
"}\n"
"\n"
"QPushButton#Select_Home:hover{\n"
"    color:rgba(250,223,11,255);\n"
"}\n"
"\n"
"QPushButton#Select_Home:pressed{\n"
"    padding-left:1px;\n"
"    padding-top:1px;\n"
"    background-color:rgba(150,123,111,255);\n"
"}\n"
"")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(30, 20, width, 600))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        
        self.title = QtWidgets.QLabel(self.frame)
        self.title.setGeometry(QtCore.QRect(margin, 5, width-2*margin, 41))
        self.title.setMaximumSize(QtCore.QSize(16777204, 16777215))
        font = QtGui.QFont()
        #font.setFamily("Mistral")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setScaledContents(True)
        #self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("label")
        
        self.close = QtWidgets.QPushButton(self.frame)
        self.close.setGeometry(QtCore.QRect(670, 10, 20, 20))
        self.close.setMaximumSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.close.setFont(font)
        self.close.setObjectName("close")
        
        self.playlist_link = QtWidgets.QLineEdit(self.frame)
        self.playlist_link.setGeometry(QtCore.QRect(margin, 70, width-2*margin-30, 25))
        font = QtGui.QFont()
        font.setKerning(False)
        self.playlist_link.setFont(font)
        self.playlist_link.setMouseTracking(False)
        self.playlist_link.setAcceptDrops(False)
        self.playlist_link.setWhatsThis("Enter Spotify playlist Link")
        self.playlist_link.setStyleSheet("")
        self.playlist_link.setText("")
        self.playlist_link.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.playlist_link.setClearButtonEnabled(True)
        self.playlist_link.setObjectName("playlist_link")
        
        self.playlist_name = QtWidgets.QLabel(self.frame)
        self.playlist_name.setGeometry(QtCore.QRect(margin, 100, width-2*margin-30, 30))
        self.playlist_name.setText("song playlist_name")
        self.playlist_name.setWordWrap(True)
        self.playlist_name.setText("")
        self.playlist_name.setObjectName("playlist_name")
        
        self.counter_label = QtWidgets.QLabel(self.frame)
        self.counter_label.setGeometry(QtCore.QRect(margin, 130, width-2*margin-30, 30))
        self.counter_label.setWordWrap(True)
        self.counter_label.setObjectName("counter_label")        
        
        self.song_name = QtWidgets.QLabel(self.frame)
        self.song_name.setGeometry(QtCore.QRect(margin, 160, width-2*margin-30, 30))
        self.song_name.setText("song name")
        self.song_name.setWordWrap(True)
        self.song_name.setObjectName("song_name")
        
        self.details = QtWidgets.QLabel(self.frame)
        self.details.setGeometry(QtCore.QRect(margin, 190, width-2*margin-30, 600-190-30))
        self.details.setText("")
        self.details.setWordWrap(True)
        self.details.setObjectName("details")
        self.details.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title.setText(_translate("MainWindow", "Spotify Downloader"))
        self.close.setText(_translate("MainWindow", "X"))
        self.playlist_link.setPlaceholderText(_translate("MainWindow", "Enter Spotify Playlist or Track Link"))
        self.song_name.setText(_translate("MainWindow", " "))
        self.counter_label.setText(_translate("MainWindow", ""))
     

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
