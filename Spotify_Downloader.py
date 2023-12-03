#!/usr/bin/python3
# Main
# if __name__ == '__main__':from PyQt5.uic import loadUi

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import  QCursor
from Template import Ui_MainWindow

import sys
import os
import string
import requests
import re
import webbrowser

from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3

import unicodedata
    
import traceback

class Settings:
    def __init__(self):        
        self.music_folder = "../Tracks"
        self.music_folder_use_playlist_name = True
        self.skip_existing=True

settings = Settings()

class WritingMetaTags():
    def __init__(self, tags, filename):
        super().__init__()
        self.tags = tags
        self.filename = filename
        self.PICTUREDATA = None
        self.url = None

    def setPIC(self):
        if self.tags['cover'] is None:
            pass
        else:
            try:
                response = requests.get(self.tags['cover']+"?size=1", stream=True)
                if response.status_code == 200 :
                    audio = ID3(self.filename)
                    audio['APIC'] = APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc=u'Cover',
                        data=response.content
                    )
                    audio.save()

            except Exception as e:
                print(f"Error adding cover: {e}")

    def WritingMetaTags(self):
        try:
            # print('[*] FileName : ', self.filename)
            audio = EasyID3(self.filename)
            audio['title'] = self.tags['title']
            audio['artist'] = self.tags['artists']
            audio['album'] = self.tags['album']
            audio['date'] = self.tags['releaseDate']
            audio.save()
            self.setPIC()

        except Exception as e:
            print(f'Error {e}')


class MusicScraper(QThread):
    song_downloading = pyqtSignal(str)
    counts = pyqtSignal(int, int, int)

    def __init__(self):
        super(MusicScraper, self).__init__()
        self.downloaded_track_count = 0
        self.failed_track_count = 0
        self.skipped_track_count = 0
        self.failed_tracks = ""
        self.session = requests.Session()

    def get_ID(self, yt_id):
        # The 'get_ID' function from your scraper code
        LINK = f'https://api.spotifydown.com/getId/{yt_id}'
        headers = {
            'authority': 'api.spotifydown.com',
            'method': 'GET',
            'path': f'/getId/{id}',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-fetch-mode': 'cors',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
        response = self.session.get(url=LINK, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        return None

    def generate_Analyze_id(self, yt_id):
        # The 'generate_Analyze_id' function from your scraper code
        DL = 'https://corsproxy.io/?https://www.y2mate.com/mates/analyzeV2/ajax'
        data = {
            'k_query': f'https://www.youtube.com/watch?v={yt_id}',
            'k_page': 'home',
            'hl': 'en',
            'q_auto': 0,
        }
        headers = {
            'authority': 'corsproxy.io',
            'method': 'POST',
            'path': '/?https://www.y2mate.com/mates/analyzeV2/ajax',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-fetch-mode': 'cors',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
        RES = self.session.post(url=DL, data=data, headers=headers)
        if RES.status_code == 200:
            return RES.json()
        return None

    def generate_Conversion_id(self, analyze_yt_id, analyze_id):
        # The 'generate_Conversion_id' function from your scraper code
        DL = 'https://corsproxy.io/?https://www.y2mate.com/mates/convertV2/index'
        data = {
            'vid'   : analyze_yt_id,
            'k'     : analyze_id,
        }
        headers = {
            'authority': 'corsproxy.io',
            'method': 'POST',
            'path': '/?https://www.y2mate.com/mates/analyzeV2/ajax',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-fetch-mode': 'cors',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
        RES = self.session.post(url=DL, data=data, headers=headers)
        if RES.status_code == 200:
            return RES.json()
        return None

    def get_PlaylistMetadata(self, Playlist_ID):
        # The 'get_PlaylistMetadata' function from your scraper code
        URL = f'https://api.spotifydown.com/metadata/playlist/{Playlist_ID}'
        headers = {
            'authority': 'api.spotifydown.com',
            'method': 'GET',
            'path': f'/metadata/playlist/{Playlist_ID}',
            'scheme': 'https',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        }
        meta_data = self.session.get(headers=headers, url=URL)
        if meta_data.status_code == 200:
            return meta_data.json()
        return None

    def slugify(self,fn):
        validchars = "-_.() '"
        out = ""
        for c in fn:
          if c != ',':
              if str.isalpha(c) or str.isdigit(c) or (c in validchars):
                out += c
              else:
                out += "-"
        return out 

    def errorcatch(self, SONG_ID):
        # The 'errorcatch' function from your scraper code
        headers = {
            'authority': 'api.spotifydown.com',
            'method': 'GET',
            'path': f'/download/{SONG_ID}',
            'scheme': 'https',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        }
        x = self.session.get(headers=headers, url='https://api.spotifydown.com/download/' + SONG_ID)
        if x.status_code == 200:
            return x.json()['link']
        return None

    def scrape_playlist(self, playlist_id, music_folder):
        playlist_metadata = self.get_PlaylistMetadata(playlist_id)        
        if settings.music_folder_use_playlist_name:
            
            music_folder = music_folder + "/" + self.slugify(playlist_metadata['title'] + " ("+playlist_metadata['artists']+")")

        headers = {
            'authority': 'api.spotifydown.com',
            'method': 'GET',
            'path': f'/trackList/playlist/{playlist_id}',
            'scheme': 'https',
            'accept': '*/*',
            'dnt': '1',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        }

        Playlist_Link = f'https://api.spotifydown.com/trackList/playlist/{playlist_id}'
        offset_data = {}
        offset = 0
        offset_data['offset'] = offset

        while offset is not None:
            response = self.session.get(url=Playlist_Link, params=offset_data, headers=headers)
            if response.status_code == 200:
                Tdata = response.json()['trackList']
                page = response.json()['nextOffset']
                for count, song in enumerate(Tdata):
                    self.scrape_track(song, music_folder)
            if page is not None:
                offset_data['offset'] = page
                response = self.session.get(url=Playlist_Link, params=offset_data, headers=headers)
            else:
                break
    
    def make_filename(self, song_metadata):
          return self.slugify(song_metadata['artists']+ ' - ' + song_metadata['album'] + ' - ' + song_metadata['title'] + '.mp3')
                  
    def scrape_track(self, song, music_folder):
        yt_id = self.get_ID(song['id'])
        if yt_id is not None:
            filename = self.make_filename(song)
            self.song_downloading.emit(filename.replace('.mp3',''))
            if settings.skip_existing and os.path.exists(music_folder + "/" + filename):
                print("Skipping:\t" + filename)
                self.skipped_track_count += 1
                self.update_track_counts_ui()
            else:
                print("Downloading:\t" + filename)
                try:
                    data = self.generate_Analyze_id(yt_id['id'])
                    try:
                        DL_ID = data['links']['mp3']['mp3128']['k']
                        DL_DATA = self.generate_Conversion_id(data['vid'], DL_ID)
                        DL_LINK = DL_DATA['dlink']
                    except Exception as NoLinkError:
                        CatchMe = self.errorcatch(song['id'])
                        if CatchMe is not None:
                            DL_LINK = CatchMe
                    if DL_LINK is not None:
                        ## DOWNLOAD
                        link = self.session.get(DL_LINK)

                        # Create Folder for Playlist
                        if not os.path.exists(music_folder):
                            os.makedirs(music_folder)

                        ## Save
                        with open(os.path.join(music_folder, filename), 'wb') as f:
                            f.write(link.content)
                        
                            SONG_META   = song
                            SONG_META['file'] = music_folder + "/" + filename
                            songTag = WritingMetaTags(tags=SONG_META, filename=music_folder + "/" + filename)
                            song_meta_add = songTag.WritingMetaTags()
                
                        #Increment the counter
                        self.downloaded_track_count += 1
                        self.update_track_counts_ui()
                    else:
                        print('[*] No Download Link Found.')
                        self.failed_track_count += 1
                        self.failed_tracks += "\n"+filename
                        self.update_track_counts_ui()
                except Exception as error_status:
                    print('[*] Error Status Code : ', error_status)
                    self.failed_track_count += 1
                    self.failed_tracks += "\n"+filename
                    self.update_track_counts_ui()

        else:
            print('[*] No data found for : ', song)
            self.failed_track_count += 1
            self.failed_tracks += "\n"+filename
            self.update_track_counts_ui()

    def update_track_counts_ui(self):
        self.counts.emit(self.downloaded_track_count, self.skipped_track_count, self.failed_track_count)
        
    
    def is_playlist(self, link):
        try:
            self.get_playlist_id(link)
            return True
        except Exception:
            return False
    
    def get_playlist_id(self, link):
        # # The 'returnSPOT_ID' function from your scraper code
        # return link.split('/')[-1].split('?si')[0]

        # Define the regular expression pattern for the Spotify playlist URL
        pattern = r"https://open\.spotify\.com/playlist/([a-zA-Z0-9]+)\?si=.*"

        # Try to match the pattern in the input text
        match = re.match(pattern, link)

        if not match:
            raise ValueError("Invalid Spotify playlist URL.")
        # Extract the playlist ID from the matched pattern
        extracted_id = match.group(1)

        return extracted_id
      
    def is_track(self, link):
        try:
            self.get_track_id(link)
            return True
        except Exception:
            return False 
             
    def get_track_id(self, link):
        # # The '' function from your scraper code
        # return link.split('/')[-1].split('?si')[0]

        # Define the regular expression pattern for the Spotify playlist URL
        pattern = r"https://open\.spotify\.com/track/([a-zA-Z0-9]+)\?si=.*"

        # Try to match the pattern in the input text
        match = re.match(pattern, link)

        if not match:
            raise ValueError("Invalid Spotify track URL.")
        # Extract the playlist ID from the matched pattern
        extracted_id = match.group(1)

        return extracted_id
        

 # Emit the signal with the updated count

# Scraper Thread
class ScraperThread(QThread):
    progress_update = pyqtSignal(str)

    def __init__(self, playlist_link):
        super().__init__()
        self.link = playlist_link
        self.scraper = MusicScraper()  # Create an instance of MusicScraper

    def run(self):
        music_folder = os.path.join(os.getcwd(), settings.music_folder)
        try:
            if self.scraper.is_playlist(self.link):
                self.progress_update.emit("Scraping ...")
                playlist_id = self.scraper.get_playlist_id(self.link)
                self.scraper.scrape_playlist(playlist_id, music_folder)
                self.progress_update.emit("Scraping completed.")
                if self.scraper.failed_track_count>0:
                    self.scraper.song_downloading.emit("Failed:\n"+self.scraper.failed_tracks)
                    print("Failed:\n"+self.scraper.failed_tracks)
                else:
                    self.scraper.song_downloading.emit("")  
            elif self.scraper.is_track(self.link):
                self.progress_update.emit("Scraping ...")
                trackid_id = self.scraper.get_track_id(self.link)
                self.scraper.scrape_track(self.link, music_folder)
                self.progress_update.emit("Scraping completed.")
            else:
                self.progress_update.emit("invalid link")
                
            
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            self.progress_update.emit(f"{e}")




# Main Window
class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        """MainWindow constructor"""
        super(MainWindow, self).__init__()

        # Main UI code goes here
        # loadUi("Template.ui", self)

        self.setupUi(self)

        self.playlist_link.returnPressed.connect(self.on_returnButton)
        self.close.clicked.connect(self.exitprogram)
        #self.Select_Home.clicked.connect(self.Medium)
        # End main UI code

    # https://open.spotify.com/playlist/37i9dQZF1E36hkEAnydKTA?si=20caa5adfed648d3

    @pyqtSlot()
    def on_returnButton(self):
        playlist_id = self.playlist_link.text()
        try:
            # self.PlaylistMsg.setText('Playlist Code : %s' % playlist_id)

            # Start the scraper in a separate thread
            self.scraper_thread = ScraperThread(playlist_id)
            self.scraper_thread.progress_update.connect(self.update_progress)
            self.scraper_thread.finished.connect(self.thread_finished)  # Connect the finished signal
            self.scraper_thread.scraper.song_downloading.connect(self.update_song_downloading)  # Connect the signal
            # Connect the count_updated signal to the update_counter slot
            self.scraper_thread.scraper.counts.connect(self.update_counters)

            self.scraper_thread.start()

        except ValueError as e:
            print(e)
            print(traceback.format_exc())
            self.statusMsg.setText(str(e))

    def thread_finished(self):
        self.scraper_thread.deleteLater()  # Clean up the thread properly

    def update_progress(self, message):
        self.status_msg.setText(message)

    @pyqtSlot(str)
    def update_song_downloading(self, song_name):
        self.song_name.setText(song_name)

    @pyqtSlot(int, int, int)
    def update_counters(self, downloaded, skipped, failed):
        if skipped != 0 or failed != 0:
            self.counter_label.setText("Downloaded:" + str(downloaded)  + " skipped: "+str(skipped) + " failed:" + str(failed))
        else:
            self.counter_label.setText("Downloaded:" + str(downloaded))
    

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

    def Medium(self):
        webbrowser.open('https://surenjanath.medium.com/')


# Main
if __name__ == '__main__':
    app = QApplication(sys.argv)
    Screen = MainWindow()
    Screen.setFixedHeight(1390)
    Screen.setFixedWidth(1320)
    Screen.setWindowFlags(Qt.FramelessWindowHint)
    Screen.setAttribute(Qt.WA_TranslucentBackground)
    Screen.show()
    sys.exit(app.exec())


