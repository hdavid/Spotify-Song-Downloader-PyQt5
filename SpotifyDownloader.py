#!/usr/bin/python3
# Main
# if __name__ == '__main__':from PyQt5.uic import loadUi

try:
    from PyQt5.QtWidgets import QMainWindow, QApplication
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
    from PyQt5.QtGui import  QCursor
    from Template import Ui_MainWindow

    import sys
    import os
    import platform
    import string
    import requests
    import re
    import webbrowser
    import unicodedata
    import traceback

    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import APIC, ID3
except Exception as e:
    print ("dependencies are not installed")
    print("run 'pip3 install -r requirements.txt' to fix")

    
class Settings:
    def __init__(self):
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            if platform.system() == "Windows":
                self.music_folder = "."
            else:
                if getattr(sys, 'frozen', False):
                    self.music_folder = os.path.dirname(sys.executable) + "/../../.."
                elif __file__:
                    self.music_folder = os.path.dirname(__file__) + "/../../.."
                    #self.music_folder = "./../../.."
        else:
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
    counts = pyqtSignal(str, int, int, int, int)
    playlist_name = pyqtSignal(str)

    def __init__(self):
        super(MusicScraper, self).__init__()
        self.playlist_track_count = 0
        self.downloaded_track_count = 0
        self.failed_track_count = 0
        self.skipped_track_count = 0
        self.failed_tracks = []
        self.playlist_tracks = []
        self.directory_tracks = []
        
        self.session = requests.Session()

    def get_ID(self, id):
        # The 'get_ID' function from your scraper code
        LINK = f'https://api.spotifydown.com/getId/{id}'
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

    def generate_Analyze_id(self, id):
        # The 'generate_Analyze_id' function from your scraper code
        DL = 'https://corsproxy.io/?https://www.y2mate.com/mates/analyzeV2/ajax'
        data = {
            'k_query': f'https://www.youtube.com/watch?v={id}',
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

    def get_track_metadata(self, track_id):
        # The 'get_PlaylistMetadata' function from your scraper code
        URL = f'https://api.spotifydown.com/metadata/track/{track_id}'
        headers = {
            'authority': 'api.spotifydown.com',
            'method': 'GET',
            'path': f'/metadata/track/{track_id}',
            'scheme': 'https',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        }
        meta_data = self.session.get(headers=headers, url=URL)
        if meta_data.status_code == 200:
            return meta_data.json()
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
        validchars = "-_.() '',"
        out = ""
        for c in fn:
          if str.isalpha(c) or str.isdigit(c) or (c in validchars):
            out += c
          else:
            out += "-"
        return out 

    def errorcatch(self, song_id):
        # The 'errorcatch' function from your scraper code
        headers = {
            'authority': 'api.spotifydown.com',
            'method': 'GET',
            'path': f'/download/{song_id}',
            'scheme': 'https',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        }
        x = self.session.get(headers=headers, url='https://api.spotifydown.com/download/' + song_id)
        if x.status_code == 200:
            return x.json()['link']
        return None

    def get_playlist_size(self, playlist_id):
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

        playlist_link = f'https://api.spotifydown.com/trackList/playlist/{playlist_id}'
        offset_data = {}
        offset = 0
        offset_data['offset'] = offset
        tracks = 0
        while offset is not None:
            response = self.session.get(url=playlist_link, params=offset_data, headers=headers)
            if response.status_code == 200:
                Tdata = response.json()['trackList']
                page = response.json()['nextOffset']
                tracks += len(Tdata)
            if page is not None:
                offset_data['offset'] = page
                response = self.session.get(url=playlist_link, params=offset_data, headers=headers)
            else:
                break
        
        return tracks

    def scrape_playlist(self, playlist_id, music_folder):
        playlist_metadata = self.get_PlaylistMetadata(playlist_id)
        if not playlist_metadata["success"]:
            self.song_downloading.emit("not a valid playlist, Spotify api return error message: " + playlist_metadata["message"])
            return
            
        if settings.music_folder_use_playlist_name: 
            music_folder = music_folder + "/" + self.slugify(playlist_metadata['title'] + " ("+playlist_metadata['artists']+")")

        
        self.playlist_name.emit(playlist_metadata['title'] + " ("+playlist_metadata['artists']+")")
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

        playlist_Link = f'https://api.spotifydown.com/trackList/playlist/{playlist_id}'
        offset_data = {}
        offset = 0
        offset_data['offset'] = offset
        self.playlist_track_count = self.get_playlist_size(playlist_id)
        self.update_track_counts_ui("Downloading")
        while offset is not None:
            response = self.session.get(url=playlist_Link, params=offset_data, headers=headers)
            if response.status_code == 200:
                Tdata = response.json()['trackList']
                page = response.json()['nextOffset']
                for count, song in enumerate(Tdata):
                    self.scrape_track(song, music_folder)
            if page is not None:
                offset_data['offset'] = page
                response = self.session.get(url=playlist_Link, params=offset_data, headers=headers)
            else:
                break
        self.song_downloading.emit("")
        self.directory_tracks = os.listdir(music_folder)
        self.update_track_counts_ui("Done")
    
    def make_filename(self, song):
          return self.slugify(song['artists']+ ' - ' + song['album'] + ' - ' + song['title'] + '.mp3')
                  
    def scrape_track(self, song, music_folder):
        yt_id = self.get_ID(song['id'])
        filename = self.make_filename(song)
        self.playlist_tracks.append(filename)
        if yt_id is not None:
            # Create Folder for Playlist
            if not os.path.exists(music_folder):
                os.makedirs(music_folder)
                
            self.song_downloading.emit(song['artists']+ ' - ' + song['album'] + ' - ' + song['title'])
            if settings.skip_existing and os.path.exists(music_folder + "/" + filename):
                self.skipped_track_count += 1
                self.update_track_counts_ui("Downloading")
            else:
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

                        ## Save
                        with open(os.path.join(music_folder, filename), 'wb') as f:
                            f.write(link.content)
                            SONG_META   = song
                            SONG_META['file'] = music_folder + "/" + filename
                            songTag = WritingMetaTags(tags=SONG_META, filename=music_folder + "/" + filename)
                            song_meta_add = songTag.WritingMetaTags()
                
                        #Increment the counter
                        self.downloaded_track_count += 1
                        self.update_track_counts_ui("Downloading")
                    else:
                        print('[*] No Download Link Found for '+filename)
                        self.failed_track_count += 1
                        self.failed_tracks.append(filename + ": No Download Link Found")
                        self.update_track_counts_ui("Error")
                except Exception as error_status:
                    print('[*] Error Status Code : '+ str(error_status) +  filename)
                    self.failed_track_count += 1
                    self.failed_tracks.append(filename + ": Error Status Code : " + str(error_status))
                    self.update_track_counts_ui("Error")

        else:
            print('[*] No data found for : ', song)
            self.failed_track_count += 1
            self.failed_tracks.append(filename + ": No data found")
            self.update_track_counts_ui("Error")
        

    def update_track_counts_ui(self, message):
        self.counts.emit(message, self.playlist_track_count, self.downloaded_track_count, self.skipped_track_count, self.failed_track_count)
        
    
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
    details_update = pyqtSignal(str)

    def __init__(self, playlist_link):
        super().__init__()
        self.link = playlist_link
        self.scraper = MusicScraper()  # Create an instance of MusicScraper

    def run(self):
        music_folder = os.path.join(os.getcwd(), settings.music_folder)
        try:
            if self.scraper.is_playlist(self.link):
                self.details_update.emit("")
                playlist_id = self.scraper.get_playlist_id(self.link)
                self.scraper.scrape_playlist(playlist_id, music_folder)
    
                details = ""   
                          
                if len(self.scraper.failed_tracks)>0:
                    details += "\nFailed track downloads:"
                    for track in self.scraper.failed_tracks:
                        details += "\n" + track
                    details += "\n"
                
                in_folder_not_in_playlist = []
                for track in self.scraper.directory_tracks:
                    if track not in self.scraper.playlist_tracks and track != ".DS_Store":
                        in_folder_not_in_playlist.append(track)
                if len(in_folder_not_in_playlist):
                    details += "\nTracks in folder but not in playlist:"
                    for track in in_folder_not_in_playlist:
                        details += "\n" + track
                    details += "\n"
                        
                in_playlist_not_in_folder = []
                for track in self.scraper.playlist_tracks:
                    if track not in self.scraper.directory_tracks:
                         in_playlist_not_in_folder.append(track)
                if len(in_playlist_not_in_folder):
                    details += "\nTracks in playlist but not in folder:"
                    for track in in_playlist_not_in_folder:
                        details += "\n" + track
                    details += "\n"
                    
                self.details_update.emit(details)
                        
            elif self.scraper.is_track(self.link):
                self.details_update.emit("")
                self.scraper.song_downloading.emit("")
                self.scraper.playlist_name.emit("Single track")
                self.scraper.playlist_track_count = 1
                self.scraper.update_track_counts_ui("Downloading")
                trackid_id = self.scraper.get_track_id(self.link)
                song = self.scraper.get_track_metadata(trackid_id)
                self.scraper.scrape_track(song, music_folder)
                self.scraper.update_track_counts_ui("Done")
                
            else:
                self.details_update.emit("invalid link")
                
            
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            self.details_update.emit(f"{e}")




# Main Window
class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        """MainWindow constructor"""
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
            self.scraper_thread.details_update.connect(self.details_update)
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
        self.playlist_name.setText("Playlist: " + playlist_name)

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


