from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3

import sys
import os
import platform
import string
import requests
import re
import webbrowser
import unicodedata
import traceback
from unidecode import unidecode


class SpotifyScraper(QObject):
    song_downloading = pyqtSignal(str)
    counts = pyqtSignal(str, int, int, int, int)
    playlist_name = pyqtSignal(str)
    details_update = pyqtSignal(str)

    def __init__(self):
        super(SpotifyScraper, self).__init__()
        self.playlist_track_count = 0
        self.downloaded_track_count = 0
        self.failed_track_count = 0
        self.skipped_track_count = 0
        self.failed_tracks = []
        self.playlist_tracks = []
        self.directory_tracks = []
        
        self.session = requests.Session()

    def get_ID(self, id):
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
    
    def scrape_item(self, link, music_folder):
        try:
            if self.is_playlist(link):
                self.scrape_playlist(link, music_folder)                    
            elif self.is_track(link):
                self.scrape_single_track(link, music_folder) 
            else:
                self.details_update.emit("Invalid link")
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            self.details_update.emit(f"{e}")
    
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
   
            
    def scrape_playlist(self, link, music_folder):
        self.details_update.emit("")
        self.song_downloading.emit("")
        
        playlist_id = self.get_item_id(link, kind="playlist")
        playlist_metadata = self.get_PlaylistMetadata(playlist_id)
        self.playlist_name.emit("Playlist: " + playlist_metadata['title'] + " ("+playlist_metadata['artists']+")")
        
        if not playlist_metadata["success"]:
            self.song_downloading.emit("not a valid playlist, Spotify api return error message: " + playlist_metadata["message"])
            return
            
        music_folder = music_folder + "/" + self.clean_filename(playlist_metadata['title'] + " ("+playlist_metadata['artists']+")")
        
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
        self.update_playlist_scrape_details()
        
    def update_playlist_scrape_details(self):
        details = ""   
                  
        if len(self.failed_tracks)>0:
            details += "\nFailed track downloads:"
            for track in self.failed_tracks:
                details += "\n" + track
            details += "\n"
        
        in_folder_not_in_playlist = []
        for track in self.directory_tracks:
            if track not in self.playlist_tracks and track != ".DS_Store" and not track.startswith(".syncthing.") and not track.endswith(".stem.m4a"):
                in_folder_not_in_playlist.append(track)
        if len(in_folder_not_in_playlist):
            details += "\nTracks in folder but not in playlist:"
            for track in in_folder_not_in_playlist:
                details += "\n" + track
            details += "\n"
                
        in_playlist_not_in_folder = []
        for track in self.playlist_tracks:
            if track not in self.directory_tracks:
                 in_playlist_not_in_folder.append(track)
        if len(in_playlist_not_in_folder):
            details += "\nTracks in playlist but not in folder:"
            for track in in_playlist_not_in_folder:
                details += "\n" + track
            details += "\n"
        
        if len(in_playlist_not_in_folder)==0 and len(in_folder_not_in_playlist)==0 and len(self.failed_tracks)==0:
            details += "Hurray ! All downloads completed sucessfully!\n\n\n\n"
            
        self.details_update.emit(details)
        print(details)
        
    
    def clean_filename(self,fn):
        validchars = "-_.() '',"
        out = ""
        for c in fn:
          if str.isalpha(c) or str.isdigit(c) or (c in validchars):
            out += c
          else:
            out += "-"
        return unidecode(out)
        
    
    def make_filename(self, song):
        return self.clean_filename(song['artists']+ ' - ' + song['album'] + ' - ' + song['title'] + '.mp3')

        
    def scrape_track(self, song, music_folder):
        yt_id = self.get_ID(song['id'])
        filename = self.make_filename(song)
        self.playlist_tracks.append(filename)
        if yt_id is not None:
            # Create Folder for Playlist
            if not os.path.exists(music_folder):
                os.makedirs(music_folder)
                
            self.song_downloading.emit(song['artists']+ ' - ' + song['album'] + ' - ' + song['title'])
            full_filename = music_folder + "/" + filename
            if os.path.exists(full_filename):
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
                        with open(full_filename, 'wb') as f:
                            f.write(link.content)
                        
                        self.set_download_and_set_cover(tags=song, full_filename=full_filename)
                
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
    
    def set_download_and_set_cover(self, tags, full_filename):
        if tags['cover'] is None:
            pass
        else:
            
            try:
                response = requests.get(tags['cover']+"?size=1", stream=True)
                if response.status_code == 200 :
                    audio = ID3(full_filename)
                    audio['APIC'] = APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc=u'Cover',
                        data=response.content
                    )
                    audio.save()
                else:
                    print(full_filename + " cover http error : " + str(response.status_code))
            except Exception as e:
                print(f"Error adding cover: {e}")
                
    def scrape_single_track(self,link, music_folder):
        self.details_update.emit("")
        self.song_downloading.emit("")
        self.playlist_name.emit("Single track")
        self.playlist_track_count = 1
        self.update_track_counts_ui("Downloading")
        trackid_id = self.get_item_id(link, kind="track")
        song = self.get_track_metadata(trackid_id)
        self.scrape_track(song, music_folder)
        self.update_track_counts_ui("Done")
        self.update_track_scrape_details()
    
    
    def update_track_scrape_details(self):
        details = ""
        
        if len(self.failed_tracks)>0:
            details += "\nFailed track downloads:"
            for track in self.failed_tracks:
                details += "\n" + track
            details += "\n"
        
        if len(self.failed_tracks)==0:
            details += "Hurray ! Download completed sucessfully!\n\n\n\n"
            
        self.details_update.emit(details)
        print(details)  


    def update_track_counts_ui(self, message):
        self.counts.emit(message, self.playlist_track_count, self.downloaded_track_count, self.skipped_track_count, self.failed_track_count)
        
    
    def is_playlist(self, link):
        try:
            self.get_item_id(link, kind="playlist")
            return True
        except Exception:
            return False
    
    
    def is_track(self, link):
        try:
            self.get_item_id(link, kind="track")
            return True
        except Exception:
            return False
    
    
    def get_item_id(self, link, kind="playlist"):
        # # The 'returnSPOT_ID' function from your scraper code
        # return link.split('/')[-1].split('?si')[0]
        pattern = r"https://open\.spotify\.com/"+kind+"/([a-zA-Z0-9]+)\?si=.*"
        match = re.match(pattern, link)
        if not match:
            raise ValueError("Invalid Spotify "+kind+" URL.")
        extracted_id = match.group(1)
        return extracted_id
      


      





