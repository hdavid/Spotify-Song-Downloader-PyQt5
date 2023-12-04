#!/usr/bin/python3
# Main
# if __name__ == '__main__':from PyQt5.uic import loadUi

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import  QCursor
from layout import Ui_MainWindow

import sys
import os
import platform
import string
import re
import traceback

from spotify_scraper import SpotifyScraper

      

class ScraperThread(QThread):
    
    def __init__(self, link):
        super().__init__()
        self.link = link
        self.scraper = SpotifyScraper()
        from os.path import expanduser
        home = expanduser("~")
        self.music_folder = home + "/Music/Tracks"
        
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            if platform.system() == "Windows":
                self.music_folder = "."
            else:
                if getattr(sys, 'frozen', False):
                    if not os.path.dirname(sys.executable).startswith("/Applications"):
                        self.music_folder = os.path.dirname(sys.executable) + "/../../.."
                elif __file__:
                    if not os.path.dirname(__file__).startswith("/Applications"):
                        self.music_folder = os.path.dirname(__file__) + "/../../.."
            

    def run(self):
        self.scraper.scrape_item(self.link, self.music_folder)


# Main Window
class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.scraper_thread = None
        
        self.setupUi(self)

        self.playlist_link.returnPressed.connect(self.on_returnButton)
        self.close.clicked.connect(self.exitprogram)
        
    @pyqtSlot()
    def on_returnButton(self):
        playlist_id = self.playlist_link.text()
        try:
            if self.scraper_thread is not None:
                return
            # Start the scraper in a separate thread
            self.scraper_thread = ScraperThread(playlist_id)
            
            self.scraper_thread.finished.connect(self.thread_finished)  
            self.scraper_thread.scraper.song_downloading.connect(self.update_song_downloading) 
            self.scraper_thread.scraper.playlist_name.connect(self.update_playlist_name)
            self.scraper_thread.scraper.counts.connect(self.update_counters)
            self.scraper_thread.scraper.details_update.connect(self.details_update)
            
            self.scraper_thread.start()
            
        except ValueError as e:
            print(e)
            print(traceback.format_exc())
            self.statusMsg.setText(str(e))

    def thread_finished(self):
        self.scraper_thread.deleteLater()  # Clean up the thread properly
        self.scraper_thread = None

    @pyqtSlot(str)
    def details_update(self, details):
        self.details.setText(details)

    @pyqtSlot(str)
    def update_playlist_name(self, playlist_name):
        self.playlist_name.setText(playlist_name)

    @pyqtSlot(str)
    def update_song_downloading(self, song_name):
        self.song_name.setText(song_name)

    @pyqtSlot(str, int, int, int, int)
    def update_counters(self, status, total, downloaded, skipped, failed):
        if skipped != 0 or failed != 0:
            self.counter_label.setText(status+":\t" + str(downloaded+skipped+failed) + "/" + str(total)  + "\tdownloaded:" + str(downloaded) + "\tskipped: " + str(skipped) + "\tfailed:" + str(failed))
        else:
            self.counter_label.setText(status+":\t" + str(downloaded+failed+skipped) + "/" + str(total) )
    

    # DRAGGLESS INTERFACE

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.ClosedHandCursor))

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_drag:
            self.move(QMouseEvent.globalPos() - self.m_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def exitprogram(self):
        sys.exit()


# Main
if __name__ == '__main__':
    app = QApplication(sys.argv)
    Screen = MainWindow()
    Screen.setFixedWidth(740)
    Screen.setFixedHeight(620)
    Screen.setWindowFlags(Qt.FramelessWindowHint)
    Screen.setAttribute(Qt.WA_TranslucentBackground)
    Screen.show()
    sys.exit(app.exec())


